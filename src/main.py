import rename.file_renamer as file_renamer
import split.pdf_splitter as pdf_splitter
import src.aws.aws_conn as aws_conn

S3_INPUT_DIR = "input-single-pdfs/"
S3_OUTPUT_DIR = "renamed-single-pdfs/"
S3_BUCKET_NAME = "feefs-pdfs"

if __name__ == "__main__":
    s3_client = aws_conn.AWSClientS3Conn(bucket=S3_BUCKET_NAME)

    print("Splitting pdfs...")
    pdf_splitter.split_pdfs_in_dir(s3_client, "/Users/maxramer/Desktop/file-renamer", "/Users/maxramer/Desktop/file-renamer/output_all")
    
    print("Uploading pdfs to S3...")
    s3_client.upload_local_files_to_s3("/Users/maxramer/Desktop/file-renamer/output_all", S3_INPUT_DIR)
    print("Successfully uploaded pdfs to S3!")
    
    print("Renaming S3 files...")
    file_renamer.begin(s3_client=s3_client, s3_input_dir=S3_INPUT_DIR, s3_output_dir=S3_OUTPUT_DIR)
    print("Complete!")
