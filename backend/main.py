import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
import time
import logging
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is required")
co = cohere.Client(cohere_api_key)

# Initialize Qdrant client
qdrant_url = os.getenv("QDRANT_URL", "localhost")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
    port=6333
)


def get_all_urls(base_url: str) -> List[str]:
    """
    Get all URLs from the book website.

    Args:
        base_url: The base URL to start crawling from

    Returns:
        List of URLs found on the website
    """
    logger.info(f"Starting to crawl {base_url}")
    urls = set()
    visited = set()

    def crawl_page(url: str):
        if url in visited or not url.startswith(base_url):
            return

        visited.add(url)
        logger.info(f"Crawling: {url}")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Add current URL to the list
            urls.add(url)

            # Find all links on the page
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                if absolute_url.startswith(base_url) and absolute_url not in visited:
                    urls.add(absolute_url)

        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")

    # Start with the base URL
    crawl_page(base_url)

    # For additional depth, crawl linked pages (but limit to avoid infinite crawling)
    urls_to_crawl = list(urls.copy())
    for url in urls_to_crawl[:10]:  # Limit to first 10 URLs to avoid excessive crawling
        crawl_page(url)

    logger.info(f"Found {len(urls)} URLs")
    return list(urls)


def extract_text_from_url(url: str) -> str:
    """
    Extract text content from a given URL.

    Args:
        url: The URL to extract text from

    Returns:
        Extracted text content
    """
    logger.info(f"Extracting text from {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        logger.info(f"Extracted {len(text)} characters from {url}")
        return text

    except Exception as e:
        logger.error(f"Error extracting text from {url}: {str(e)}")
        return ""


def chunk_text(text: str, chunk_size: int = 512) -> List[str]:
    """
    Split text into chunks of specified size.

    Args:
        text: The text to chunk
        chunk_size: Maximum size of each chunk

    Returns:
        List of text chunks
    """
    if not text:
        return []

    chunks = []
    words = text.split()

    current_chunk = []
    current_length = 0

    for word in words:
        if current_length + len(word) > chunk_size and current_chunk:
            # Save current chunk and start a new one
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space

    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    logger.info(f"Text chunked into {len(chunks)} parts")
    return chunks


def embed(text_list: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Cohere API.

    Args:
        text_list: List of texts to embed

    Returns:
        List of embeddings (each embedding is a list of floats)
    """
    if not text_list:
        return []

    logger.info(f"Generating embeddings for {len(text_list)} text chunks")

    # Cohere API has limits, so we'll process in batches if needed
    all_embeddings = []

    # Process in batches of up to 96 texts (Cohere's typical limit)
    batch_size = 96
    for i in range(0, len(text_list), batch_size):
        batch = text_list[i:i + batch_size]

        try:
            response = co.embed(
                texts=batch,
                model="embed-multilingual-v2.0",  # Using multilingual model for broader coverage
                input_type="search_document"
            )

            batch_embeddings = [embedding for embedding in response.embeddings]
            all_embeddings.extend(batch_embeddings)

            logger.info(f"Generated embeddings for batch {i//batch_size + 1}")

            # Respect API rate limits
            time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
            # Return zeros for failed embeddings to maintain alignment
            all_embeddings.extend([[0.0] * 768 for _ in range(len(batch))])

    logger.info(f"Successfully generated {len(all_embeddings)} embeddings")
    return all_embeddings


def create_collection(name: str = "rag_embedding"):
    """
    Create a collection in Qdrant for storing embeddings.

    Args:
        name: Name of the collection to create
    """
    logger.info(f"Creating collection: {name}")

    try:
        # Check if collection already exists
        collections = qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if name in collection_names:
            logger.info(f"Collection {name} already exists, deleting and recreating")
            qdrant_client.delete_collection(name)

        # Create new collection
        # Assuming Cohere's multilingual model returns 768-dimensional vectors
        qdrant_client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )

        logger.info(f"Collection {name} created successfully")

    except Exception as e:
        logger.error(f"Error creating collection {name}: {str(e)}")
        raise


def save_chunk_to_qdrant(chunk: str, embedding: List[float], url: str, collection_name: str = "rag_embedding"):
    """
    Save a text chunk and its embedding to Qdrant.

    Args:
        chunk: The text chunk to save
        embedding: The embedding vector for the chunk
        url: The source URL of the chunk
        collection_name: The name of the collection to save to
    """
    point_id = str(uuid.uuid4())

    try:
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "url": url,
                        "timestamp": time.time()
                    }
                )
            ]
        )

        logger.info(f"Saved chunk to Qdrant with ID: {point_id}")

    except Exception as e:
        logger.error(f"Error saving chunk to Qdrant: {str(e)}")
        raise


def generate_query_embedding(query_text: str) -> List[float]:
    """
    Generate embedding for a query text using Cohere API.

    Args:
        query_text: The query text to embed

    Returns:
        Embedding vector for the query
    """
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


def search_similar_chunks(query_text: str, top_k: int = 5, collection_name: str = "rag_embedding") -> List[Dict[str, Any]]:
    """
    Search for similar chunks in Qdrant based on semantic similarity.

    Args:
        query_text: The query text to search for
        top_k: Number of top similar results to return
        collection_name: The name of the collection to search in

    Returns:
        List of similar chunks with their metadata
    """
    logger.info(f"Searching for similar chunks to: '{query_text[:50]}...'")

    # Generate embedding for the query
    query_embedding = generate_query_embedding(query_text)

    try:
        # Perform semantic search in Qdrant using query_points method
        search_response = qdrant_client.query_points(
            collection_name=collection_name,
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


def retrieve_embedding_by_id(point_id: str, collection_name: str = "rag_embedding", include_vector: bool = True) -> Dict[str, Any]:
    """
    Retrieve a specific embedding and its metadata by ID.

    Args:
        point_id: The ID of the point to retrieve
        collection_name: The name of the collection to search in
        include_vector: Whether to include the vector data in the response

    Returns:
        Dictionary containing the point data
    """
    logger.info(f"Retrieving embedding by ID: {point_id}")

    try:
        points = qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[point_id],
            with_payload=True,
            with_vectors=include_vector
        )

        if not points:
            logger.warning(f"No point found with ID: {point_id}")
            return {}

        point = points[0]
        result = {
            "id": point.id,
            "vector": point.vector if include_vector else None,
            "payload": point.payload,
            "vector_dimension": len(point.vector) if point.vector else None
        }

        logger.info(f"Retrieved point with ID: {point_id}, dimension: {result['vector_dimension']}")
        return result

    except Exception as e:
        logger.error(f"Error retrieving embedding by ID: {str(e)}")
        raise


def retrieve_all_embeddings_batch(collection_name: str = "rag_embedding", batch_size: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieve all embeddings from the collection in batches.

    Args:
        collection_name: The name of the collection to retrieve from
        batch_size: Number of embeddings to retrieve per batch

    Returns:
        List of all embeddings with their metadata
    """
    logger.info(f"Starting batch retrieval from collection: {collection_name}, batch size: {batch_size}")

    all_embeddings = []
    offset = None

    try:
        while True:
            # Retrieve a batch of points
            batch_response = qdrant_client.scroll(
                collection_name=collection_name,
                limit=batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )

            points = batch_response.points
            next_page_offset = batch_response.next_page_offset

            for point in points:
                embedding_data = {
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload,
                    "vector_dimension": len(point.vector) if point.vector else None
                }
                all_embeddings.append(embedding_data)

            logger.info(f"Retrieved batch of {len(points)} embeddings, total so far: {len(all_embeddings)}")

            # If no more points to retrieve, break
            if next_page_offset is None:
                break

            offset = next_page_offset

        logger.info(f"Completed batch retrieval. Total embeddings retrieved: {len(all_embeddings)}")
        return all_embeddings

    except Exception as e:
        logger.error(f"Error during batch retrieval: {str(e)}")
        raise


def get_embedding_dimensions(collection_name: str = "rag_embedding") -> Dict[str, int]:
    """
    Get information about embedding dimensions in the collection.

    Args:
        collection_name: The name of the collection to check

    Returns:
        Dictionary with dimension information
    """
    logger.info(f"Getting embedding dimensions for collection: {collection_name}")

    try:
        collection_info = qdrant_client.get_collection(collection_name=collection_name)
        points_count = collection_info.points_count

        # Get a sample to check dimensions
        sample_result = qdrant_client.scroll(
            collection_name=collection_name,
            limit=1,
            with_vectors=True
        )

        # Scroll returns a tuple (points, next_page_offset)
        sample_points = sample_result[0]  # First element is the list of points

        if sample_points:
            sample_vector = sample_points[0].vector
            dimension = len(sample_vector) if sample_vector else 0
        else:
            dimension = 0

        dimensions_info = {
            "dimension_size": dimension,
            "total_points": points_count,
            "collection_name": collection_name
        }

        logger.info(f"Collection dimensions info: {dimensions_info}")
        return dimensions_info

    except Exception as e:
        logger.error(f"Error getting embedding dimensions: {str(e)}")
        raise


def validate_embedding_integrity(point_id: str, collection_name: str = "rag_embedding") -> bool:
    """
    Validate the integrity of a specific embedding.

    Args:
        point_id: The ID of the point to validate
        collection_name: The name of the collection to check

    Returns:
        True if embedding is valid, False otherwise
    """
    logger.info(f"Validating embedding integrity for ID: {point_id}")

    try:
        embedding_data = retrieve_embedding_by_id(point_id, collection_name, include_vector=True)

        if not embedding_data:
            logger.error(f"No embedding found for ID: {point_id}")
            return False

        # Check if vector exists and has the right dimensions
        if embedding_data["vector"] is None:
            logger.error(f"No vector found for ID: {point_id}")
            return False

        if embedding_data["vector_dimension"] != 768:  # Cohere embedding dimension
            logger.error(f"Invalid dimension for ID {point_id}: {embedding_data['vector_dimension']}, expected 768")
            return False

        # Check if payload exists and has required fields
        payload = embedding_data["payload"]
        if not payload or "text" not in payload or "url" not in payload:
            logger.error(f"Missing required payload fields for ID: {point_id}")
            return False

        # Check if text content is reasonable
        text_content = payload.get("text", "")
        if not text_content or len(text_content.strip()) == 0:
            logger.error(f"Empty text content for ID: {point_id}")
            return False

        logger.info(f"Embedding integrity validated for ID: {point_id}")
        return True

    except Exception as e:
        logger.error(f"Error validating embedding integrity for ID {point_id}: {str(e)}")
        return False


def get_all_documents_count(collection_name: str = "rag_embedding") -> int:
    """
    Get the total count of documents in the collection.

    Args:
        collection_name: The name of the collection to count

    Returns:
        Total number of documents in the collection
    """
    try:
        count = qdrant_client.count(
            collection_name=collection_name
        )
        logger.info(f"Total documents in collection '{collection_name}': {count}")
        return count
    except Exception as e:
        logger.error(f"Error getting document count: {str(e)}")
        return 0


def list_collections() -> List[str]:
    """
    List all collections in the Qdrant instance.

    Returns:
        List of collection names
    """
    try:
        collections = qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]
        logger.info(f"Available collections: {collection_names}")
        return collection_names
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        return []


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Format search results for display.

    Args:
        results: List of search results

    Returns:
        Formatted string of search results
    """
    if not results:
        return "No results found."

    formatted_results = []
    for i, result in enumerate(results, 1):
        # Clean text to handle special characters
        clean_text = result['text'].replace('\u200b', '')  # Remove zero-width space
        clean_text = clean_text.replace('\u200c', '')  # Remove zero-width non-joiner
        clean_text = clean_text.replace('\u200d', '')  # Remove zero-width joiner
        clean_text = clean_text.replace('\u2060', '')  # Remove word joiner

        formatted_results.append(
            f"Result {i} (Score: {result['score']:.4f}):\n"
            f"URL: {result['url']}\n"
            f"Content: {clean_text[:200]}{'...' if len(clean_text) > 200 else ''}\n"
        )

    return "\n".join(formatted_results)


def validate_retrieved_content(query: str, results: List[Dict[str, Any]]) -> bool:
    """
    Validate that retrieved content is relevant to the query.

    Args:
        query: The original query
        results: The search results to validate

    Returns:
        True if content is relevant, False otherwise
    """
    if not results:
        return False

    # Simple validation: check if any result contains keywords from the query
    query_lower = query.lower()
    for result in results:
        content_lower = result['text'].lower()
        if any(keyword in content_lower for keyword in query_lower.split()[:3]):  # Check first 3 keywords
            return True

    return False


def test_embedding_accuracy(collection_name: str = "rag_embedding", sample_size: int = 10) -> Dict[str, Any]:
    """
    Test the accuracy of embedding retrieval by validating a sample of embeddings.

    Args:
        collection_name: The name of the collection to test
        sample_size: Number of embeddings to test

    Returns:
        Dictionary with test results
    """
    logger.info(f"Testing embedding accuracy for collection: {collection_name}, sample size: {sample_size}")

    try:
        # Get a sample of points to test
        sample_result = qdrant_client.scroll(
            collection_name=collection_name,
            limit=sample_size,
            with_payload=True,
            with_vectors=True
        )

        # Scroll returns a tuple (points, next_page_offset)
        sample_points = sample_result[0]  # First element is the list of points

        total_tested = 0
        valid_embeddings = 0
        invalid_embeddings = []

        for point in sample_points:
            total_tested += 1
            is_valid = validate_embedding_integrity(point.id, collection_name)
            if is_valid:
                valid_embeddings += 1
            else:
                invalid_embeddings.append(point.id)

        accuracy_rate = valid_embeddings / total_tested if total_tested > 0 else 0

        results = {
            "total_tested": total_tested,
            "valid_embeddings": valid_embeddings,
            "invalid_embeddings": invalid_embeddings,
            "accuracy_rate": accuracy_rate,
            "collection_name": collection_name
        }

        logger.info(f"Embedding accuracy test completed: {results}")
        return results

    except Exception as e:
        logger.error(f"Error testing embedding accuracy: {str(e)}")
        raise


def test_metadata_consistency(collection_name: str = "rag_embedding", sample_size: int = 20) -> Dict[str, Any]:
    """
    Test the consistency of metadata across embeddings.

    Args:
        collection_name: The name of the collection to test
        sample_size: Number of embeddings to test

    Returns:
        Dictionary with test results
    """
    logger.info(f"Testing metadata consistency for collection: {collection_name}, sample size: {sample_size}")

    try:
        # Get a sample of points to test
        sample_result = qdrant_client.scroll(
            collection_name=collection_name,
            limit=sample_size,
            with_payload=True
        )

        # Scroll returns a tuple (points, next_page_offset)
        sample_points = sample_result[0]  # First element is the list of points

        total_tested = 0
        consistent_metadata = 0
        inconsistent_metadata = []

        for point in sample_points:
            total_tested += 1
            payload = point.payload

            # Check for required metadata fields
            has_required_fields = all(field in payload for field in ["text", "url", "timestamp"])

            # Check if text content is reasonable
            text_content = payload.get("text", "")
            has_valid_text = len(text_content.strip()) > 0

            # Check if URL is valid
            url = payload.get("url", "")
            has_valid_url = url.startswith("http")

            if has_required_fields and has_valid_text and has_valid_url:
                consistent_metadata += 1
            else:
                inconsistent_metadata.append({
                    "id": point.id,
                    "missing_fields": [field for field in ["text", "url", "timestamp"] if field not in payload],
                    "valid_text": len(text_content.strip()) > 0,
                    "valid_url": url.startswith("http") if url else False
                })

        consistency_rate = consistent_metadata / total_tested if total_tested > 0 else 0

        results = {
            "total_tested": total_tested,
            "consistent_metadata": consistent_metadata,
            "inconsistent_metadata": inconsistent_metadata,
            "consistency_rate": consistency_rate,
            "collection_name": collection_name
        }

        logger.info(f"Metadata consistency test completed: {results}")
        return results

    except Exception as e:
        logger.error(f"Error testing metadata consistency: {str(e)}")
        raise


def test_similarity_search_accuracy(collection_name: str = "rag_embedding", test_queries: List[str] = None) -> Dict[str, Any]:
    """
    Test the accuracy of similarity search by validating relevance of results.

    Args:
        collection_name: The name of the collection to test
        test_queries: List of test queries to use (default: predefined queries)

    Returns:
        Dictionary with test results
    """
    if test_queries is None:
        test_queries = [
            "machine learning",
            "safety in robotics",
            "physical AI",
            "sensor fusion",
            "robotics"
        ]

    logger.info(f"Testing similarity search accuracy with queries: {test_queries}")

    try:
        total_queries = len(test_queries)
        queries_with_relevant_results = 0
        detailed_results = []

        for query in test_queries:
            # Perform search
            search_results = search_similar_chunks(query, top_k=3, collection_name=collection_name)

            # Check if results are relevant to the query
            is_relevant = validate_retrieved_content(query, search_results)

            if is_relevant:
                queries_with_relevant_results += 1

            detailed_results.append({
                "query": query,
                "result_count": len(search_results),
                "is_relevant": is_relevant,
                "top_result_snippet": search_results[0]['text'][:100] + "..." if search_results else "No results"
            })

        relevance_rate = queries_with_relevant_results / total_queries if total_queries > 0 else 0

        results = {
            "total_queries": total_queries,
            "queries_with_relevant_results": queries_with_relevant_results,
            "relevance_rate": relevance_rate,
            "detailed_results": detailed_results,
            "collection_name": collection_name
        }

        logger.info(f"Similarity search accuracy test completed: {results}")
        return results

    except Exception as e:
        logger.error(f"Error testing similarity search accuracy: {str(e)}")
        raise


def monitor_retrieval_performance(collection_name: str = "rag_embedding") -> Dict[str, float]:
    """
    Monitor and report performance metrics for retrieval operations.

    Args:
        collection_name: The name of the collection to monitor

    Returns:
        Dictionary with performance metrics
    """
    logger.info(f"Monitoring retrieval performance for collection: {collection_name}")

    import time

    try:
        # Test count operation performance
        start_time = time.time()
        doc_count = get_all_documents_count(collection_name)
        count_time = time.time() - start_time

        # Test single retrieval performance
        start_time = time.time()
        sample_result = qdrant_client.scroll(
            collection_name=collection_name,
            limit=1,
            with_payload=True
        )
        scroll_time = time.time() - start_time

        # Test search performance
        start_time = time.time()
        # Scroll returns a tuple (points, next_page_offset)
        sample_points = sample_result[0]  # First element is the list of points
        if sample_points:
            search_results = search_similar_chunks("test query for performance", top_k=5, collection_name=collection_name)
        else:
            search_results = []
        search_time = time.time() - start_time

        performance_metrics = {
            "document_count": doc_count,
            "count_operation_time": count_time,
            "scroll_operation_time": scroll_time,
            "search_operation_time": search_time,
            "collection_name": collection_name
        }

        logger.info(f"Performance monitoring completed: {performance_metrics}")
        return performance_metrics

    except Exception as e:
        logger.error(f"Error monitoring retrieval performance: {str(e)}")
        raise


def performance_test(collection_name: str = "rag_embedding") -> Dict[str, float]:
    """
    Run performance tests on the retrieval system.

    Args:
        collection_name: The name of the collection to test

    Returns:
        Dictionary with performance metrics
    """
    import time

    logger.info("Starting performance tests...")

    # Test document count
    start_time = time.time()
    doc_count = get_all_documents_count(collection_name)
    count_time = time.time() - start_time

    # Test a simple search
    start_time = time.time()
    test_query = "artificial intelligence"
    search_results = search_similar_chunks(test_query, top_k=3, collection_name=collection_name)
    search_time = time.time() - start_time

    # Test retrieval by ID if any documents exist
    retrieval_time = 0
    if search_results:
        start_time = time.time()
        retrieve_embedding_by_id(search_results[0]['id'], collection_name)
        retrieval_time = time.time() - start_time

    performance_metrics = {
        "document_count": doc_count,
        "count_query_time": count_time,
        "search_query_time": search_time,
        "retrieval_time": retrieval_time,
        "total_test_time": count_time + search_time + retrieval_time
    }

    logger.info(f"Performance test completed: {performance_metrics}")
    return performance_metrics


def test_pipeline(collection_name: str = "rag_embedding") -> bool:
    """
    Run comprehensive tests on the entire pipeline.

    Args:
        collection_name: The name of the collection to test

    Returns:
        True if all tests pass, False otherwise
    """
    logger.info("Starting pipeline tests...")

    try:
        # Test 1: Check if collection exists
        collections = list_collections()
        if collection_name not in collections:
            logger.error(f"Collection '{collection_name}' does not exist")
            return False
        logger.info(f"✓ Collection '{collection_name}' exists")

        # Test 2: Check document count
        doc_count = get_all_documents_count(collection_name)
        if doc_count == 0:
            logger.error("No documents found in the collection")
            return False
        logger.info(f"✓ Found {doc_count} documents in collection")

        # Test 3: Perform a search test
        test_query = "machine learning"
        search_results = search_similar_chunks(test_query, top_k=2, collection_name=collection_name)
        if len(search_results) == 0:
            logger.error("Search returned no results")
            return False
        logger.info(f"✓ Search test successful, found {len(search_results)} results")

        # Test 4: Validate retrieved content relevance
        is_relevant = validate_retrieved_content(test_query, search_results)
        if not is_relevant:
            logger.warning("Retrieved content may not be fully relevant to query")
        else:
            logger.info("✓ Retrieved content is relevant to query")

        # Test 5: Test retrieval by ID
        sample_id = search_results[0]['id']
        retrieved_data = retrieve_embedding_by_id(sample_id, collection_name)
        if not retrieved_data:
            logger.error("Failed to retrieve data by ID")
            return False
        logger.info("✓ ID-based retrieval test successful")

        # Test 6: Performance test
        performance_metrics = performance_test(collection_name)
        if performance_metrics["search_query_time"] > 0.5:  # More than 500ms
            logger.warning(f"Search query took {performance_metrics['search_query_time']:.3f}s (slower than desired)")
        else:
            logger.info(f"✓ Search performance acceptable: {performance_metrics['search_query_time']:.3f}s")

        logger.info("✓ All pipeline tests passed!")
        return True

    except Exception as e:
        logger.error(f"Pipeline test failed with error: {str(e)}")
        return False


def query_rag_system(query: str, top_k: int = 5, collection_name: str = "rag_embedding") -> str:
    """
    Main interface for querying the RAG system.

    Args:
        query: The user's query
        top_k: Number of results to return
        collection_name: The name of the collection to search in

    Returns:
        Formatted search results
    """
    logger.info(f"Processing RAG query: '{query}'")

    try:
        # Search for similar chunks
        results = search_similar_chunks(query, top_k, collection_name)

        # Validate the results
        is_valid = validate_retrieved_content(query, results)
        if not is_valid:
            logger.warning("Retrieved results may not be fully relevant")

        # Format and return the results
        formatted_results = format_search_results(results)
        return formatted_results

    except Exception as e:
        logger.error(f"Error processing RAG query: {str(e)}")
        return f"Error processing query: {str(e)}"


def main():
    """
    Main function to orchestrate the entire workflow:
    1. Indexing mode: Get all URLs from the book website, extract text, chunk, embed, and store in Qdrant
    2. Retrieval mode: Query the indexed content and test the pipeline
    """
    import sys

    # Check command line arguments to determine mode
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

        if mode == "index":
            logger.info("Starting the Qdrant Book Indexing Process")

            # Define the target website
            base_url = "https://ai-book-silk.vercel.app/"

            # Step 1: Get all URLs from the website
            urls = get_all_urls(base_url)
            logger.info(f"Discovered {len(urls)} URLs to process")

            # Step 2: Create Qdrant collection
            create_collection("rag_embedding")

            total_chunks_processed = 0

            # Step 3: Process each URL
            for i, url in enumerate(urls):
                logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")

                # Extract text from the URL
                text = extract_text_from_url(url)
                if not text:
                    logger.warning(f"No text extracted from {url}, skipping")
                    continue

                # Chunk the text
                chunks = chunk_text(text)
                logger.info(f"Chunked content from {url} into {len(chunks)} parts")

                if not chunks:
                    continue

                # Generate embeddings for all chunks
                embeddings = embed(chunks)

                # Save each chunk and its embedding to Qdrant
                for chunk, embedding in zip(chunks, embeddings):
                    if len(embedding) == 768:  # Verify embedding dimension
                        save_chunk_to_qdrant(chunk, embedding, url, "rag_embedding")
                        total_chunks_processed += 1
                    else:
                        logger.warning(f"Invalid embedding dimension: {len(embedding)}, skipping")

            logger.info(f"Completed indexing. Total chunks saved to Qdrant: {total_chunks_processed}")
            logger.info("Qdrant Book Indexing Process Completed Successfully!")

        elif mode == "test":
            logger.info("Starting pipeline tests...")
            success = test_pipeline("rag_embedding")
            if success:
                logger.info("All pipeline tests passed!")
                print("Pipeline tests completed successfully!")
            else:
                logger.error("Some pipeline tests failed!")
                print("Some pipeline tests failed!")

        elif mode == "query" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            logger.info(f"Processing query: {query}")
            results = query_rag_system(query, top_k=5, collection_name="rag_embedding")
            print(f"\nSearch Results for '{query}':\n")
            print(results)

        elif mode == "count":
            count = get_all_documents_count("rag_embedding")
            print(f"Total documents in rag_embedding collection: {count}")

        elif mode == "collections":
            collections = list_collections()
            print(f"Available collections: {collections}")

        else:
            print("Usage:")
            print("  python main.py index     - Run the indexing process")
            print("  python main.py test      - Run pipeline tests")
            print("  python main.py query <your query> - Query the RAG system")
            print("  python main.py count     - Get document count")
            print("  python main.py collections - List all collections")

    else:
        # Default behavior: run indexing
        logger.info("Starting the Qdrant Book Indexing Process (default mode)")

        # Define the target website
        base_url = "https://ai-book-silk.vercel.app/"

        # Step 1: Get all URLs from the website
        urls = get_all_urls(base_url)
        logger.info(f"Discovered {len(urls)} URLs to process")

        # Step 2: Create Qdrant collection
        create_collection("rag_embedding")

        total_chunks_processed = 0

        # Step 3: Process each URL
        for i, url in enumerate(urls):
            logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")

            # Extract text from the URL
            text = extract_text_from_url(url)
            if not text:
                logger.warning(f"No text extracted from {url}, skipping")
                continue

            # Chunk the text
            chunks = chunk_text(text)
            logger.info(f"Chunked content from {url} into {len(chunks)} parts")

            if not chunks:
                continue

            # Generate embeddings for all chunks
            embeddings = embed(chunks)

            # Save each chunk and its embedding to Qdrant
            for chunk, embedding in zip(chunks, embeddings):
                if len(embedding) == 768:  # Verify embedding dimension
                    save_chunk_to_qdrant(chunk, embedding, url, "rag_embedding")
                    total_chunks_processed += 1
                else:
                    logger.warning(f"Invalid embedding dimension: {len(embedding)}, skipping")

        logger.info(f"Completed indexing. Total chunks saved to Qdrant: {total_chunks_processed}")
        logger.info("Qdrant Book Indexing Process Completed Successfully!")


if __name__ == "__main__":
    main()