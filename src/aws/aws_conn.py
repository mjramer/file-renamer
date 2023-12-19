import boto3
import time
import logging
import os

S3 = "s3"

class AWSClientS3Conn:
    def __init__(self, bucket):
        self.bucket = bucket
        self.client = boto3.client(S3)
        self.resource = boto3.resource(S3)
    
    def rename_s3_file(self, old_key, new_key, delete_on):
        # Copy the object with the new key
        copy_source = {'Bucket': self.bucket, 'Key': old_key}
        self.client.copy_object(CopySource=copy_source, Bucket=self.bucket, Key=new_key)

        # Delete the old object
        if delete_on:
            self.client.delete_object(Bucket=self.bucket, Key=old_key)
        logging.info("Renamed from " + old_key + " to " + new_key)

    def get_files_from_s3_dir(self, dir):
        my_bucket = self.resource.Bucket(self.bucket)

        files = []
        for object_summary in my_bucket.objects.filter(Prefix=dir):
            full_path_file = object_summary.key
            if ".pdf" in full_path_file:
                file = os.path.split(full_path_file)[-1]
                files.append(file)
        return files

    def upload_local_files_to_s3(self, local_dir, s3_dir):
        for single_pdf in os.listdir(local_dir):
            if ".pdf" in single_pdf:
                try:
                    full_local_path = os.path.join(local_dir, single_pdf)
                    full_s3_path = os.path.join(s3_dir, single_pdf)
                    self.client.upload_file(full_local_path, self.bucket, full_s3_path)
                except FileNotFoundError:
                    print("The file was not found")
    
    def download_all_files_from_s3_dir(self, local_dir, s3_dir):
        files = self.get_files_from_s3_dir(s3_dir)
        for file in files:
            full_path_file = os.path.join(local_dir, file)
            with open(full_path_file, 'wb') as f:
                self.client.download_fileobj(self.bucket, os.path.join(s3_dir, file), f)

class AWSClientTextractConn:
    def __init__(self, region, bucket):
        self.region = region
        self.bucket = bucket
        self.client = boto3.client('textract', region_name=region)

    def start_job(self, s3_file_name):
        response = None
        response = self.client.start_document_text_detection(
            DocumentLocation={
                'S3Object': {
                    'Bucket': self.bucket,
                    'Name': s3_file_name
                }})

        return response["JobId"]


    def is_job_complete(self, job_id):
        time.sleep(1)
        response = self.client.get_document_text_detection(JobId=job_id)
        status = response["JobStatus"]
        # logging.info("Job status: {}".format(status))

        while(status == "IN_PROGRESS"):
            time.sleep(1)
            response = self.client.get_document_text_detection(JobId=job_id)
            status = response["JobStatus"]
            # logging.info("Job status: {}".format(status))

        return status


    def get_job_results(self, job_id):
        pages = []
        time.sleep(1)
        response = self.client.get_document_text_detection(JobId=job_id)
        pages.append(response)
        next_token = None
        if 'NextToken' in response:
            next_token = response['NextToken']

        while next_token:
            time.sleep(2)
            response = self.client.\
                get_document_text_detection(JobId=job_id, NextToken=next_token)
            pages.append(response)
            next_token = None
            if 'NextToken' in response:
                next_token = response['NextToken']

        return pages

    def extract_text(self, s3_file):
        # logging.info("Renaming " + s3_file)
        job_id = self.start_job(s3_file)
        if self.is_job_complete(job_id):
            response = self.get_job_results(job_id)

        text = ""
        for result_page in response:
            for item in result_page["Blocks"]:
                if item["BlockType"] == "LINE":
                    text += item["Text"] + "\n"
        return text
