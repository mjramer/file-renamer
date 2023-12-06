import fitz  # PyMuPDF
import sys
import os.path
from os import path

global_page_num = 1

def split_pdf(input_pdf_path, output_folder):
    global global_page_num
    pdf_document = fitz.open(input_pdf_path)

    print("Splitting file: " + input_pdf_path + " with " + str(range(pdf_document.page_count)) + " pages")
    for page_number in range(pdf_document.page_count):
        pdf_writer = fitz.open()
        pdf_writer.insert_pdf(pdf_document, from_page=page_number, to_page=page_number)
        
        output_path = f"{output_folder}/page_{global_page_num}.pdf"
        pdf_writer.save(output_path)
        pdf_writer.close()

        print(f"Page {page_number} saved to {output_path}")
        # global global_page_num
        global_page_num += 1

    pdf_document.close()

if __name__ == "__main__":
    # input_pdf_path = sys.argv[0]  # Replace with your input PDF file path
    input_pdfs_path = sys.argv[1]
    output_folder = sys.argv[2]  # Replace with your desired output folder
    for filename in os.listdir(input_pdfs_path):
        f = os.path.join(input_pdfs_path, filename)
        # checking if it is a file
        if os.path.isfile(f) and ".pdf" in f:
            print(f)
            split_pdf(f, output_folder)