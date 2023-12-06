import boto3
import time
import sys
import logging
from multiprocessing import Pool
import threading
from tqdm import tqdm

S3 = "s3"
S3_BUCKET_NAME = "feefs-pdfs"
REGION = "us-east-1"
CLIENT = boto3.client('textract', region_name=REGION)

INPUT_PDFS_DIR = "input-single-pdfs/"
OUTPUT_PDFS_DIR = "renamed-single-pdfs/"

s3_client = boto3.client(S3)
s3_resource = boto3.resource(S3)

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


class SafeProgressBar:
    def __init__(self, total):
        self.pbar = tqdm(total=total, desc="Renaming PDFs")
        self.total = total
        self.lock = threading.Lock()
        self.pbar.update(0)

    def update(self):
        with self.lock:
            self.pbar.update(1)

    def close(self):
        self.pbar.close()
    
    def update_total(self, total):
        self.total = total

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
    # logging.info("Resultset page received: {}".format(len(pages)))
    next_token = None
    if 'NextToken' in response:
        next_token = response['NextToken']

    while next_token:
        time.sleep(2)
        response = CLIENT.\
            get_document_text_detection(JobId=job_id, NextToken=next_token)
        pages.append(response)
        # logging.info("Resultset page received: {}".format(len(pages)))
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
    print("Renamed from " + old_key + " to " + new_key)

# def extract_date(input_string):
#     start_index = None
#     end_index = None

#     for i, char in enumerate(input_string):
#         if char.isdigit():
#             if start_index is None:
#                 start_index = i
#             end_index = i

#     if start_index is not None and end_index is not None:
#         result = input_string[start_index:end_index + 1]
#         return result
#     else:
#         return None
def extract_date(input_string):
    first_slash_index = input_string.find('/')
    
    if first_slash_index != -1:
        second_slash_index = input_string.find('/', first_slash_index + 1)
        
        if second_slash_index != -1:
            start_index = max(0, first_slash_index - 2)
            end_index = min(len(input_string), second_slash_index + 2)
            result = input_string[start_index:end_index]
            return result

    return None

# def process_file(document_name, pbar):
def process_file(document_name):
    # logging.info("tasks assigned!")
    job_id = start_job(document_name)
    # logging.info("Started job for pdf: {}".format(document_name))
    if is_job_complete(job_id):
        response = get_job_results(job_id)

    new_file_name = OUTPUT_PDFS_DIR
    found_site_id = False
    found_signature = False
    found_date = False
    found_teen = False

    # Print detected text
    date = ""
    for result_page in response:
        for item in result_page["Blocks"]:
            if item["BlockType"] == "LINE":
                curr_line = item["Text"]
                # print(curr_line)
                # file_text_dict.append(curr_line)
                if found_site_id == True:
                    site_id = "Site " + curr_line
                    if "SNL" in site_id:
                        site_id = "Site " + site_id.split(' ')[-1] + " SNL"
                    if found_teen:
                        site_id = "Teen " + site_id
                        found_teen = False
                    new_file_name += site_id
                    found_site_id = False
                if found_signature == True:
                    if "/" in curr_line:
                        date = extract_date(curr_line)
                        formatted_date = date.replace('/', '.')
                        new_file_name += " " + formatted_date
                        found_signature = False
                if found_date == True and date == "":
                    if curr_line.isalpha() == False and "/" in curr_line:
                        date = curr_line.replace('/', '.')
                    elif "/" in curr_line:
                        date = extract_date(curr_line)
                        formatted_date = date.replace('/', '.')
                        new_file_name += " " + formatted_date
                        found_date = False
                    else:
                        print("No date found for string: " + curr_line)
                elif date == "":
                    found_date = False
                if curr_line == "Site ID:":
                    found_site_id = True
                if curr_line == "Date:":
                    found_date = True
                if "Teen Program" in curr_line:
                    found_teen = True
                if "Signature:" in curr_line:
                    found_signature = True
    new_file_name += ".pdf"
    rename_s3_file(document_name, new_file_name)
    # print(new_file_name)
    # pbar.update()

if __name__ == "__main__":
    my_bucket = s3_resource.Bucket(S3_BUCKET_NAME)
    logging.info("Starting...")

    single_pdfs = []
    for object_summary in my_bucket.objects.filter(Prefix=INPUT_PDFS_DIR):
        if ".pdf" in object_summary.key:
            single_pdfs.append(object_summary.key)

    # total_tasks = len(single_pdfs)
    # pbar = SafeProgressBar(total_tasks)

    with Pool(20) as pool:
        result = pool.map_async(process_file, single_pdfs)
        for result in result.get():
            pass
            # print(f'Got result: {result}', flush=True)
        # async_result = [pool.apply_async(process_file, args=(pdf, pbar)) for pdf in single_pdfs]
        # pool.map(process_file, single_pdfs, pbar)

    # for pdf in single_pdfs:
    #     if (len(threads) < 10):
    #         thread = threading.Thread(target=process_file, args=(pdf,pbar))
    #         threads.append(thread)
    #         thread.start()
    #     else:
    #         # Wait until thread becomes available
    #         while (len(threads) >= 10):
    #             time.sleep(1)
    #             pass

    # Wait for all threads to finish
    # for thread in threads:
    #     thread.join()

    # Close the loading bar
    # pbar.close()    
