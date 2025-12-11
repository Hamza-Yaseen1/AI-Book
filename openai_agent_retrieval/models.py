from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for agent queries"""
    query: str = Field(..., min_length=1, max_length=2000, description="The user's query to process")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results to retrieve from the database")
    include_sources: bool = Field(default=True, description="Whether to include source information in the response")


class RetrievalResult(BaseModel):
    """Model for individual retrieval results"""
    id: str
    text: str
    url: str
    score: float
    timestamp: Optional[float] = None


class QueryResponse(BaseModel):
    """Response model for agent queries"""
    query: str
    response: str
    sources: List[RetrievalResult] = []
    retrieved_count: int = 0
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    service: str = "openai-agent-retrieval"