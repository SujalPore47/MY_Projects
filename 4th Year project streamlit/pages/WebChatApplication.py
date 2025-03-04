import streamlit as st
from Rag_chat_backend.web_chat_logic import WEBQA
from Rag_chat_backend.web_data_scraping import WebQdrantHandler
from dotenv import load_dotenv
import time
# Load environment variables
load_dotenv()

class WebChatApp:
    def __init__(self):
        self.web_qa = WEBQA()
        self.web_db = WebQdrantHandler()
        self.initialize_ui()

    def initialize_ui(self):
        st.set_page_config(page_title="Chat with Web Data",layout="wide")
        # st.set_option("client.showErrorDetails", False)
        st.title("Chat with Web data")

        # Initialize Chat History
        if "web_chat_history" not in st.session_state:
            st.session_state.web_chat_history = []

        # Sidebar
        self.setup_sidebar()

    def process_web_data(self, web_link):
        try:
            processing_result = self.web_db.load_web_to_qdrant_collection(
                website_link=web_link, collection_name="chat with web app"
            )
            if processing_result["Success"]:
                st.sidebar.success("The document has been successfully loaded.")
            else:
                st.error(f"Error processing document: {processing_result['Error']}")
        except Exception as e:
            st.error(f"Error processing document: {e}")

    def setup_sidebar(self):
        if st.sidebar.button("Clear Chat History"):
            st.session_state.web_chat_history = []
            st.sidebar.success("Chat history cleared!")

        web_link = st.sidebar.text_input("Enter your link")
        if web_link and st.sidebar.button("Submit and Process Website data"):
            # Validate and convert the link format
            if not web_link.startswith("http://") and not web_link.startswith("https://"):
                if web_link.startswith("www."):
                    # Automatically prepend 'https://' if the user only entered a 'www.' link
                    web_link = "https://" + web_link
                else:
                    st.error("Invalid link format. Please enter a valid URL (e.g., https://example.com).")
                    return  # Stop further processing if the link is invalid
            
            # If we reach here, the link is valid and possibly converted; process the web data
            self.process_web_data(web_link=web_link)


    def format_chat_history(self,chat_history):
        formatted_history = "### Chat_History:\n\n"
        for chat in chat_history:
            role = "User" if chat["role"] == "user" else "Assistant"
            formatted_history += f"**{role}:** {chat['content']}\n\n"
        return formatted_history.strip()

    def chat_history_display(self):
        """Displays full chat history with avatars and retrieved documents."""
        if st.session_state.web_chat_history:
            for chat in st.session_state.web_chat_history:
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

                for ai_response in self.web_qa.async_get_answer_and_docs(
                        question=user_query,
                        chat_history=self.format_chat_history(st.session_state.web_chat_history[-4:])
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
            st.session_state.web_chat_history.append({"role": "user", "content": user_query})
            st.session_state.web_chat_history.append({"role": "ai", "content": response_str, "retrieved_docs": retrieved_docs})

    def run(self):
        self.chat_history_display()
        self.handle_chat()

if __name__ == "__main__":
    app = WebChatApp()
    app.run()
