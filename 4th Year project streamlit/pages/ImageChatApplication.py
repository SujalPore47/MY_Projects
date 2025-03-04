from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
from Rag_chat_backend.image_database import DatabaseChroma
# Load environment variables
load_dotenv()


class ImageChatApplication:
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.db = DatabaseChroma()
        self.llm = genai.GenerativeModel("gemini-1.5-flash-002")
        self.prompt = """Analyze this image thoroughly. Provide detailed, structured responses:
                        Always maintain professional yet approachable tone."""
        
        self.init_session()
        
    def init_session(self):
        st.set_page_config("Image Chat Analyst", layout="wide")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "current_image" not in st.session_state:
            st.session_state.current_image = None

    def init_sidebar(self):
        with st.sidebar:
            st.header("Image Management")
            
            # Image upload section
            with st.expander("Upload New Image"):
                uploaded_file = st.file_uploader("Choose image", type=["jpg", "jpeg", "png"])
                if uploaded_file:
                    self.handle_image_upload(uploaded_file)
            
            # Image query section
            with st.expander("Search Images"):
                text_query = st.text_input("Describe image to find")
                if text_query:
                    self.handle_image_query(text_query)
            
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.success("History cleared!")

    def handle_image_upload(self, uploaded_file):
        """Process and store uploaded images"""
        try:
            image_dir = "uploaded_images"
            os.makedirs(image_dir, exist_ok=True)
            image_path = os.path.join(image_dir, uploaded_file.name)
            
            with Image.open(uploaded_file) as img:
                img.save(image_path)
                
            self.db.add_image(image_path)
            st.session_state.current_image = image_path
            st.session_state.chat_history = []
            
        except Exception as e:
            st.error(f"Upload error: {e}")

    def handle_image_query(self, text_query: str):
        """Handle image search and update current image"""
        new_image = self.db.query_image(text_query)
        if not new_image:
            st.error("No matching images found")
            return
            
        if new_image != st.session_state.current_image:
            st.session_state.chat_history = []
            st.session_state.current_image = new_image
            
        st.image(new_image, use_container_width=True)

    def get_ai_response(self, query: str) -> str:
        """Get response from Gemini model"""
        try:
            with Image.open(st.session_state.current_image) as img:
                response = self.llm.generate_content([self.prompt, query, img])
                return response.text
        except Exception as e:
            st.error(f"AI Error: {e}")
            return "Sorry, I couldn't process that request."

    def display_chat(self):
        """Display chat messages in proper format"""
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])               
                # Display image analysis if available
                # if msg.get("preview"):
                #     st.image(msg["preview"], caption="Analyzed Image", width=300)
    
    def handle_query(self,query):
        st.session_state.chat_history.append({
                        "role": "user",
                        "content": query
                    })
                    # Get and display AI response
        response = self.get_ai_response(query)
        st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "preview": st.session_state.current_image
                    })
        
    def run(self):
        """Main application loop"""
        self.init_sidebar()
        st.title("Interactive Image Analysis")
        st.subheader("Current Image Context")
        
        if st.session_state.current_image:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(st.session_state.current_image, use_container_width=True)
            with col2:
                self.display_chat()
                if query := st.chat_input("Ask about the image..."):
                    self.handle_query(query=query)
        else:
            st.info("Please upload or search for an image to begin")

if __name__ == "__main__":
    app = ImageChatApplication()
    app.run()