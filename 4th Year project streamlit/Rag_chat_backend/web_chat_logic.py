import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from Rag_chat_backend.web_data_scraping import WebQdrantHandler
from operator import itemgetter

class WEBQA:
    def __init__(self, model_name="gemini-1.5-flash-002", collection_name="chat with web app"):
        """Initialize the chatbot with model and database handler."""
        load_dotenv()
        self.collection_name = collection_name
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.5
        )
        self.web_db = WebQdrantHandler()
        self.prompt = self._create_prompt()
        self.chain = self._create_chain()

    def _create_prompt(self):
        """Define and return the prompt template."""
        prompt = ChatPromptTemplate.from_messages([
            ("human", """You are an AI assistant designed to answer questions using only the information provided in the document context. Please adhere to the following guidelines:
                    1. **Explanatory and Detailed**: When the answer is found in the context, provide a thorough and detailed explanation that shows how you derived your answer, including any relevant details or references from the text. Avoid overly brief or TLDR responses.
                    2. **Context-Driven Response**: Ensure that your answer is completely based on the context. If the context supports multiple points, include those details to build a comprehensive answer.
                    3. **Unavailable Information**: If the answer is not present in the context, respond exactly with: "I don’t know based on the provided document."
                    4. **Relevance Check**: If the question is unrelated to the document's content, reply with: "Please ask questions related to the document content."
                    5. **No Fabrication**: Do not add or infer any information that is not present in the provided context.
                    Inputs:
                    - **Question**: {question}
                    - **Context**: {context}
                    - **Chat History**: {chat_history}
                    Answer:"""),
            ])
        return prompt
    
    def _create_chain(self):
        """Create and return the query chain."""
        return ({
            "context": RunnablePassthrough(),
            "question": RunnablePassthrough(),
            "chat_history":RunnablePassthrough(),
        } | RunnableParallel({
            "response": self.prompt | self.model | StrOutputParser(),
            "context": itemgetter("context")
        }))
    
    def initialize_vector_store(self):
        """Initialize the vector store with the given collection name."""
        return self.web_db.initialize_vectorstore(collection_name=self.collection_name)

    def get_answer_and_doc(self, question: str,chat_history:str):
        """Retrieve relevant context and generate an answer."""
        if chat_history:
            response = self.chain.invoke({"question": question,"context": self.initialize_vector_store().as_retriever(search_type="mmr", search_kwargs={'k': 5}).invoke(input=question),"chat_history":chat_history})
        else:
            response = self.chain.invoke({"question": question,"context": self.initialize_vector_store().as_retriever(search_type="mmr", search_kwargs={'k': 2}).invoke(input=question)})
        return {
        'answer' : response['response'],
        'context': response['context']['context']
        }
    
    def async_get_answer_and_docs(self,question: str,chat_history: str):
        """Retrieve relevant context and generate an answer asynchronously."""
        return self.chain.stream({"question": question,"context": self.initialize_vector_store().as_retriever(search_type="mmr", search_kwargs={'k': 2}).invoke(input=question),"chat_history":chat_history})

    # async def async_get_answer_and_docs(self,question: str,chat_history: str):
    #     async for event in self.chain.astream_events({"question": question,"context": self.initialize_vector_store().as_retriever(search_type="mmr", search_kwargs={'k': 2}).invoke(input=question),"chat_history":chat_history},version="v1"):
    #         event_type = event['event']
    #         if event_type == "on_retriever_end":
    #             yield {
    #                 "event_type": event_type,
    #                 "content": [doc.dict() for doc in event['data']['output']['documents']]
    #             }
    #         elif event_type == "on_chat_model_stream":
    #             yield {
    #                 "event_type": event_type,
    #                 "content": event['data']['chunk'].content
    #             }
        
    #     yield {
    #         "event_type": "done"
    #     }
# if __name__ == "__main__":
#     print(WEBQA().get_answer_and_doc(question="England tour of India",chat_history="None for now"))