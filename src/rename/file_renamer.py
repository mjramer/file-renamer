import boto3
import time
import sys
import logging
from multiprocessing import Pool
import re
import string
import random

S3 = "s3"
S3_BUCKET_NAME = "feefs-pdfs"
REGION = "us-east-1"
CLIENT = boto3.client('textract', region_name=REGION)

INPUT_PDFS_DIR = "input-single-pdfs/"
OUTPUT_PDFS_DIR = "renamed-single-pdfs/"

DATE_REGEX_MD = "\d{1}/\d{1}/\d{2}"
DATE_REGEX_MDD = "\d{1}/\d{2}/\d{2}"
DATE_REGEX_MMD = "\d{2}/\d{1}/\d{2}"
DATE_REGEX_MMDD = "\d{2}/\d{2}/\d{2}"


s3_client = boto3.client(S3)
s3_resource = boto3.resource(S3)

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


def start_job(object_name):
    response = None
    response = CLIENT.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': S3_BUCKET_NAME,
                'Name': object_name
            }})

    return response["JobId"]


def is_job_complete(job_id):
    time.sleep(1)
    response = CLIENT.get_document_text_detection(JobId=job_id)
    status = response["JobStatus"]
    # logging.info("Job status: {}".format(status))

    while(status == "IN_PROGRESS"):
        time.sleep(1)
        response = CLIENT.get_document_text_detection(JobId=job_id)
        status = response["JobStatus"]
        # logging.info("Job status: {}".format(status))

    return status


def get_job_results(job_id):
    pages = []
    time.sleep(1)
    response = CLIENT.get_document_text_detection(JobId=job_id)
    pages.append(response)
    next_token = None
    if 'NextToken' in response:
        next_token = response['NextToken']

    while next_token:
        time.sleep(2)
        response = CLIENT.\
            get_document_text_detection(JobId=job_id, NextToken=next_token)
        pages.append(response)
        next_token = None
        if 'NextToken' in response:
            next_token = response['NextToken']

    return pages

def rename_s3_file(old_key, new_key):
    # Copy the object with the new key
    copy_source = {'Bucket': S3_BUCKET_NAME, 'Key': old_key}
    s3_client.copy_object(CopySource=copy_source, Bucket=S3_BUCKET_NAME, Key=new_key)

    # Delete the old object
    # s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=old_key)
    logging.info("Renamed from " + old_key + " to " + new_key)

def extract_date_single_dig_month(input_string):
    first_slash_index = input_string.find('/')
    
    if first_slash_index != -1:
        second_slash_index = input_string.find('/', first_slash_index + 1)
        
        if second_slash_index != -1:
            start_index = max(0, first_slash_index - 1)
            end_index = min(len(input_string), second_slash_index + 3)
            result = input_string[start_index:end_index]
            return result

    return None

def extract_date_double_dig_month(input_string):
    first_slash_index = input_string.find('/')
    
    if first_slash_index != -1:
        second_slash_index = input_string.find('/', first_slash_index + 1)
        
        if second_slash_index != -1:
            start_index = max(0, first_slash_index - 2)
            end_index = min(len(input_string), second_slash_index + 3)
            result = input_string[start_index:end_index]
            return result

    return None

def extract_text(s3_file):
    job_id = start_job(s3_file)
    if is_job_complete(job_id):
        response = get_job_results(job_id)

    text = ""
    for result_page in response:
        for item in result_page["Blocks"]:
            if item["BlockType"] == "LINE":
                text += item["Text"]
    return text
    

def generate_file_name(text):
    new_file_name = OUTPUT_PDFS_DIR
    found_site_id = False
    found_date = False
    found_teen = False

    site_id = ""
    date = ""
    for curr_line in text.splitlines():
        if found_site_id == True:
            if any(map(str.isdigit, curr_line)):
                site_id = "Site " + curr_line
                if "SNL" in site_id:
                    site_id = "Site " + site_id.split(' ')[-1] + " SNL"
                if found_teen:
                    site_id = "Teen " + site_id
                    found_teen = False
            else:
                id = ''.join(random.choices(string.ascii_lowercase, k=5))
                site_id = "no-site-id-found-" + id
                logging.warning("No site ID found! Is the file missing a site ID number?")
            new_file_name += site_id
            found_site_id = False
        if re.match(DATE_REGEX_MD, curr_line) or \
           re.match(DATE_REGEX_MDD, curr_line):
            date = extract_date_single_dig_month(curr_line)
            new_file_name += " " + date.replace("/", ".")
            found_date = True
        elif re.match(DATE_REGEX_MMD, curr_line) or \
           re.match(DATE_REGEX_MMDD, curr_line):
            date = extract_date_double_dig_month(curr_line)
            new_file_name += " " + date.replace("/", ".")
            found_date = True
        if curr_line == "Site ID:":
            found_site_id = True
        if "Teen Program" in curr_line:
            found_teen = True
    if (found_date == False):
        id = ''.join(random.choices(string.ascii_lowercase, k=5))
        new_file_name = "no-date-found-" + id
        logging.warning("No date found! Is the file missing a date?")
    new_file_name += ".pdf"
    return new_file_name

def rename_file(file_name):
    text = extract_text(file_name)
    new_file_name = generate_file_name(text)
    rename_s3_file(file_name, new_file_name)


if __name__ == "__main__":
    my_bucket = s3_resource.Bucket(S3_BUCKET_NAME)
    logging.info("Starting...")

    single_pdfs = []
    for object_summary in my_bucket.objects.filter(Prefix=INPUT_PDFS_DIR):
        if ".pdf" in object_summary.key:
            single_pdfs.append(object_summary.key)

    with Pool(20) as pool:
        result = pool.map_async(rename_file, single_pdfs)
        for result in result.get():
            pass 
