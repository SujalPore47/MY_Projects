from dotenv import load_dotenv
load_dotenv()

# Import necessary libraries
import streamlit as st 
import os
import google.generativeai as genai
from PIL import Image
import pytesseract
import io

# Configure Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Function to get response from Gemini without Tesseract
def get_gemini_response_without_tesseract(input_text, img, prompt):
    response = model.generate_content([input_text,img, prompt])
    return response.text

# Function to get response from Gemini with Tesseract
def get_gemini_response_with_tesseract(input_text, image_text, prompt):
    response = model.generate_content([input_text, image_text, prompt])
    return response.text

# Function to get details from the image
def get_image_details(upload_file):
    # Open the image
    image = Image.open(upload_file)

    # Extract image details
    image_details = {
        "format": image.format,
        "size": image.size,
        "mode": image.mode,
        "type": upload_file.type,
        "filename": upload_file.name
    }
    
    # Get byte data
    byte_data = io.BytesIO()
    image.save(byte_data, format=image.format)
    byte_data = byte_data.getvalue()
    image_details["byte_data"] = byte_data
    
    # Extract text from the image using Tesseract
    text = pytesseract.image_to_string(image)
    image_details["text"] = text
    
    return image_details, image

# Initialize Streamlit app
st.set_page_config(page_title="Invoice Extractor")
st.header("Multi-language Invoice Extractor")

input_text = st.text_input("Input", key="input")
upload_file = st.file_uploader("Choose an invoice image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

if upload_file is not None:
    image = Image.open(upload_file)
    st.image(image, caption="Uploaded Invoice", use_column_width=True)

submit = st.button("SUBMIT")

input_prompt = """
You will extract all the information provided from the image, which is an invoice,
and answer all the input questions using the invoice image that has been uploaded to you.
"""

if submit and upload_file is not None:
    img = Image.open(upload_file)
    image_details , image = get_image_details(upload_file)
    image_text = image_details["text"]
    
    response_without_tesseract = get_gemini_response_without_tesseract(input_text, img, input_prompt)
    response_with_tesseract = get_gemini_response_with_tesseract(input_text, image_text, input_prompt)
    
    st.subheader("Response with Tesseract:")
    st.write(response_with_tesseract)
    
    st.subheader("Response without Tesseract:")
    st.write(response_without_tesseract)
