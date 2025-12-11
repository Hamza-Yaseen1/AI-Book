FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt backend_requirements.txt
COPY openai_agent_retrieval/requirements.txt agent_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r backend_requirements.txt
RUN pip install --no-cache-dir -r agent_requirements.txt

# Copy all project files
COPY backend ./backend
COPY openai_agent_retrieval ./openai_agent_retrieval
COPY frontend ./frontend
COPY hf_app.py ./hf_app.py

# Expose port for Hugging Face Spaces
EXPOSE 7860

# Run the unified application
CMD ["python", "hf_app.py"]

