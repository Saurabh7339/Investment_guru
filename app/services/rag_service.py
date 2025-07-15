from app.vector_db.chroma_setup import ChromaDB
from app.services.embedding_service import EmbeddingService
from typing import List, Dict
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, CSVLoader, UnstructuredFileLoader
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_db = ChromaDB()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def get_context_for_recommendation(self, client_data: Dict) -> str:
        """Generate a query from client data and retrieve relevant context"""
        try:
            # Create a query based on client profile
            query_parts = [
                f"Investor type: {client_data.get('investor_type', '')}",
                f"Risk tolerance: {client_data.get('risk_tolerance', '')}",
                f"Investment horizon: {client_data.get('investment_horizon', '')}",
                f"Goals: {client_data.get('investment_goals', '')}",
                f"Current holdings: {', '.join(client_data.get('portfolio', []))}"
            ]
            query = " ".join(query_parts)
            
            # Retrieve relevant documents
            results = self.vector_db.query(query_texts=[query], n_results=3)
            
            # Format the context
            context = "\n\n".join([
                f"Source: {metadata['source']}\nContent: {document}"
                for document, metadata in zip(results['documents'][0], results['metadatas'][0])
            ])
            
            return context
        
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return "No relevant context found"

    def load_documents(self, file_path: str):
        try:
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith('.csv'):
                loader = CSVLoader(file_path)
            else:
                loader = UnstructuredFileLoader(file_path)
            return loader.load()
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            return []

    def process_and_store_documents(self, file_paths: List[str]):
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
            
            try:
                docs = self.load_documents(file_path)
                if not docs:
                    continue
                    
                split_docs = self.text_splitter.split_documents(docs)
                
                documents = [doc.page_content for doc in split_docs]
                metadatas = [{"source": file_path} for _ in split_docs]
                
                self.vector_db.add_documents(
                    documents=documents,
                    metadatas=metadatas
                )
                logger.info(f"Successfully processed {file_path}")
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                continue

    # ... rest of your methods remain the same ...