import os
from openai import OpenAI
import PyPDF2
from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import boto3

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Function to send text to OpenAI API
def send_text_to_openai(text):
    completion = client.chat.completions.create(
        model="gpt-4",
        message=[
            {"role": "system", "content": "You summarize the following texts that you get:"},
            {"role": "user", "content": " " + text}
        ]
    )
    return completion.choices[0].message


# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and process
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the 'notes' key is in the request files
    if 'notes' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    # Retrieve a list of uploaded files with the name 'notes'
    notes = request.files.getlist('notes')

    if notes.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    extracted_text = ""
    # Loop through each file, upload to S3, and extract text
    for note in notes:
        # Upload each file to S3
        upload_success = upload_file(note,'notestreams3',note.filename)
        if not upload_success:
            return jsonify({'error': f'Failed to upload {note.filename} to S3'}), 500

        # Extract text from the uploaded PDF
        try:
            extracted_text += " " + extract_text_from_pdf(note)
        except Exception as e:
            return jsonify({'error': f'Failed to extract text from {note.filename}: {str(e)}'}), 400

    # Send the extracted text to OpenAI
    try:
        response = send_text_to_openai(extracted_text)
    except Exception as e:
        return jsonify({'error': f'Failed to get response from OpenAI: {str(e)}'}), 400

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=False)
