import google.generativeai as genai
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import tempfile

class CSVHandler:
    def __init__(self):
        load_dotenv()
        # Configure the Gemini model
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    def custom_prompt(self, input_text):
        return (
            "You are an expert data analyst. Based on the dataset provided, "
            "give detailed and accurate responses to the following question: "
            f"{input_text}"
        )

    def ask_csv_question(self, csv_bytes, user_question):
        if csv_bytes is None or user_question is None or user_question.strip() == "":
            return "Please upload a CSV file and ask a question."

        # Write CSV content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            tmp_file.write(csv_bytes)
            tmp_file_path = tmp_file.name

        try:
            # Create the Gemini agent with dangerous code allowance
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.5,
                max_tokens=None,
                timeout=None,
                max_retries=5,
            )
            
            agent = create_csv_agent(llm, tmp_file_path, verbose=True, allow_dangerous_code=True , handle_parsing_errors = True)
            
            prompt = self.custom_prompt(user_question)
            response = agent.run(prompt)
            return response
        finally:
            # Ensure the temporary file is deleted
            os.remove(tmp_file_path)
