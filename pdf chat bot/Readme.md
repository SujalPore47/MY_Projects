# CSV Chat Bot

This project creates a pdf Chat Bot using Google's Gemini model. The bot can answer questions about a pdf file that you upload.

## Features

- Upload a pdf file and ask questions about its content.
- Uses Google's Gemini model for natural language processing.
- Simple web interface built with Gradio.

1. **Install the required packages:**

    ```sh
    # Specify Python version
    python==3.10.14
    pip install -r requirements.txt
    ```

2. **Set up environment variables:**

    Create a `.env` file in the root directory and add your Google API key:

    ```env
    GOOGLE_API_KEY=your_google_api_key_here
    ```

3. **Run the application:**

    ```sh
    streamlit run app.py
    ```

## Usage

1. Open your browser and go to ``.
2. Upload a CSV file.
3. Ask a question about the data in the CSV file.

## Requirements

- Python 3.7+
- See `requirements.txt` for the full list of dependencies.

## Acknowledgements

- [Gradio](https://gradio.app)
- [Google Generative AI](https://ai.google.dev/gemini-api/docs/api-key)
- [LangChain](https://python.langchain.com/en/latest/)
