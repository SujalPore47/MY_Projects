import streamlit as st
import os
from Rag_chat_backend.chat_logic import PDFQA
from Rag_chat_backend.vector_database_logic import QdrantHandler
from dotenv import load_dotenv
import tempfile
import time
# Load environment variables
load_dotenv()

class PDFChatApp:
    def __init__(self):
        self.pdf_qa = PDFQA()
        self.database = QdrantHandler()
        self.initialize_ui()

    def initialize_ui(self):
        st.set_page_config(page_title="Chat with your PDFs",layout="wide")
        st.set_option("client.showErrorDetails", False)
        st.title("Chat with PDF")

        # Initialize Chat History
        if "pdf_chat_history" not in st.session_state:
            st.session_state.pdf_chat_history = []

        # Sidebar
        self.setup_sidebar()

    def setup_sidebar(self):
        if st.sidebar.button("Clear Chat History"):
            st.session_state.pdf_chat_history = []
            st.sidebar.success("Chat history cleared!")

        pdf_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")
        if pdf_file and st.sidebar.button("Submit and Process PDF"):
            self.process_pdf(pdf_file)

    def format_chat_history(self,chat_history):
        formatted_history = "### Chat_History:\n\n"
        for chat in chat_history:
            role = "User" if chat["role"] == "user" else "Assistant"
            formatted_history += f"**{role}:** {chat['content']}\n\n"
        return formatted_history.strip()

    def process_pdf(self, pdf_file):
        try:
            pdf_path = self.file_loader(pdf_file)
            processing_result = self.database.load_pdf_to_qdrant_collection(
                pdf_path=pdf_path, collection_name="chat with pdf app"
            )
            if processing_result["Success"]:
                st.sidebar.success("The document has been successfully loaded.")
                os.remove(pdf_path)
            else:
                st.error(f"Error processing document: {processing_result['Error']}")
        except Exception as e:
            st.error(f"Error processing document: {e}")

    def file_loader(self, pdf_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_file.getbuffer())
            return temp_file.name

    def chat_history_display(self):
        """Displays full chat history with avatars and retrieved documents."""
        if st.session_state.pdf_chat_history:
            for chat in st.session_state.pdf_chat_history:
                role, content = chat["role"], chat["content"]
                avatar = "👤" if role == "user" else "🤖"
                with st.chat_message("user" if role == "user" else "ai", avatar=avatar):
                    st.markdown(content)
                    # Show retrieved documents if available (for AI responses)
                    if role == "ai" and "retrieved_docs" in chat and chat["retrieved_docs"]:
                        with st.expander("📄 **Retrieved Documents (Click to Expand)**"):
                            st.markdown(f"<div style='color: green; font-size: 15px;'>{chat["retrieved_docs"]}</div>", 
                                        unsafe_allow_html=True)

    def handle_chat(self):
        """Handles user input and displays AI responses with animations & styled UI."""
        if user_query := st.chat_input("Enter your query"):
            with st.chat_message("user", avatar="👤"):
                st.write(user_query)
            with st.chat_message("ai", avatar="🤖"):
                # Create a placeholder for the streaming response
                response_placeholder = st.empty()
                response_str = ""  # This string accumulates the entire response
                retrieved_docs = ""  # Initialize retrieved_docs

                for ai_response in self.pdf_qa.async_get_answer_and_docs(
                        question=user_query,
                        chat_history=self.format_chat_history(st.session_state.pdf_chat_history[-4:])
                    ):
                    try:
                        # If there's a response, append it to our string and update the placeholder
                        if "response" in ai_response:
                            response_str += ai_response["response"].replace("\n", " ")
                            response_placeholder.markdown(response_str + "▌")  # Cursor effect during streaming
                            time.sleep(0.02)  # Small delay to simulate a real-time typing effect
                        else:
                            # If no response key exists, assume these are the retrieved documents
                            with st.expander("📄 **Retrieved Documents (Click to Expand)**"):
                                retrieved_docs = "\n\n".join(
                                    [f"- {doc.page_content}" for doc in ai_response["context"]["context"]]
                                )
                                st.markdown(
                                    f"<div style='color: green; font-size: 15px;'>{retrieved_docs}</div>",
                                    unsafe_allow_html=True
                                )
                    except Exception:
                        # Ignore any errors and continue streaming
                        pass
                # Final update to remove the cursor effect once streaming is complete
                response_placeholder.markdown(response_str)

            # Update chat history after streaming is done
            st.session_state.pdf_chat_history.append({"role": "user", "content": user_query})
            st.session_state.pdf_chat_history.append({"role": "ai", "content": response_str, "retrieved_docs": retrieved_docs})

    def run(self):
        self.chat_history_display()
        self.handle_chat()

if __name__ == "__main__":
    app = PDFChatApp()
    app.run()