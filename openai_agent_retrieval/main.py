import time
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

from config import DEBUG, HOST, PORT
from models import QueryRequest, QueryResponse, HealthResponse
from agent import query_agent

# Initialize logging
logging.basicConfig(level=logging.INFO if not DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="OpenAI Agent with Qdrant Retrieval API",
    description="An API that provides an OpenAI agent with retrieval capabilities from Qdrant vector database",
    version="1.0.0",
    debug=DEBUG
)

# Add CORS middleware - Allow frontend from different port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers that might be needed by the frontend
    expose_headers=["Access-Control-Allow-Origin"]
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return HealthResponse()


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a user query using the OpenAI agent with Qdrant retrieval.

    Args:
        request: QueryRequest containing the user's query and parameters

    Returns:
        QueryResponse with the agent's response and metadata
    """
    start_time = time.time()

    try:
        logger.info(f"Processing query: {request.query}")

        # Process the query with the agent
        result = query_agent(
            query=request.query,
            max_results=request.max_results
        )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Create response object
        response = QueryResponse(
            query=result["query"],
            response=result["response"],
            sources=result["sources"] if request.include_sources else [],
            retrieved_count=result["retrieved_count"],
            processing_time=processing_time
        )

        logger.info(f"Query processed successfully in {processing_time:.2f} seconds")
        return response

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "OpenAI Agent with Qdrant Retrieval API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/query",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    logger.info(f"Starting server on {HOST}:{PORT}")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )