from pydantic import BaseModel, Field
from typing import Optional, List

class Assessment(BaseModel):
    """Model representing an SHL assessment with test_type as list"""
    url: str = Field(..., description="URL to the assessment")
    name: str = Field(None, description="Name of the assessment")
    adaptive_support: bool = Field(..., description="Whether the assessment supports adaptive testing")
    description: str = Field(..., description="Description of the assessment")
    duration: str = Field(..., description="Estimated duration of the assessment")
    remote_support: bool = Field(..., description="Whether the assessment can be taken remotely")
    test_type: List[str] = Field(..., description="List of test types (e.g., ['Cognitive', 'Personality'])")
    score: Optional[float] = Field(
        None,
        description="Relevance score between 0 and 1",
        ge=0,
        le=1
    )


class Query(BaseModel):
    query: str
    top_k: Optional[int] = 5

class HealthResponse(BaseModel):
    status: str

class RecommendationResponse(BaseModel):
    recommendations: List[Assessment]
