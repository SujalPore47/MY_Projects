import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Studently.ai", layout="wide",initial_sidebar_state="auto")

st.markdown("""
    <style>
    /* Import a modern font */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    /* ---------------------------
       Title Animation (unchanged)
    --------------------------- */
    @keyframes typing {
        0% { width: 0; }
        50% { width: 12ch; }
        100% { width: 0; }
    }
    @keyframes blink-caret {
        50% { border-color: transparent; }
    }
    /* The glow keyframes are removed for a cleaner look:
    @keyframes glow {
        0% { text-shadow: 0 0 7px rgba(0,150,255,0.8); }
        20% { text-shadow: 0 0 10px rgba(0,150,255,1); }
        40% { text-shadow: 0 0 14px rgba(0,150,255,0.8); }
    }
    */
    .animated-title {
        font-size: 50px;
        font-weight: bold;
        color: white;
        white-space: nowrap;
        overflow: hidden;
        border-right: 4px solid #007BFF;
        display: inline-block;
        width: 0;   
        animation: typing 4s steps(12, end) infinite,
                   blink-caret 0.75s step-end infinite;
                   /* Removed glow animation */
    }

    /* ---------------------------------------------
       Glowing "Select an Application" Neon Animation
       (Optional: neon animation keyframes removed for simplicity)
    --------------------------------------------- */
    /*@keyframes neonGlow {
        0% {
            text-shadow: 0 0 5px #0ff, 0 0 10px #f0f, 0 0 15px #f00;
        }
        50% {
            text-shadow: 0 0 20px #0ff, 0 0 30px #f0f, 0 0 40px #f00;
        }
        100% {
            text-shadow: 0 0 5px #0ff, 0 0 10px #f0f, 0 0 15px #f00;
        }
    }*/
    .floating-text {
        font-size: 28px;
        font-family: 'poppins';
        /*font-weight: 700;*/
        text-align: center;
        color: #fff;
        opacity: 0.7;
        /* Removed neonGlow animation for simplicity */
        margin-bottom: 40px;
    }

    /* ---------------------------------------------
       Button Styling Adjustments
    --------------------------------------------- */
    div.stButton > button {
        position: flex-box;
        z-index: 1;
        padding: 50px;
        font-size: 20px;
        width: 230px;
        height: 230px;
        border: 1px solid rgba(225,225,225,0.7);
        border-radius: 50px;
        color: white;               /* Text color for visibility */
        background-color:rgb(29, 29, 29);     /* Grey background */
        overflow: visible;
        transition: transform 0.2s ease-in-out;
        box-shadow: rgba(225,225,225,0.3) 0px 5px 15px;  /* Simple white box-shadow */
    }

    div.stButton > button:hover {
        transform: scale(1.1);
    }
    
    </style>
    """, unsafe_allow_html=True)

# Center the animated title at the top
st.markdown('<div style="text-align: center;"><span class="animated-title">Studently.ai</span></div>', unsafe_allow_html=True)

# Glowing "Select an Application" text
st.markdown('<div class="floating-text">Select an Application</div>', unsafe_allow_html=True)

# Layout the buttons in a row (they will appear below the text with a 40px gap)
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Dataframe Query", use_container_width=True):
        st.switch_page("pages/DataFrameChatApplication.py")

    if st.button("News Researcher", use_container_width=True):
        st.switch_page("pages/AI_NewsResearcher.py")
with col2:
    if st.button("PDF Query", use_container_width=True):
        st.switch_page("pages/PdfChatApplication.py")
    
with col3:
    if st.button("Image Query", use_container_width=True):
        st.switch_page("pages/ImageChatApplication.py")
        
with col4:
    if st.button("Web Based chat", use_container_width=True):
        st.switch_page("pages/WebChatApplication.py")
