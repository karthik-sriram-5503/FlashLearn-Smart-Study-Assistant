import os
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

class EmbeddingStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
    def create_vector_store(self, documents):
        """Create a vector store from documents."""
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return vector_store
    
    def get_retriever(self):
        """Get a retriever for the vector store."""
        try:
            vector_store = Chroma(
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            return vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 3})
        except Exception as e:
            print(f"Error initializing vector store: {e}")
            return None