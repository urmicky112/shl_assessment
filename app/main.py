from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from app.models import HealthResponse, RecommendationResponse, Query
from app.database import VectorDB
from app.llm import GeminiProcessor
from app.utils import extract_text_from_url
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SHL Assessment Recommender",
    description="RAG system for recommending SHL assessments based on job descriptions",
    version="1.0.0"
)

# CORS middleware setup
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
vector_db = VectorDB()
gemini_processor = GeminiProcessor()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_assessments(query: Query):
    try:
        # Step 1: Get relevant assessments from vector DB
        double_k = min(20, 2 * query.top_k)  # Cap at 20 to avoid too many LLM calls
        relevant_docs = vector_db.search(query.query, top_k=double_k)
        
        # Step 2: Process with LLM to refine results
        refined_results = gemini_processor.refine_recommendations(
            query=query.query,
            assessments=relevant_docs
        )
        
        return {"recommendations": refined_results}
    
    except Exception as e:
        logging.error(f"Error in recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)