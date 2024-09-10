import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.document_loaders import PDFMinerLoader


# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the prompt template
prompt_template = """
You are a helpful AI assistant / PDF chatbot with extensive knowledge who helps the user to answer their queries using the PDF document as reference.

Context:\n{context}\n

Question:\n{question}\n

Answer:
"""

# Function to get Gemini response
def get_gemini_response(context, question):
    # Ensure that context is not empty
    if not context.strip():
        return "Error: No content available to answer the question."
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_template.format(context=context, question=question))
        
        # Ensure the response object has a valid text field
        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "No valid response from the model."
    except Exception as e:
        st.error(f"Error in generating response: {e}")
        return "Error generating response."

# Function to load and process PDF files using UnstructuredLoader
def file_loader(upload_file):
    file_suffix = get_file_suffix(upload_file)
    temp_filename = f"temp.{file_suffix}"

    with open(temp_filename, "wb") as f:
        f.write(upload_file.getbuffer())

    if file_suffix == "pdf":
        try:
            loader = PDFMinerLoader(temp_filename)
            documents = loader.load()
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            documents = None
        os.remove(temp_filename)  # Only remove if file was processed successfully
        return documents
    else:
        st.error("Unsupported file format.")
        os.remove(temp_filename)
        return None

# Function to extract content from documents
def extract_content_from_documents(processed_documents):
    contents = [doc.page_content for doc in processed_documents]
    return ' '.join(contents)

# Function to get file suffix
def get_file_suffix(upload_file):
    if upload_file is not None:
        return upload_file.name.split('.')[-1].lower()
    return None

# Streamlit Interface
def main():
    st.set_page_config(page_title="Chat PDF", page_icon="💁")
    st.header("Chat with PDF using Gemini💁")

    # Initialize session state
    if 'context' not in st.session_state:
        st.session_state['context'] = ""

    # File uploader and process button
    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your Files", accept_multiple_files=True, type=["pdf"])  # Restrict to PDF
        if st.button("Submit & Process"):
            if pdf_docs:
                with st.spinner("Processing..."):
                    try:
                        raw_text = ""
                        for file in pdf_docs:
                            processed_documents = file_loader(file)
                            if processed_documents:
                                raw_text += extract_content_from_documents(processed_documents)
                        
                        # Debug: Output the combined text from all processed files
                        st.write("Combined Raw Text:", raw_text)  # Displaying the combined raw text for debugging
                        
                        # Store the combined document content in session state
                        st.session_state['context'] = raw_text
                        st.success("Processing complete. You can now ask questions about the content.")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Please upload at least one file.")

    # Question input and response display
    user_question = st.text_input("Ask a Question from the Uploaded Files")
    if user_question:
        if st.session_state['context']:
            with st.spinner("Fetching answer..."):
                response = get_gemini_response(st.session_state['context'], user_question)
                st.write("**Reply:**")
                st.write(response)
        else:
            st.warning("Please process the files first.")

if __name__ == "__main__":
    main()
