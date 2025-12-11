import logging
import json
import asyncio
from typing import Dict, Any, List
from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv
from config import OPENAI_API_KEY  # Ensure the key is loaded from your .env file
from retrieval import retrieve_chunks_as_objects
from models import RetrievalResult

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
if OPENAI_API_KEY.startswith("sk-or-"):
    logger.info("Detected OpenRouter API key, using OpenRouter base URL")
    import httpx
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        http_client=httpx.Client()
    )
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

def retrieve_content_tool(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Custom tool for the OpenAI agent to retrieve content from Qdrant.
    """
    try:
        logger.info(f"Retrieving content for query: {query}")
        results = retrieve_chunks_as_objects(query, max_results)

        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "text": result.text,
                "url": result.url,
                "score": result.score,
                "timestamp": result.timestamp
            })

        logger.info(f"Retrieved {len(formatted_results)} results")
        return formatted_results

    except Exception as e:
        logger.error(f"Error retrieving content: {str(e)}")
        return []


def query_agent(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Query the OpenAI agent with retrieval-augmented generation.
    """
    try:
        logger.info(f"Processing query: {query}")
        retrieval_results = retrieve_content_tool(query, max_results)

        context_str = ""
        if retrieval_results:
            context_str = "Relevant information found:\n\n"
            for i, result in enumerate(retrieval_results, 1):
                context_str += f"Document {i} (Score: {result['score']:.3f}, Source: {result['url']}):\n"
                context_str += f"{result['text']}\n\n"
        else:
            context_str = "No relevant documents found in the knowledge base.\n\n"

        full_prompt = f"""
        Please answer the following query based on the provided context:

        Context:
        {context_str}

        Query: {query}

        Please provide a helpful and accurate response based on the context. If the context doesn't contain relevant information, please say so. Include source URLs when referencing specific documents.
        """

        # Call the OpenAI API with the modern client
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using gpt-3.5-turbo; change to gpt-4 if preferred
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided context. When referencing specific documents, include their source URLs."
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Extract the response
        agent_response = response.choices[0].message.content

        # Format the results as RetrievalResult objects for the response
        sources = []
        for result in retrieval_results:
            sources.append(RetrievalResult(
                id=result['id'],
                text=result['text'][:200] + "..." if len(result['text']) > 200 else result['text'],
                url=result['url'],
                score=result['score'],
                timestamp=result.get('timestamp')
            ))

        result = {
            "query": query,
            "response": agent_response,
            "sources": sources,
            "retrieved_count": len(retrieval_results)
        }

        logger.info(f"Agent processed query successfully")
        return result

    except Exception as e:
        logger.error(f"Error querying agent: {str(e)}")
        raise
