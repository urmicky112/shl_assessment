import chromadb
from chromadb.utils import embedding_functions
from typing import List
from app.models import Assessment
import json
import os
from pathlib import Path
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class VectorDB:
    """ChromaDB wrapper for storing and retrieving SHL assessment embeddings"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_db_path)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="shl_assessments",
            embedding_function=self.embedding_function,
            metadata={
                "hnsw:space": "cosine",
                "hnsw:construction_ef": 100,
                "hnsw:M": 16,
                "hnsw:search_ef": 10,
                "hnsw:num_threads": 4,
                "hnsw:resize_factor": 1.2,
                "hnsw:batch_size": 100,
                "hnsw:sync_threshold": 1000
            }  # Using cosine similarity
        )
        
        # Initialize with data if empty
        if self.collection.count() == 0:
            self._initialize_data()

    def _initialize_data(self):
        """Load initial SHL assessments data into ChromaDB with list support"""
        try:
            data_path = Path(__file__).parent.parent / "data" / "shl_assessments.json"
            with open(data_path, "r") as f:
                assessments = json.load(f)
            
            if not assessments:
                raise ValueError("No assessments found in the data file")
            
            ids = []
            documents = []
            metadatas = []
            
            for idx, assessment in enumerate(assessments):
                # Serialize list fields to strings
                test_type = assessment.get('test_type', [])
                if isinstance(test_type, list):
                    test_type = ",".join(test_type)  # Convert list to comma-separated string
                elif not isinstance(test_type, str):
                    test_type = str(test_type)
                
                # Prepare metadata with list support
                metadata = {
                    "url": assessment['url'],
                    "name": assessment.get('name', ''),
                    "adaptive_support": assessment['adaptive_support'],
                    "description": assessment['description'],
                    "duration": assessment['duration'],
                    "remote_support": assessment['remote_support'],
                    "test_type": test_type,  # Now stored as list
                    "keywords": assessment.get('keywords', '')
                }
                
                # Create document text for embedding
                document_text = (
                    f"SHL Assessment: {metadata['description']}\n"
                    f"Name: {metadata['name']}\n"
                    f"Types: {', '.join(test_type)}\n"
                    f"Duration: {metadata['duration']}\n"
                    f"Remote: {'Yes' if metadata['remote_support'] else 'No'}\n"
                    f"Adaptive: {'Yes' if metadata['adaptive_support'] else 'No'}"
                )
                
                ids.append(f"id{idx}")
                documents.append(document_text)
                metadatas.append(metadata)
            
            # Batch add to ChromaDB
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Successfully loaded {len(assessments)} assessments into ChromaDB")
            
        except Exception as e:
            logger.error(f"Failed to initialize data: {str(e)}")
            raise

    def _create_document_text(self, assessment: dict) -> str:
        """Create a text representation of an assessment for embedding"""
        return (
            f"SHL Assessment: {assessment.get('description', '')}\n"
            f"Type: {assessment.get('test_type', '')[0]}\n"
            f"Duration: {assessment.get('duration', '')}\n"
            f"Remote Supported: {'Yes' if assessment.get('remote_support', False) else 'No'}\n"
            f"Adaptive: {'Yes' if assessment.get('adaptive_support', False) else 'No'}\n"
            f"Keywords: {assessment.get('keywords', '')}"
        )        
    
    def search(self, query: str, top_k: int = 6) -> List[Assessment]:
        """
        Search for relevant assessments based on query
        
        Args:
            query: Search query or job description
            top_k: Number of results to return
            
        Returns:
            List of Assessment objects with relevance scores
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["metadatas", "distances"]
        )
        
        assessments = []
        for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
            try:
                # Convert test_type to list if it's stored as string in ChromaDB
                test_type = metadata['test_type']
                if isinstance(test_type, str):
                    test_type = [t.strip() for t in test_type.split(",")]
                
                assessment = Assessment(
                    url=metadata['url'],
                    name=metadata.get('name'),
                    adaptive_support=metadata['adaptive_support'],
                    description=metadata['description'],
                    duration=metadata['duration'],
                    remote_support=metadata['remote_support'],
                    test_type=test_type,
                    score=1 - distance  # Convert to similarity score
                )
                assessments.append(assessment)
            except Exception as e:
                logging.warning(f"Failed to parse assessment metadata: {str(e)}")
        
        return sorted(assessments, key=lambda x: x.score, reverse=True)