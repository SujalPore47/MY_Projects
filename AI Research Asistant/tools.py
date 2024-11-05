from crewai_tools import SerperDevTool , WebsiteSearchTool , tool 
import os
from dotenv import load_dotenv
from crewai import LLM
import google.generativeai as genai
load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


search_tool = SerperDevTool()
web_rag_tool =WebsiteSearchTool(
    config=dict(
        llm=dict(
            provider="google",
            config=dict(
                model="gemini/gemini-1.5-flash",
                temperature=0.5
            ),
        ),
        embedder=dict(
            provider="google",
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document"
            ),
        ),
    )
)

from crewai_tools import tool
import google.generativeai as genai

@tool("convert_to_html")
def convert_to_html_tool(content: str) -> str:
    """This tool generates HTML code for a well-structured article based on the provided content. The article is styled with inline CSS to ensure readability and visual appeal."""

    # Configure the AI model
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-pro-002")

    # Template prompt for generating HTML content
    template = """
    Generate an HTML article template based on the provided content. The structure should follow:
    
    1. **Introduction to the Trend**: Provide context for the recent developments in {topic}.
    2. **Current Advancements**: Detail significant innovations and recent advancements.
    3. **Impact on Industries and Communities**: Explain the relevance of these developments in practical applications.
    4. **Concluding Thoughts**: Summarize insights and discuss future possibilities.
    5. PLS DO NOT WRITE ```html at the start or end of the reply pls just dont write that i want the code to directly be run soo dont write that ```html at start and also at the end dont write ```  
    
    Each section should use <h2> tags for headings, <p> tags for content, and end with a "References" section styled with inline CSS.
    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Article on Recent Developments in {topic}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f7fa; color: #333; }}
            .container {{ max-width: 800px; margin: 20px auto; padding: 20px; background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); }}
            h1 {{ text-align: center; color: #0056b3; margin-bottom: 20px; font-size: 2.8em; text-transform: uppercase; }}
            h2 {{ color: #333; margin-top: 20px; font-size: 1.8em; border-bottom: 2px solid #0056b3; padding-bottom: 5px; }}
            p {{ line-height: 1.6; font-size: 1.1em; margin: 10px 0; padding: 0 10px; text-indent: 1em; }}
            .references {{ margin-top: 30px; font-size: 1em; border-top: 2px solid #e9ecef; padding-top: 10px; }}
            .reference {{ margin: 5px 0; background-color: #f8f9fa; padding: 10px; border-left: 5px solid #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Recent Developments in {topic}</h1>
            <h2>1. Introduction to the Trend</h2>
            <p>{{introduction_content}}</p>
            <h2>2. Current Advancements</h2>
            <p>{{advancements_content}}</p>
            <h2>3. Impact on Industries and Communities</h2>
            <p>{{impact_content}}</p>
            <h2>4. Concluding Thoughts</h2>
            <p>{{conclusion_content}}</p>
            <div class="references">
                <h3>References</h3>
                <div class="reference">[1] Reference example</div>
                <div class="reference">[2] Reference example</div>
            </div>
        </div>
    </body>
    </html>
    

    Ensure that the content for each section is logically formatted, with clear headers, well-organized paragraphs, and properly styled references.
    """

    # Format the prompt with the topic content
    prompt = template.format(topic=content)

    # Generate the HTML content
    response = model.generate_content([prompt])
    
    # Return the generated HTML code
    return response.text
