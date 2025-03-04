from dotenv import load_dotenv
import streamlit as st
import hashlib
from chromadb.utils.embedding_functions.open_clip_embedding_function import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
from chromadb import PersistentClient

# Load environment variables
load_dotenv()

class DatabaseChroma:
    def __init__(self, 
                 collection_name: str = "multimodal_collection",
                 embedding_function: OpenCLIPEmbeddingFunction = OpenCLIPEmbeddingFunction(),
                 data_loaders: ImageLoader = ImageLoader(),
                 client: PersistentClient = PersistentClient(path="./chroma_db")):
        
        self.collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            data_loader=data_loaders
        )

    def add_image(self, image_path: str) -> None:
        """Add image to ChromaDB with SHA-256 hash as ID"""
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            file_hash = hashlib.sha256(image_bytes).hexdigest()
            # Check for existing image
            existing = self.collection.get(ids=[file_hash])
            if existing['ids']:
                st.warning("Image already exists in database!")
                return
            self.collection.add(ids=[file_hash], uris=[image_path])
            st.success("Image added successfully!")      
        except Exception as e:
            st.error(f"Error adding image: {e}")

    def query_image(self, text_query: str) -> str:
        """Query images by text and return top result URI"""
        try:
            results = self.collection.query(
                query_texts=[text_query],
                n_results=1,
                include=['uris']
            )
            return results['uris'][0][0] if results['uris'] else None
        except Exception as e:
            st.error(f"Query error: {e}")
            return None