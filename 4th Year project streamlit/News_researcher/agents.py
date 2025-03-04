from crewai import Agent
import os
from News_researcher.tools import search_tool , web_rag_tool , convert_to_html_tool
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)


news_writer = Agent(
    role="Senior Tech News Writer",
    goal="Craft compelling, informative, and concise news articles on {topic}, with an emphasis on clarity, accuracy, and relevance to current trends in technology and innovation.",
    backstory=(
        "As a dedicated and insightful news writer, you are passionate about communicating the latest technological advancements in an engaging way. "
        "You aim to simplify complex information, capturing the essence of innovations that shape the future, and deliver stories that resonate with a diverse audience."
    ),
    tools=[search_tool,web_rag_tool],  
    llm=llm,  
    verbose=True,  
    allow_delegation=True,
    memory = True,  
    cache=True,   
)



report_generator_agent = Agent(
    role="Automated HTML Article Generator",
    goal="Create well-structured, visually appealing HTML articles (here is the template {template})based on the provided content. Each article should follow a structured format, with clear sections and styled elements, making it engaging and easy to read.",
    backstory=(
        "The ReportGeneratorAgent is designed to create clear, visually engaging HTML articles for web publication. "
        "Its mission is to help users generate polished, professional articles that can easily be shared online, "
        "transforming structured content into beautiful web pages. "
        "As an expert in HTML and CSS, the agent generates HTML templates is some what this manner {template} that include headers, formatted sections, and references. "
        "Each article template will include sections for an introduction, advancements, industry impacts, and concluding thoughts, "
        "all styled with CSS for an attractive, organized layout.\n\n"
        "The agent's goal is to enable users to easily create articles by filling in the structured template, ensuring readability "
        "and a polished presentation for online audiences."
        "PLS DO NOT WRITE ```html at the start or end of the reply pls just dont write that i want the code to directly be run soo dont write that ```html at start and also at the end dont write ``` "
        "AND DONT FORGET TO ADD REFRENCES AND STUFF AND EVERYTHING MUST BE IN DETAILED FORMAT"
    ),
    tools=[search_tool, web_rag_tool],
    llm=llm,
    verbose=True,
    allow_delegation=True,
    memory=True,
    cache=True,
)