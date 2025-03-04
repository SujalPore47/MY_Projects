import os
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_experimental.tools import PythonAstREPLTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain_core.runnables import RunnableParallel

# Load environment variables
load_dotenv()

# Streamlit configuration
st.set_page_config(page_title="DataFrame Query Bot", page_icon="📊", layout="wide")
st.set_option("client.showErrorDetails", False)

class DataFrameQueryBot:
    def __init__(self):
        self.model_to_use = None
        self.llm = None
        self.df = None
        self.chain = None
        self.init_session()
        self.init_sidebar()

    def init_session(self):
        if "csv_chat_history" not in st.session_state:
            st.session_state.csv_chat_history = []

    def init_sidebar(self):
        if st.sidebar.button("Clear Chat History"):
            st.session_state.csv_chat_history = []
            st.sidebar.success("Chat history cleared!")
        
        self.model_to_use = st.sidebar.selectbox("Change model", ["Gemini", "Gpt-4o-mini"])
        self.llm = self.init_llm()
        uploaded_file = st.sidebar.file_uploader("Upload your data file (CSV or Excel)", type=["csv", "xlsx", "xls"])
        if uploaded_file:
            self.load_dataframe(uploaded_file)
    
    def init_llm(self):
        if self.model_to_use == "Gpt-4o-mini":
            return ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash-002", api_key=os.getenv("GOOGLE_API_KEY"))
    
    def load_dataframe(self, uploaded_file):
        try:
            self.df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            st.sidebar.success("File uploaded successfully!")
            st.subheader("DataFrame Preview")
            st.dataframe(self.df.head(), use_container_width=True)
            self.setup_langchain()
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    def setup_langchain(self):
        tool = PythonAstREPLTool(locals={"df_1": self.df})
        parser = JsonOutputKeyToolsParser(key_name=tool.name, first_tool_only=True)
        llm_with_tool = self.llm.bind_tools(tools=[tool], tool_choice=tool.name)

        df_context = f"""
        ```python
        df_1.head().to_markdown()
        >>> {self.df.head().to_markdown()}
        ```
        """
        system_prompt = f"""
        # Action:
        You are an AI assistant with access to pandas DataFrames derived from an uploaded file. Your task is to generate Python code to answer 
        user queries related to the data using pandas.
        # DataFrame Preview:
        {df_context}
        # Instructions:
        - Answer only database-related queries.
        - Generate concise, executable pandas code.
        - Do not use external libraries unless explicitly requested.
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "This is the question{question}, and this is the chat history {chat_history}")
        ])
        self.chain = RunnableParallel({"response": prompt | llm_with_tool | parser | tool})
    
    def display_chat(self):
        user_query = st.chat_input("Enter your query")
        if user_query and self.df is not None:
            chat_history_str = "\n".join(
                f"User: {msg['content']}" if msg["role"] == "user" else f"Assistant: {msg['content']}"
                for msg in st.session_state.csv_chat_history[-4:]
            )
            
            result = self.chain.invoke({"question": user_query, "chat_history": chat_history_str})
            assistant_response = result["response"]
            
            st.session_state.csv_chat_history.append({"role": "user", "content": user_query})
            st.session_state.csv_chat_history.append({"role": "assistant", "content": assistant_response})
            
            with st.chat_message("user", avatar="👤"):
                st.write(user_query)
            with st.chat_message("ai", avatar="🤖"):
                try:
                    st.pyplot(assistant_response, use_container_width=True)
                except Exception:
                    st.write(assistant_response)

if __name__ == "__main__":
    bot = DataFrameQueryBot()
    bot.display_chat()
