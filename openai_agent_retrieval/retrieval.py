import logging
from typing import List, Dict, Any
from config import QDRANT_URL, QDRANT_API_KEY, QDRANT_PORT, QDRANT_COLLECTION_NAME
from qdrant_client import QdrantClient
from qdrant_client.http import models
import cohere
from models import RetrievalResult

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    port=QDRANT_PORT
)

# Initialize Cohere client for query embeddings
cohere_api_key = None  # Will be set when needed to avoid errors if not available
try:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    cohere_api_key = os.getenv("COHERE_API_KEY")
    if cohere_api_key:
        co = cohere.Client(cohere_api_key)
    else:
        logger.warning("COHERE_API_KEY not found in environment. Query embedding functionality may be limited.")
        co = None
except ImportError:
    logger.warning("Cohere library not available. Query embedding functionality may be limited.")
    co = None


def generate_query_embedding(query_text: str) -> List[float]:
    """
    Generate embedding for a query text using Cohere API.

    Args:
        query_text: The query text to embed

    Returns:
        Embedding vector for the query
    """
    if not co:
        raise ValueError("Cohere client not available. Please set COHERE_API_KEY environment variable.")

    try:
        response = co.embed(
            texts=[query_text],
            model="embed-multilingual-v2.0",
            input_type="search_query"
        )

        embedding = response.embeddings[0]  # Get the first (and only) embedding
        logger.info(f"Generated query embedding with dimension: {len(embedding)}")
        return embedding

    except Exception as e:
        logger.error(f"Error generating query embedding: {str(e)}")
        raise


def search_similar_chunks(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for similar chunks in Qdrant based on semantic similarity.

    Args:
        query_text: The query text to search for
        top_k: Number of top similar results to return

    Returns:
        List of similar chunks with their metadata
    """
    logger.info(f"Searching for similar chunks to: '{query_text[:50]}...'")

    # Generate embedding for the query
    query_embedding = generate_query_embedding(query_text)

    try:
        # Perform semantic search in Qdrant using query_points method
        search_response = qdrant_client.query_points(
            collection_name=QDRANT_COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
            with_payload=True
        )

        results = []
        for result in search_response.points:
            results.append({
                "id": result.id,
                "text": result.payload.get("text", ""),
                "url": result.payload.get("url", ""),
                "timestamp": result.payload.get("timestamp", ""),
                "score": result.score
            })

        logger.info(f"Found {len(results)} similar chunks")
        return results

    except Exception as e:
        logger.error(f"Error searching for similar chunks: {str(e)}")
        raise


def retrieve_content_tool(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Custom tool for the OpenAI agent to retrieve content from Qdrant.

    Args:
        query: The query to search for in the vector database
        max_results: Maximum number of results to return

    Returns:
        List of retrieved documents with their metadata
    """
    try:
        logger.info(f"Retrieving content for query: {query}")
        raw_results = search_similar_chunks(query, max_results)

        # Convert to dictionary format for OpenAI
        formatted_results = []
        for raw_result in raw_results:
            formatted_results.append({
                "id": raw_result["id"],
                "text": raw_result["text"],
                "url": raw_result["url"],
                "score": raw_result["score"],
                "timestamp": raw_result.get("timestamp")
            })

        logger.info(f"Retrieved {len(formatted_results)} results")
        return formatted_results

    except Exception as e:
        logger.error(f"Error retrieving content: {str(e)}")
        return []


def retrieve_chunks_as_objects(query_text: str, top_k: int = 5) -> List[RetrievalResult]:
    """
    Search for similar chunks and return them as RetrievalResult objects.

    Args:
        query_text: The query text to search for
        top_k: Number of top similar results to return

    Returns:
        List of RetrievalResult objects
    """
    raw_results = search_similar_chunks(query_text, top_k)

    results = []
    for raw_result in raw_results:
        result = RetrievalResult(
            id=raw_result["id"],
            text=raw_result["text"],
            url=raw_result["url"],
            score=raw_result["score"],
            timestamp=raw_result.get("timestamp")
        )
        results.append(result)

    return results