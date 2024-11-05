from crewai import Task
from tools import search_tool , web_rag_tool , convert_to_html_tool
from agents import news_writer , report_generator_agent



# Writing task with language model configuration
write_task = Task(
    description=(
        "Write an engaging, well-researched article on the latest trends in {topic}. "
        "Discuss recent advancements, their impact on relevant industries, and emphasize positive implications. "
        "Include credible sources and relevant links to support the information provided. "
        "The language should be accessible to a general audience, with an optimistic and informative tone."
    ),
    expected_output=(
        "A professionally structured, 4-paragraph article on recent {topic} developments in Docx format. "
        "Organize content as follows: "
        "1. Introduction to the trend, "
        "2. Current advancements, "
        "3. Impact on industries and communities, and "
        "4. Concluding thoughts on future potential. "
        "Use formal headers, clear sub-sections, and include sources in a references section at the end."
    ),
    tools=[search_tool, web_rag_tool],
    agent=news_writer,
    async_execution=False,
    output_file='new-blog-post.docx'
)

extract_and_generate_task = Task(
    description=(
        "The goal of this task is to extract relevant information from the provided content and use it to create a structured, visually appealing HTML article. "
        "The article should follow a four-part structure: Introduction, Current Advancements, Impact on Industries and Communities, and Concluding Thoughts, "
        "along with a References section at the end. The HTML should be formatted for readability and visual engagement."
    ),
    expected_output=(
        "I want the output simalar but not better in this format or template {template}"
        "An HTML document that presents a well-structured, styled article following these main sections:\n"
        "1. **Introduction to the Trend** - Provides context for recent developments in the topic.\n"
        "2. **Current Advancements** - Highlights significant innovations and findings.\n"
        "3. **Impact on Industries and Communities** - Discusses real-world applications and benefits.\n"
        "4. **Concluding Thoughts** - Summarizes key insights and potential future developments.\n"
        "5. **References** - Lists sources in a structured format.\n\n"
        " PLS DO NOT WRITE ```html at the start or end of the reply pls just dont write that i want the code to directly be run soo dont write that ```html at start and also at the end dont write ``` "
        "AND DONT FORGET TO ADD REFRENCES AND STUFF AND EVERYTHING MUST BE IN DETAILED FORMAT I WANT IT TO BE FULLY CURATED AND DETAILED"
        "The HTML file should include inline CSS for styling headers, sections, and references. Use colors, font sizes, and spacing to make the article visually engaging and easy to read."
    ),
    tools=[search_tool, web_rag_tool,convert_to_html_tool],
    agent=report_generator_agent,
    async_execution=False,
    output_file='generated_article.html'
)


