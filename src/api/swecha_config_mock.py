"""
Mock Swecha API Configuration
=============================

Alternative configuration for WhispNote to use the local mock server
for development and testing when the real Swecha API is not available.

Usage:
1. Start mock server: uv run python mock_swecha_api.py
2. Update .env file to use mock server
3. Use WhispNote normally - contributions will go to mock server
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock server configuration
MOCK_SERVER_BASE_URL = "http://localhost:8080"
MOCK_SERVER_TOKEN = "mock-development-token"  # Not required but for compatibility

# Override Swecha API settings for mock server
if os.getenv("USE_MOCK_SWECHA_API", "false").lower() == "true":
    SWECHA_API_BASE_URL = MOCK_SERVER_BASE_URL
    SWECHA_API_TOKEN = MOCK_SERVER_TOKEN
    print("🔧 Using Mock Swecha API for development")
    print(f"📡 Mock server: {MOCK_SERVER_BASE_URL}")
    print("💡 Start mock server with: uv run python mock_swecha_api.py")
else:
    # Use production settings
    SWECHA_API_BASE_URL = os.getenv("SWECHA_API_BASE_URL", "https://api.corpus.swecha.org")
    SWECHA_API_TOKEN = os.getenv("SWECHA_API_TOKEN")
    print("🌐 Using Production Swecha API")
    print(f"📡 Production server: {SWECHA_API_BASE_URL}")

TOKEN_TYPE = "bearer"

# Validation for production
if not SWECHA_API_TOKEN and not os.getenv("USE_MOCK_SWECHA_API"):
    print("⚠️  Warning: SWECHA_API_TOKEN not found in environment variables")
    print("💡 Create a .env file based on .env.example and add your API token")
    print("🔧 Or set USE_MOCK_SWECHA_API=true to use the mock server")
