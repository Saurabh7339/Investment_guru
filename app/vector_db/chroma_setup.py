import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import os
import logging

logger = logging.getLogger(__name__)

class ChromaDB:
    def __init__(self, collection_name: str = "investment_docs"):
        # Configure persistent storage directory
        self.persist_directory = "db/chroma"
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
        try:
            if not ids:
                ids = [str(i) for i in range(len(documents))]
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def query(self, query_texts: List[str], n_results: int = 5) -> Dict:
        try:
            return self.collection.query(
                query_texts=query_texts,
                n_results=n_results
            )
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise