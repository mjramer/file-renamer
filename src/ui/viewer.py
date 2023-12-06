import tkinter as tk
from tkinter import filedialog
import subprocess
import os

multi_pdf_file = ""
pdf_output_dir = ""

folder_result_name = ""
file_result_name = ""


def choose_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_label.config(text=f"Selected Folder: {os.path.basename(folder_path).split('/')[-1]}")
        pdf_output_dir = folder_path
    

def choose_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_label.config(text=f"Selected File: {os.path.basename(file_path).split('/')[-1]}")
        multi_pdf_file = file_path


def run_script():
    subprocess.run(["python", "pdf_splitter.py", multi_pdf_file, pdf_output_dir])  # Replace "your_script.py" with the actual script filename
    # After executing the script, schedule the thank-you message and window close
    window.after(2000, show_thank_you)

def show_thank_you():
    # Update the labels with the thank-you message
    folder_label.config(text="Thanks for splitting pdfs with Bad Bunny! Adios")
    file_label.config(text="")
    # Schedule window close after 2 seconds
    window.after(2000, close_window)

def close_window():
    window.destroy()

# Create the main window
window = tk.Tk()
window.title("Bad Bunny Themed File Chooser and Script Runner")

# Set window size and position
window.geometry("600x400")

# Add Bad Bunny image as a background
try:
    image = tk.PhotoImage(file='img/bad-bunny.png')
    background_label = tk.Label(window, image=image)
    background_label.image = image
    background_label.place(relwidth=1, relheight=1)
except tk.TclError:
    print("Unable to load image. Make sure the image file is in GIF or PGM/PPM format.")

# # Add button to run a different script
script_button = tk.Button(window, text="Split PDF!", command=run_script, fg="brown", bg="black")
script_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# Add label to display selected folder
folder_label = tk.Label(window, text="Selected Folder: None", fg="white", bg="#87CEEB")
folder_label.pack(side=tk.BOTTOM, padx=10, pady=10)

# Add button to choose a folder
folder_button = tk.Button(window, text="Choose Output Folder", command=choose_folder, bg="#87CEEB")
folder_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# Add label to display selected file
file_label = tk.Label(window, text="Selected PDF: None", fg="white", bg="#87CEEB")
file_label.pack(side=tk.BOTTOM, padx=10, pady=10)

# Add button to choose a file
file_button = tk.Button(window, text="Choose PDF", command=choose_file, bg="#87CEEB")
file_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# Run the main loop
window.mainloop()
