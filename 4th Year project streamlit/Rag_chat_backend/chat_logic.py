import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from Rag_chat_backend.vector_database_logic import QdrantHandler
from operator import itemgetter

class PDFQA:
    def __init__(self, model_name="gemini-1.5-flash-002", collection_name="chat with pdf app"):
        """Initialize the chatbot with model and database handler."""
        load_dotenv()
        self.collection_name = collection_name
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            api_key=os.getenv("GOOGLE_API_KEY"),
            streaming=True
        )
        self.db = QdrantHandler()
        self.prompt = self._create_prompt()
        self.chain = self._create_chain()

    def _create_prompt(self):
        """Define and return the prompt template."""
        prompt = ChatPromptTemplate.from_messages([
            ("human", """You are an AI assistant for question-answering tasks. Use only the provided retrieved context to answer the user's question.  
                        - If the answer is present in the context, provide a **concise** response in **seven sentences or less**.  
                        - If the answer is **not found**, say: *"I don’t know based on the provided document."*  
                        - If the question is **irrelevant to the document**, respond: *"Please ask questions related to the document content."*  
                        - Do **not** make up answers or provide information beyond the retrieved context.
            Question: {question} 
            Context: {context}
            chat_history:{chat_history} 
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
        return self.db.initialize_vectorstore(collection_name=self.collection_name)

    def get_answer_and_doc(self, question: str,chat_history:str):
        """Retrieve relevant context and generate an answer."""
        if chat_history:
            response = self.chain.invoke({"question": question,"context": self.initialize_vector_store().as_retriever(search_type="mmr", search_kwargs={'k': 2}).invoke(input=question),"chat_history":chat_history})
        else:
            response = self.chain.invoke({"question": question,"context": self.initialize_vector_store().as_retriever(search_type="mmr", search_kwargs={'k': 2}).invoke(input=question)})
        return {
        'answer' : response['response'],
        'context': response['context']['context']
        }
    
    def async_get_answer_and_docs(self,question: str,chat_history: str):
        """Retrieve relevant context and generate an answer asynchronously."""
        return self.chain.stream({"question": question,"context": self.initialize_vector_store().as_retriever(search_type="mmr", search_kwargs={'k': 2}).invoke(input=question),"chat_history":chat_history})