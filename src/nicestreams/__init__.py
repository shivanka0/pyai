import os
from openai import OpenAI
import PyPDF2
from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
from dotenv import load_dotenv

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
        messages=[
            {"role": "system", "content": "You summarize the following texts that u get:"},
            {
                "role": "user",
                "content": " " + text
            }
        ]
    )
    text = completion.choices[0].message.content
    return text
# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and process
@app.route('/upload', methods=['POST'])
def upload_pdf():
    if request.files.getlist('notes') is None:
        return jsonify({'error': 'No file uploaded 1'}), 400

    # Get all the uploaded files as a list
    notes = request.files.getlist('notes')  # This retrieves a list of files

    if notes is None:
        return jsonify({'error': 'No files uploaded 2'}), 400

    extracted_texts = []

    # Loop through the list of uploaded files
    for note in notes:
        try:
            # Extract text from the current PDF
             extracted_text = extract_text_from_pdf(note)
             if extracted_text is None:
                 return jsonify({'error': 'Error processing file'}), 400
             extracted_texts.append(extracted_text)
        except Exception as e:
            return jsonify({'error': f'Error processing file'}), 400

    # Combine the texts or handle them individually (if needed)
    combined_text = " ".join(extracted_texts)

    responses = []
    for text in extracted_texts:
        # Send the combined text to OpenAI
        try:
            response = send_text_to_openai(text)
            responses.append(response)
            response = ''
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    # # Send the combined text to OpenAI
    # try:
    #     response = send_text_to_openai()
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 400
    return jsonify(responses)


if __name__ == '__main__':
    app.run(debug=True)
