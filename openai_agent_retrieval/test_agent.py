"""
Simple test script to verify the OpenAI Agent with Qdrant Retrieval implementation.
This script tests the core functionality without requiring a running server.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported without errors."""
    print("Testing imports...")

    try:
        from config import OPENAI_API_KEY, QDRANT_URL
        print("[OK] Config module imported successfully")
    except Exception as e:
        print(f"[ERROR] Config import failed: {e}")
        return False

    try:
        from models import QueryRequest, QueryResponse
        print("[OK] Models module imported successfully")
    except Exception as e:
        print(f"[ERROR] Models import failed: {e}")
        return False

    try:
        from retrieval import retrieve_content_tool
        print("[OK] Retrieval module imported successfully")
    except Exception as e:
        print(f"[ERROR] Retrieval import failed: {e}")
        return False

    try:
        from agent import query_agent
        print("[OK] Agent module imported successfully")
    except Exception as e:
        print(f"[ERROR] Agent import failed: {e}")
        return False

    return True


def test_config():
    """Test that required configuration is available."""
    print("\nTesting configuration...")

    # Check if required environment variables are set
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY not found in environment")
        return False
    else:
        print("[OK] OPENAI_API_KEY found in environment")

    if not os.getenv("QDRANT_URL"):
        print("[ERROR] QDRANT_URL not found in environment")
        return False
    else:
        print("[OK] QDRANT_URL found in environment")

    return True


def test_retrieval():
    """Test the retrieval functionality."""
    print("\nTesting retrieval functionality...")

    try:
        from retrieval import retrieve_content_tool

        # Test with a simple query
        results = retrieve_content_tool("test query", max_results=2)
        print(f"[OK] Retrieval test completed, found {len(results)} results")

        if results:
            print(f"  First result ID: {results[0]['id'][:20]}...")
            print(f"  First result score: {results[0]['score']:.3f}")

        return True
    except Exception as e:
        print(f"[ERROR] Retrieval test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running tests for OpenAI Agent with Qdrant Retrieval...\n")

    success = True

    # Test imports
    success &= test_imports()

    # Test configuration
    success &= test_config()

    # Test retrieval
    success &= test_retrieval()

    print(f"\n{'='*50}")
    if success:
        print("[OK] All tests passed! The implementation is ready.")
        print("\nTo start the server, run:")
        print("  cd openai_agent_retrieval")
        print("  python main.py")
    else:
        print("[ERROR] Some tests failed. Please check the output above.")
    print(f"{'='*50}")

    return success


if __name__ == "__main__":
    main()