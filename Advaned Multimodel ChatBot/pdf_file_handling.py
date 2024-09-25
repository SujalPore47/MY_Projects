import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.document_loaders import PDFMinerLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
import tempfile

class PDFHandler:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API key is missing. Please set the GOOGLE_API_KEY environment variable.")
        genai.configure(api_key=api_key)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=api_key,
            temperature=0.5,
        )  # Initialize the language model

    # Load the file and extract documents
    def file_loader(self, pdf_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_file.getbuffer())
            temp_filename = temp_file.name

        try:
            loader = PDFMinerLoader(temp_filename)
            documents = loader.load()
            if documents:
                st.success(f"Loaded {len(documents)} document(s) from the PDF.")
                return documents  # Return the list of document objects
            else:
                st.error("No documents loaded from the PDF.")
                return None
        except Exception as e:
            st.error(f"Error loading PDF: {e}")
            return None

    # Use a simple QA chain to generate a response from the PDF content
    def get_qa_response(self, documents, question):
        if not documents:
            return "No documents to process."

        qa_chain = load_qa_chain(llm=self.llm, chain_type="stuff")
        
        # Structure the inputs correctly
        inputs = {
            "input_documents": documents,
            "question": question
        }
        
        response = qa_chain.invoke(inputs)
        return response["output_text"]
