import rename.file_renamer as file_renamer
import split.pdf_splitter as pdf_splitter
import src.aws.aws_conn as aws_conn
import os

S3_BUCKET_NAME = "feefs-pdfs"

LOCAL_MULTI_PDFS_DIR = "/Users/maxramer/Desktop/file-renamer/multi-pdfs"
LOCAL_SINGLE_PDFS_DIR = "/Users/maxramer/Desktop/file-renamer/input-single-pdfs"
LOCAL_RENAMED_PDFS_DIR = "/Users/maxramer/Desktop/file-renamer/renamed-single-pdfs"

S3_MULTI_PDFS_DIR = "multi-pdfs"
S3_SINGLE_PDFS_DIR = "input-single-pdfs"
S3_RENAMED_PDFS_DIR = "renamed-single-pdfs"

def create_dir_if_necessary(dir):
    isExist = os.path.exists(dir)
    if not isExist:
        print(dir + " does not exist!")
        os.makedirs(dir)

if __name__ == "__main__":
    create_dir_if_necessary(LOCAL_MULTI_PDFS_DIR)
    create_dir_if_necessary(LOCAL_SINGLE_PDFS_DIR)
    create_dir_if_necessary(LOCAL_RENAMED_PDFS_DIR)

    s3_client = aws_conn.AWSClientS3Conn(bucket=S3_BUCKET_NAME)
    s3_client.download_all_files_from_s3_dir(LOCAL_MULTI_PDFS_DIR, S3_MULTI_PDFS_DIR)

    print("Splitting pdfs...")
    pdf_splitter.split_pdfs(input_dir=LOCAL_MULTI_PDFS_DIR, output_dir=LOCAL_SINGLE_PDFS_DIR)
    
    print("Uploading pdfs to S3...")
    s3_client.upload_local_files_to_s3(local_dir=LOCAL_SINGLE_PDFS_DIR, s3_dir=S3_SINGLE_PDFS_DIR)
    print("Successfully uploaded pdfs to S3!")
    
    print("Renaming S3 files...")
    file_renamer.begin(s3_client=s3_client, s3_input_dir=S3_SINGLE_PDFS_DIR, s3_output_dir=S3_RENAMED_PDFS_DIR)
    print("Downloading pdfs...")
    s3_client.download_all_files_from_s3_dir(local_dir=LOCAL_RENAMED_PDFS_DIR, s3_dir=S3_RENAMED_PDFS_DIR)
    
    print("Deleting all S3 files...")
    s3_client.delete_all_files_in_s3_dir(S3_MULTI_PDFS_DIR)
    s3_client.delete_all_files_in_s3_dir(S3_SINGLE_PDFS_DIR)
    s3_client.delete_all_files_in_s3_dir(S3_RENAMED_PDFS_DIR)
    print("Complete!")