# Import necessary libraries
from streamlit_mic_recorder import mic_recorder 
import streamlit as st
import os
from streamlit_chat import message
from datetime import datetime
import json
import uuid
import google.generativeai as genai
from dotenv import load_dotenv
from csv_file_handling import CSVHandler  
from pdf_file_handling import PDFHandler  
from img_file_handling import IMGHandler  
from search_the_web import SearchTheWeb
from youtube_summariser import YoutubeSummariser
from audio_handler import transcribe_audio
####################################### Load environment variables ################################################################
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Advanced Multimodel Chat Application"
###################################################################################################################################
                                              #Main Function                             
###################################################################################################################################

def main():
    # Initialize handlers
    csv_handler = CSVHandler()
    pdf_handler = PDFHandler()
    img_handler = IMGHandler()
    web_search  = SearchTheWeb()
    yt_summarise = YoutubeSummariser()
    # Initialize session state for history
    if 'history' not in st.session_state:
        st.session_state['history'] = []
###################################################################################################################################
    # Function to handle conversation history
    def load_history():
        return st.session_state['history']

    def save_history(history):
        st.session_state['history'] = history
###################################################################################################################################
    # Function to generate AI response
    def generate_response(history , user_input):
        # Format history as a string
        history_text = "\n".join([f"{entry['time']}: {entry['user_input']} → {entry['ai_response']}" for entry in history])
        # Combine history with user input
        prompt = f"{history_text}\n{user_input}\nAI:"
        llm_model = genai.GenerativeModel("gemini-1.5-flash")
        response = llm_model.generate_content(prompt)
        return response.text if response else "Error generating response."
###################################################################################################################################

    # Streamlit page configuration
    st.set_page_config(page_title="Advanced Multimodel Chat Application", layout="wide")
###################################################################################################################################

    # Main title
    st.title("Multi_Model ChatBot")
###################################################################################################################################

    # Load conversation history
    history = load_history()
###################################################################################################################################

    # Display chat messages from history
    st.write("## Chat")
    for entry in history:
        message(entry['user_input'], is_user=True, key=f"user_{uuid.uuid4()}")
        message(entry['ai_response'], key=f"ai_{uuid.uuid4()}")
###################################################################################################################################

    # Sidebar for file uploads and management
    st.sidebar.header("Functionalities")
###################################################################################################################################
######################################### CSV file uploader and processing #########################################################
    if csv_file := st.sidebar.file_uploader("Upload a CSV file", type="csv"):
        if st.sidebar.button("Submit and Process CSV"):
            st.session_state['csv_bytes'] = csv_file.read()# Store CSV content in session state
            st.sidebar.success("CSV file uploaded successfully!")
################################ Button to remove CSV data from session state #####################################################
    if 'csv_bytes' in st.session_state and st.sidebar.button("Stop chatting with CSV file"):
        del st.session_state['csv_bytes']# Remove from session state
        st.sidebar.info("CSV data removed. You are now chatting without the CSV context.")
###################################################################################################################################
######################################### PDF file uploader and processing#########################################################
    if pdf_file := st.sidebar.file_uploader("Upload a PDF file", type="pdf"):
        if st.sidebar.button("Submit and Process PDF"):
            documents = pdf_handler.file_loader(pdf_file)  # Process PDF file
            if documents:
                st.session_state['pdf_documents'] = documents  # Store in session state
                st.sidebar.success("PDF file processed successfully!")
            else:
                st.sidebar.error("Error processing PDF.")
#################################### Button to remove PDF data from session state ####################################################
    if 'pdf_documents' in st.session_state and st.sidebar.button("Stop chatting with PDF file"):
        del st.session_state['pdf_documents']
        st.sidebar.info("PDF data removed. You are now chatting without the PDF context.")
######################################################################################################################################
################################################ Image file uploader ##################################################################
    if img_file := st.sidebar.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"]):
        if st.sidebar.button("Submit and Process IMG"):
            st.session_state['img_file'] = img_file  # Store image file in session state
            st.sidebar.success("Image file uploaded successfully!")
################################### Button to remove image data from session state####################################################
    if 'img_file' in st.session_state and st.sidebar.button("Stop chatting with Image file"):
        del st.session_state['img_file'] #Remove from sessions state
        st.sidebar.info("Image data removed. You are now chatting without the image context.")
#####################################################################################################################################

#####################################################################################################################################

#End of side bar

###################################################################################################################################

################################################### Function to handle input , submit and search ##############################################
    def handle_submit():
        user_input = st.session_state.get('input_text', '')
        if user_input:
            # Check if CSV data is available for CSV-related queries
            if 'csv_bytes' in st.session_state:
                csv_bytes = st.session_state['csv_bytes']
                ai_response = csv_handler.ask_csv_question(csv_bytes, user_input)
            # Check if PDF data is available for PDF-related queries
            elif 'pdf_documents' in st.session_state:
                documents = st.session_state['pdf_documents']
                ai_response = pdf_handler.get_qa_response(documents=documents, question=user_input)
            # Check if Image data is available for Image-related queries
            elif 'img_file' in st.session_state:
                image_file = st.session_state['img_file']
                template = """You are a helpful AI assistant / image chatbot with extensive knowledge
                            who helps the user to answer their queries using the image as reference.
                            Answer:"""
                ai_response = img_handler.get_gemini_response_without_tesseract(
                    input_text=user_input, img_file=image_file, prompt=template
                )
            else:
                # Generate AI response for general conversation
                ai_response = generate_response(history=history, user_input=user_input)

            # Update chat history
            history.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user_input": user_input, "ai_response": ai_response})
            save_history(history)

            # Clear the input bar
            st.session_state['input_text'] = ""
###################################################################################################################################
    def handle_search():
        user_input = st.session_state.get('input_text', '')
        if user_input:
            # Check if CSV data is available for CSV-related queries
            if 'csv_bytes' in st.session_state:
                csv_bytes = st.session_state['csv_bytes']
                ai_response = csv_handler.ask_csv_question(csv_bytes, user_input)
            # Check if PDF data is available for PDF-related queries
            elif 'pdf_documents' in st.session_state:
                documents = st.session_state['pdf_documents']
                ai_response = pdf_handler.get_qa_response(documents=documents, question=user_input)
            # Check if Image data is available for Image-related queries
            elif 'img_file' in st.session_state:
                image_file = st.session_state['img_file']
                template = """You are a helpful AI assistant / image chatbot with extensive knowledge
                            who helps the user to answer their queries using the image as reference.
                            Answer:"""
                ai_response = img_handler.get_gemini_response_without_tesseract(
                    input_text=user_input, img_file=image_file, prompt=template
                )
            else:
                # Generate AI response for general conversation
                ai_response = web_search.websearch(user_input=user_input)

            # Update chat history
            history.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "user_input": user_input, "ai_response": ai_response})
            save_history(history)

            # Clear the input bar
            st.session_state['input_text'] = ""
###################################################################################################################################
    def handle_summarise():
        user_input = st.session_state.get('input_text', '')
        if user_input:
            try:
                # Define the prompt for the summarizer
                prompt = """You are a YouTube video summarizer. You will be taking the transcript text
                and summarizing the entire video, providing the important summary in points within 250 words.
                Please provide the summary of the text given here: """

                # Attempt to extract the transcript from the YouTube video
                transcribe_text = yt_summarise.extract_transcript_details(youtube_video_url=user_input)

                # Check if the transcript extraction returned an error message
                if "Invalid YouTube link" in transcribe_text or "Could not retrieve transcript" in transcribe_text:
                    st.error(transcribe_text)
                    return

                # If transcript extraction is successful, generate the summary
                ai_response = yt_summarise.get_summary(prompt=prompt, yt_transcribe_text=transcribe_text)

                # Check if summary generation returned an error message
                if "An error occurred while generating the summary" in ai_response:
                    st.error(ai_response)
                    return

                # Update chat history
                history.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "user_input": user_input,
                    "ai_response": ai_response
                })
                save_history(history)

            except ValueError:
                st.error("Please paste an appropriate YouTube link.")
            except Exception as e:
                # Catch all other exceptions and print a user-friendly message
                st.error(f"An error occurred while processing the YouTube link. Please ensure the link is correct and try again.")

            finally:
                # Clear the input bar regardless of success or failure
                st.session_state['input_text'] = ""                
###################################################################################################################################
    def handle_audio():
            if voice_recorder is not None:
                audio_bytes = voice_recorder['bytes']                
                # Transcribe audio bytes
                audio_text = transcribe_audio(audio_bytes=audio_bytes)
                if audio_text:
                    st.session_state['audio_text'] = audio_text
                    st.success("Successfully loaded the audio")
                    user_input = st.session_state['audio_text']                   
                    # Process user input
                    if user_input:
                        if 'csv_bytes' in st.session_state:
                            csv_bytes = st.session_state['csv_bytes']
                            ai_response = csv_handler.ask_csv_question(csv_bytes, user_input)
                        elif 'pdf_documents' in st.session_state:
                            documents = st.session_state['pdf_documents']
                            ai_response = pdf_handler.get_qa_response(documents=documents, question=user_input)
                        elif 'img_file' in st.session_state:
                            image_file = st.session_state['img_file']
                            template = """You are a helpful AI assistant / image chatbot with extensive knowledge
                                        who helps the user to answer their queries using the image as reference.
                                        Answer:"""
                            ai_response = img_handler.get_gemini_response_without_tesseract(
                                input_text=user_input, img_file=image_file, prompt=template
                            )
                        else:
                            ai_response = generate_response(history=history, user_input=user_input)
                        
                        # Append to history and save
                        history.append({"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "user_input": user_input, "ai_response": ai_response})
                        save_history(history)
                        
                        # Clear the audio input
                        st.session_state['audio_text'] = ""
                    else:
                        st.write("No input detected from the recorded audio.")
                else:
                    st.write("No transcribed text detected from the audio.")
            else:
                st.error("No audio data found. Please try recording again.")


    # Form to handle all the input operations
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_area("Type your message...", key="input_text", height=50)
        
        # Create five columns for buttons
        col1, col2, col3, col4 = st.columns([0.4, 0.8, 1, 1])
        
        with col1:
            submit_button = st.form_submit_button("Send", on_click=handle_submit)
            
        with col2:
            search_button = st.form_submit_button("Search The Web", on_click=handle_search)

        with col3:
            YT_button = st.form_submit_button("Summarise The Video", on_click=handle_summarise) 
        
        with col4:
            audio_button = st.form_submit_button("Send_audio", on_click=handle_audio)

    voice_recorder = mic_recorder(start_prompt="Start recording",stop_prompt="Stop recording")

###################################################################################################################################
                                           #Handling Voice Input
###################################################################################################################################

###################################################################################################################################
###################################################################################################################################
    # Save conversation to a file button (Optional)
    if st.sidebar.button("Save Chat"):
        with open("chat_history.json", "w") as f:
            json.dump(history, f, indent=4)
        st.sidebar.success("Chat saved to chat_history.json")
###################################################################################################################################
if __name__ == "__main__":
    main()