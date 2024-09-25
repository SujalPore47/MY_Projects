from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import streamlit as st
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class IMGHandler:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-flash")

        # Define the prompt template
        self.prompt_template_for_img = PromptTemplate(
            template="""You are a helpful AI assistant / image chatbot with extensive knowledge
            who helps the user to answer their queries using the image as reference.
            Answer:"""
        )

    def get_file_suffix(self, img_file):
        if img_file is not None:
            return img_file.name.split('.')[-1].lower()
        return None   

    def file_loader(self, img_file):
        file_suffix = self.get_file_suffix(img_file)
        temp_filename = f"temp.{file_suffix}"

        with open(temp_filename, "wb") as f:
            f.write(img_file.getbuffer())

        if file_suffix in ["jpg", "jpeg", "png"]:
            image = Image.open(temp_filename)
            return image
        else:
            st.error("Unsupported file format.")
            os.remove(temp_filename)
            return None 

    # Function to get response from Gemini without Tesseract
    def get_gemini_response_without_tesseract(self,input_text, img_file, prompt):
        img = self.file_loader(img_file)
        response = self.model.generate_content([input_text,img, prompt])
        return response.text
