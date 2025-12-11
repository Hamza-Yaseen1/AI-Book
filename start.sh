#!/bin/bash

# Start the backend API server in the background
echo "Starting backend API server on port 8000..."
python openai_agent_retrieval/run_server.py &
BACKEND_PID=$!

# Wait a bit for the backend to start
sleep 3

# Start the frontend server on port 3000
echo "Starting frontend server on port 3000..."
python frontend/server.py &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
