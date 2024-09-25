import os
from dotenv import load_dotenv
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search.tool import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool, initialize_agent

# Load environment variables from .env file
load_dotenv()

# Fetch API keys from environment variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class SearchTheWeb:
    def __init__(self):
        # Validate presence of API keys
        if not TAVILY_API_KEY:
            raise ValueError("Tavily API key is missing. Please set the TAVILY_API_KEY environment variable.")
        if not GOOGLE_API_KEY:
            raise ValueError("Google API key is missing. Please set the GOOGLE_API_KEY environment variable.")
        
        # Initialize TavilySearchAPIWrapper without passing api_key since it's set by env variable
        self.search = TavilySearchAPIWrapper()

        # Initialize TavilySearchResults tool
        self.tavily_tool = TavilySearchResults(max_results=3)

        # Define tools, combining Tavily's API wrapper and search results tool
        self.tools = [
            Tool(
                name="Tavily Search Results",
                func=self.tavily_tool.invoke,
                description="Fetches search results based on the query input."
            ),
        ]
        
        # Initialize the Language Model (LLM) using ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model ="gemini-1.5-flash",
            api_key=GOOGLE_API_KEY,
            temperature=0.5, 
            max_retries=5
        )
        
        # Initialize the agent with the defined tools and LLM
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent="zero-shot-react-description",
            verbose=True  # Set to True to enable detailed logs
        )
    
    def websearch(self, user_input: str) -> str:
        try:
            # Use the agent to execute the search
            result = self.agent_executor.run(user_input)
            return result
        except Exception as e:
            return f"An error occurred during the web search: {e}"