import rename.file_renamer as file_renamer
import split.pdf_splitter as pdf_splitter
import src.aws.aws_conn as aws_conn

S3_BUCKET_NAME = "feefs-pdfs"

S3_MULTI_PDFS_DIR="multi-pdfs"
S3_SINGLE_PDFS_DIR = "input-single-pdfs"
S3_RENAMED_PDFS_DIR = "renamed-single-pdfs"

if __name__ == "__main__":
    s3_client = aws_conn.AWSClientS3Conn(bucket=S3_BUCKET_NAME)

    print("Downloading pdfs from S3...")
    s3_client.download_all_files_from_s3_dir("/Users/maxramer/Desktop/file-renamer/multi-pdfs", S3_MULTI_PDFS_DIR)

    print("Splitting pdfs...")
    pdf_splitter.split_pdfs("/Users/maxramer/Desktop/file-renamer/multi-pdfs", "/Users/maxramer/Desktop/file-renamer/output_all")
    
    print("Uploading pdfs to S3...")
    s3_client.upload_local_files_to_s3("/Users/maxramer/Desktop/file-renamer/output_all", S3_SINGLE_PDFS_DIR)
    print("Successfully uploaded pdfs to S3!")
    
    print("Renaming S3 files...")
    file_renamer.begin(s3_client=s3_client, s3_input_dir=S3_SINGLE_PDFS_DIR, s3_output_dir=S3_RENAMED_PDFS_DIR)
    print("Downloading pdfs...")
    s3_client.download_all_files_from_s3_dir(local_dir="/Users/maxramer/Desktop/file-renamer/renamed-single-pdfs", s3_dir=S3_RENAMED_PDFS_DIR)
    print("Complete!")