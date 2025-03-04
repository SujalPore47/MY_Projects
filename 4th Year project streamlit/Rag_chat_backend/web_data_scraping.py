from qdrant_client import QdrantClient, models
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain_qdrant import QdrantVectorStore
import os

load_dotenv()

class WebQdrantHandler:
    def __init__(self):
        self.qdrant_client = QdrantClient(
            url="https://57614a40-2110-4eef-bd71-53120bff80a8.europe-west3-0.gcp.cloud.qdrant.io:6333",
            api_key=os.getenv("QUADRANT_API_KEY")
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=40
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
    def get_or_create_qdrant_collection(self,collection_name : str):
        try:
            exists_collection = self.qdrant_client.collection_exists(collection_name)
            if exists_collection==True:
                self.qdrant_client.get_collection(collection_name)
                print(f"Collection {collection_name} already exists")
            else:
                self.qdrant_client.create_collection(
                    collection_name, 
                    vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
                )
                print(f"Collection {collection_name} created successfully")
        except Exception as e:
            print(f"Error creating collection {collection_name}: {e}")
    
    def initialize_vectorstore(self,collection_name : str):
        self.get_or_create_qdrant_collection(collection_name=collection_name)
        vecstore = QdrantVectorStore(
            client=self.qdrant_client, 
            embedding=self.embeddings, 
            collection_name=collection_name
        )
        return vecstore
    
    def load_web_to_qdrant_collection(self, website_link: str, collection_name: str):
        try:
            web_loader = WebBaseLoader(web_path=website_link)
            web_docs = web_loader.load_and_split(text_splitter=self.text_splitter)
            for doc in web_docs:
                doc.metadata = {"source_url": website_link}
            self.initialize_vectorstore(collection_name=collection_name).add_documents(documents=web_docs)
            return {
                "Success": True,
                "Error": None
            }
        except Exception as e:
            return {
                "Success": False,
                "Error": str(e)
            }
# if __name__ == "__main__":
#     WebQdrantHandler().load_web_to_qdrant_collection(website_link="https://www.cricbuzz.com/",collection_name="chat with web app")