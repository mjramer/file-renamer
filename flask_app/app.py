from flask import Flask, render_template, request, redirect, url_for, session
import subprocess
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_directory', methods=['POST'])
def select_directory():
    # Get the selected directory path from the form
    selected_directory = request.form['directory']
    
    # Store the selected directory path in session
    session['selected_directory'] = selected_directory

    return redirect(url_for('index'))

@app.route('/generate', methods=['POST'])
def generate():
    # Get the selected directory path from session
    selected_directory = session.get('selected_directory')

    if selected_directory:
        # Execute the Python script with the selected directory as an argument
        script_path = os.path.join(os.getcwd(), 'scripts', 'generate_script.py')
        subprocess.run(['python', script_path, selected_directory])
        return "Script executed successfully!"

    return "Please select a directory before generating."

if __name__ == '__main__':
    app.run(debug=True)
