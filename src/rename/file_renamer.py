import sys
import logging
from multiprocessing import Pool
import re
from aws import s3_utils


S3 = "s3"
S3_BUCKET_NAME = "feefs-pdfs"
REGION = "us-east-1"

INPUT_PDFS_DIR = "input-single-pdfs/"
OUTPUT_PDFS_DIR = "renamed-single-pdfs/"

DATE_REGEX_MD = "\d{1}/\d{1}/\d{2}"
DATE_REGEX_MDD = "\d{1}/\d{2}/\d{2}"
DATE_REGEX_MMD = "\d{2}/\d{1}/\d{2}"
DATE_REGEX_MMDD = "\d{2}/\d{2}/\d{2}"

new_files_names_dict = {}

textract_client = s3_utils.AWSClientTextractConn(region=REGION, bucket=S3_BUCKET_NAME)

root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

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
                site_id = "no-site-id-found"
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
        if "Teen" in curr_line:
            found_teen = True
    if (found_date == False):
        new_file_name = OUTPUT_PDFS_DIR + "no-date-found"
        logging.warning("No date found! Is the file missing a date?")

    new_file_name += ".pdf"
    return new_file_name

def rename_file(file_name):
    text = textract_client.extract_text(file_name)
    return {file_name : generate_file_name(text)}

def begin(s3_client, s3_input_dir):
    logging.info("Starting...")

    single_pdfs = s3_client.get_files_from_dir(s3_input_dir)

    renamed_files_hash_table = {}
    with Pool(20) as pool:
        result = pool.map_async(rename_file, single_pdfs)
        for result in result.get():
            old_file_name = next(iter(result.keys()))
            new_file_name = next(iter(result.values()))
            if renamed_files_hash_table.get(new_file_name) == None:
                renamed_files_hash_table[new_file_name] = [old_file_name]
            else:
                collisions = renamed_files_hash_table[new_file_name]
                collisions.append(old_file_name)
                renamed_files_hash_table[new_file_name] = collisions
    logging.info(renamed_files_hash_table)

# if __name__ == "__main__":
#     # begin(S3_BUCKET_NAME, INPUT_PDFS_DIR)