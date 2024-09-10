import gradio as gr
import google.generativeai as genai
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import tempfile

def main():
    load_dotenv()

    # Load the Google API key from the environment variable
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key is None or google_api_key == "":
        print("GOOGLE_API_KEY is not set")
        exit(1)
    else:
        print("GOOGLE_API_KEY is set")

    # Configure the Gemini model
    genai.configure(api_key=google_api_key)

    def custom_prompt(input_text):
        return (
            "You are an expert data analyst. Based on the dataset provided, "
            "give detailed and accurate responses to the following question: "
            f"{input_text}"
        )

    def ask_csv_question(csv_bytes, user_question):
        if csv_bytes is None or user_question is None or user_question.strip() == "":
            return "Please upload a CSV file and ask a question."
        
        # Decode the uploaded CSV file content from bytes
        csv_content = csv_bytes.decode('utf-8')
        
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
                max_retries=2,
            )
            
            agent = create_csv_agent(llm, tmp_file_path, verbose=True, allow_dangerous_code=True)
            
            prompt = custom_prompt(user_question)
            response = agent.run(prompt)
            return response
        finally:
            # Ensure the temporary file is deleted
            os.remove(tmp_file_path)

    # Gradio interface
    interface = gr.Interface(
        fn=ask_csv_question,
        inputs=[
            gr.File(type="binary", label="Upload CSV file"),
            gr.Textbox(lines=1, placeholder="Ask a question about your CSV", label="Question")
        ],
        outputs="text",
        title="Ask your CSV 📈"
    )

    interface.launch()

if __name__ == "__main__":
    main()
