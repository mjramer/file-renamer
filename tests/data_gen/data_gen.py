import boto3
import time
import sys
import logging
import os
from botocore.exceptions import ClientError


S3 = "s3"
S3_BUCKET_NAME = "feefs-pdfs"
REGION = "us-east-1"
CLIENT = boto3.client('textract', region_name=REGION)

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

    while(status == "IN_PROGRESS"):
        time.sleep(1)
        response = CLIENT.get_document_text_detection(JobId=job_id)
        status = response["JobStatus"]

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

def process_file(document_name):
    job_id = start_job(document_name)
    if is_job_complete(job_id):
        response = get_job_results(job_id)

    # Print detected text
    data = ""
    for result_page in response:
        for item in result_page["Blocks"]:
            if item["BlockType"] == "LINE":
                data += item["Text"] + "\n"    
    return data 

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True      

def delete_file(file_name, bucket):
    try:
        response = s3_client.delete_object(Bucket=bucket, Key=file_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True  

if __name__ == "__main__":
    for raw_pdf in os.listdir("raw_data/"):
        upload_file("raw_data/" + raw_pdf, S3_BUCKET_NAME)
        with open("data/" + raw_pdf.replace(".pdf", ".txt"), "w") as data:
            string = process_file(raw_pdf)
            data.write(string)
        delete_file(raw_pdf, S3_BUCKET_NAME)
        logging.info("Generated txt for " + raw_pdf)