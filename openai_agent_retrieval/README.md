# OpenAI Agent with Qdrant Retrieval API

This project implements an OpenAI agent with FastAPI that integrates retrieval capabilities from a Qdrant vector database. The agent can answer questions by retrieving relevant information from the vector database and using it as context.

## Features

- FastAPI-based web service with OpenAPI documentation
- OpenAI agent that uses retrieved context to answer queries
- Qdrant vector database integration for semantic search
- RESTful API endpoints with proper validation
- Configurable retrieval parameters
- Comprehensive logging and error handling

## Requirements

- Python 3.8+
- OpenAI API key
- Qdrant vector database (with pre-indexed content)
- Optional: Cohere API key for embedding consistency

## Installation

1. Clone the repository or create the project structure
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_URL=your_qdrant_url_here  # e.g., localhost or a cloud instance
QDRANT_API_KEY=your_qdrant_api_key_if_needed
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=rag_embedding
COHERE_API_KEY=your_cohere_api_key_here  # Optional
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

## Usage

### Running the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `POST /query` - Query the OpenAI agent with retrieval
- `GET /docs` - Interactive API documentation

### Example Query

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "max_results": 5,
    "include_sources": true
  }'
```

## Project Structure

```
openai_agent_retrieval/
├── main.py          # FastAPI application
├── agent.py         # OpenAI agent implementation
├── retrieval.py     # Qdrant retrieval functions
├── models.py        # Pydantic data models
├── config.py        # Configuration settings
├── requirements.txt # Project dependencies
└── README.md        # This file
```

## API Documentation

The API provides interactive documentation at `/docs` when running. This includes:

- Endpoint descriptions
- Request/response schemas
- Example requests
- Testing interface

## Architecture

The system consists of several components:

1. **FastAPI Application**: Handles HTTP requests and responses
2. **OpenAI Agent**: Processes queries and generates responses
3. **Qdrant Retrieval**: Retrieves relevant documents from vector database
4. **Data Models**: Pydantic models for request/response validation

## Error Handling

The application includes comprehensive error handling:

- Input validation with Pydantic
- Proper HTTP status codes
- Detailed error messages
- Logging for debugging

## Security Considerations

- Validate all inputs
- Use environment variables for API keys
- Implement rate limiting in production
- Use HTTPS in production
- Validate and sanitize retrieved content