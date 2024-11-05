from crewai import Crew, Process
from agents import  news_writer , report_generator_agent
from task import  write_task , extract_and_generate_task



class NewsPipeline:
    def __init__(self, verbose=True):
        """
        Initialize the NewsPipeline with the Crew configuration.
        """
        self.crew = Crew(
            agents=[news_writer , report_generator_agent],
            tasks=[write_task , extract_and_generate_task],
            process=Process.sequential,
            verbose=verbose
        )

    def search(self, query: str , template):
        # Pass the query as the input topic to the Crew kickoff
        inputs = {'topic': query , 'template' : template}
        result = self.crew.kickoff(inputs=inputs)
        return result
    