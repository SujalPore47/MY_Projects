import re
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import google.generativeai as genai
from langchain_community.document_loaders import PebbloSafeLoader, UnstructuredFileIOLoader, UnstructuredFileLoader
from langchain_google_community import GoogleDriveLoader
import os
from PIL import Image
from pebblo.entity_classifier.entity_classifier import EntityClassifier

# Set up LLM and PWD
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
os.environ['PWD'] = os.getcwd()
ec = EntityClassifier()
# Function to get Gemini response
def get_gemini_response(input_text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(input_text)
    return response.text

# Function to load documents from Google Drive
def google_drive_loader(service_account_file, folder_id):
    loader = PebbloSafeLoader(
        GoogleDriveLoader(
            folder_id=folder_id,
            credentials_path=service_account_file,
            token_path="./google_token.json",
            recursive=True,
            file_loader_cls=UnstructuredFileIOLoader,
            file_loader_kwargs={"mode": "elements"},
            load_auth=True,
        ),
        name="app.py",
        owner="Sujal_Pore",
        description="ATS application for Gemini",
    )
    return loader.load()

# Function to extract content from documents
def extract_content_from_documents(processed_documents):
    contents = []
    for doc in processed_documents:
        content = doc.page_content
        contents.append(content)
    return ' '.join(contents)

# Function to extract file_id from the link
def extract_file_id_from_link(link):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', link)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Drive link format")

# Function to load PDF file
def pdf_loader(upload_file):
    with open("temp.pdf", "wb") as f:
        f.write(upload_file.getbuffer())
    loader = PebbloSafeLoader(
        UnstructuredFileLoader("temp.pdf", mode='elements'),
        name="app.py",
        owner="Sujal_Pore",
        description="ATS application for Gemini"
    )
    data = loader.load()
    os.remove("temp.pdf")  # Clean up the temporary file
    return data

# Function to load image
def image_loader(upload_file):
    with open("temp_image", "wb") as f:
        f.write(upload_file.getbuffer())
    loader = PebbloSafeLoader(
        UnstructuredFileLoader("temp_image", mode='elements'),
        name="app.py",
        owner="Sujal_Pore",
        description="ATS application for Gemini"
    )
    data = loader.load()
    os.remove("temp_image")
    return data

# Function to load text file
def text_file_loader(upload_file):
    with open("temp_text.txt", "wb") as f:
        f.write(upload_file.getbuffer())
    loader = PebbloSafeLoader(
        UnstructuredFileLoader("temp_text.txt", mode='elements'),
        name="app.py",
        owner="Sujal_Pore",
        description="ATS application for Gemini"
    )
    data = loader.load()
    os.remove("temp_text.txt")  # Clean up the temporary file
    return data

# Function to get the file suffix
def get_file_suffix(upload_file):
    if upload_file is not None:
        return upload_file.name.split('.')[-1].lower()
    return None

# Ensure the service account file path is correctly formatted
service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if not service_account_file or not os.path.isfile(service_account_file):
    service_account_file = r'credentials\credentials.json'
    if not os.path.isfile(service_account_file):
        raise FileNotFoundError("Service account credentials file not found. Please provide a valid path.")

# Setting up a prompt
input_prompt = """
Hey Act Like a skilled or very experienced ATS(Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage Matching based 
on JD and
the missing keywords with high accuracy
resume:{text}
description:{JD}

I want the response in a paragraph-like structure:
1. Job Description Match: <value>
2. Missing Keywords: <list>
3. Profile Summary: <summary>
"""

# Initializing Streamlit title and page config
st.set_page_config("Application Tracking System")
st.title("ATS Using Gemini")

# Job description input text
JD = st.text_input("# Please Enter The Job Description", key="JD")

# Function to upload file
upload_file = st.file_uploader("Upload Your Resume Here", type=["pdf", "jpg", "png", "jpeg", "txt"])
file_suffix = get_file_suffix(upload_file)
if upload_file is not None and file_suffix in ['jpg', 'png', 'jpeg']:
    img = Image.open(upload_file)
    st.image(img, "Your Resume", use_column_width=True)

# Function to upload file from Google Drive
st.subheader("Embed The Google Drive Link Here (if your resume is placed in Google Drive)")
link = st.text_input("Enter the link", key="link")

# Submit button for processing resume
submit = st.button("SUBMIT")

if submit:
    if JD and upload_file is not None:
        file_suffix = get_file_suffix(upload_file)
        if file_suffix == 'pdf':  # Check if the file suffix is PDF
            processed_documents = pdf_loader(upload_file)
            text = extract_content_from_documents(processed_documents)
            entities, total_count, anonymized_text = ec.presidio_entity_classifier_and_anonymizer(input_text=text,anonymize_snippets=True)
        elif file_suffix in ['jpg', 'png', 'jpeg']:  # Check if the file suffix is an image
            processed_documents = image_loader(upload_file)
            text = extract_content_from_documents(processed_documents)
            entities, total_count, anonymized_text = ec.presidio_entity_classifier_and_anonymizer(input_text=text,anonymize_snippets=True)
        elif file_suffix == 'txt':
            processed_documents = text_file_loader(upload_file)
            text = extract_content_from_documents(processed_documents)
            entities, total_count, anonymized_text = ec.presidio_entity_classifier_and_anonymizer(input_text=text,anonymize_snippets=True)
        response = get_gemini_response(input_prompt.format(text=anonymized_text, JD=JD))
        st.write(response)
        st.write(entities, total_count, anonymized_text)
    elif JD and link:
        file_id = extract_file_id_from_link(link)
        processed_documents = google_drive_loader(service_account_file, file_id)
        text = extract_content_from_documents(processed_documents)
        entities, total_count, anonymized_text = ec.presidio_entity_classifier_and_anonymizer(input_text=text,anonymize_snippets=True)
        response = get_gemini_response(input_prompt.format(text=anonymized_text, JD=JD))
        st.write(response)                
        