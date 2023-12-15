import rename.file_renamer as file_renamer
import split.pdf_splitter as pdf_splitter
import aws.s3_utils as s3_utils

S3_INPUT_DIR = "input-single-pdfs/"
S3_OUTPUT_DIR = "renamed-single-pdfs/"
S3_BUCKET_NAME = "feefs-pdfs"

if __name__ == "__main__":
    s3_client = s3_utils.AWSClientS3Conn(bucket=S3_BUCKET_NAME)
    pdf_splitter.split_pdfs_in_dir("/Users/maxramer/Desktop/file-renamer/input_all", "/Users/maxramer/Desktop/file-renamer/output_all")
    s3_client.upload_local_files_to_s3("/Users/maxramer/Desktop/file-renamer/output_all", S3_INPUT_DIR)
    # file_renamer.begin(s3_client=s3_client, s3_input_dir=S3_INPUT_DIR)