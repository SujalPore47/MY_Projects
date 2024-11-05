import streamlit as st
from crew import NewsPipeline 
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
google_llm = genai.GenerativeModel("gemini-1.5-flash-002")

def generate_overview(context):
    template = """Based upon the  context :{context}  you will generate a overview of the report which is in html
    format so the the user understand what inside in the html file like just give an overview of the report which 
    is in html format , you will not write any part of the html code not a single line you will just give an overview
    of content present inside it .
    """
    prompt = template.format(context=context)
    response = google_llm.generate_content(prompt)
    return response.text

news_pipeline = NewsPipeline()
MD_FILE_PATH = "new-blog-post.docx"  # Path to the pre-generated Markdown file


def load_html_file(file_path):
    """
    Reads an HTML file and returns its content as a string.
    
    :param file_path: The path to the HTML file.
    :return: A string containing the HTML file content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return html_content
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return None
    except IOError:
        print("An error occurred while reading the file.")
        return None
    
# Streamlit App Layout
st.title("AI Research Assistant")
st.write("Enter a topic to generate a research report and download it as a Docx file.")

# Input section for user query
template = load_html_file('template.html')
query = st.text_input("Enter your research topic:", "")

# Process the query when the button is clicked
if st.button("Generate Report"):
    if query:
        # Display a loading message while processing
        st.write("Processing your request...")

        try:
            # Run the search method with the user's query
            result = news_pipeline.search(query=query,template=template)
            response_content = result if result else "No results found."
            overview = generate_overview(context=response_content.raw)
            # Display the response
            st.write(overview)

            # Check if the Markdown file exists and provide a download link
            if os.path.exists(MD_FILE_PATH):
                st.write("Report generated successfully!")
                HTML_FILE_PATH = "generated_article.html"
                if os.path.exists(HTML_FILE_PATH):
                    st.write("Article generated successfully!")
                    with open(HTML_FILE_PATH, "rb") as file:
                        st.download_button(
                                label="Download HTML Article",
                                data=file,
                                file_name="generated_article.html",
                                mime="text/html"
                            )
                else:
                        st.write("HTML file not found. Please ensure it has been generated.")
        except Exception as e:
            # Display the error message if an exception occurs
            st.write(f"An error occurred: {str(e)}")
    else:
        st.write("Please enter a topic before generating the report.")
