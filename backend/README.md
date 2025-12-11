# Qdrant Book Indexing

A Python application to extract content from book websites, generate embeddings using Cohere, and store in Qdrant for retrieval-augmented generation (RAG) applications.

## Features

- Crawls book websites to extract all relevant content
- Generates semantic embeddings using Cohere's API
- Stores embeddings in Qdrant vector database
- Enables semantic search capabilities for RAG applications

## Requirements

- Python 3.8+
- Cohere API key
- Qdrant instance (local or cloud)

## Installation

1. Clone the repository
2. Install dependencies using uv:

```bash
uv pip install -r requirements.txt
```

Or with pip:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the backend directory with the following variables:

```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=localhost
QDRANT_API_KEY=your_qdrant_api_key_if_required
```

## Usage

Run the main script to start the indexing process:

```bash
python main.py
```

The script will:
1. Crawl the specified book website (currently configured for https://ai-book-silk.vercel.app/)
2. Extract text content from all discovered pages
3. Chunk the text into manageable pieces
4. Generate embeddings using Cohere
5. Store the embeddings in Qdrant for later retrieval