#!/usr/bin/env python3
"""
Test script for the Mock Swecha API Server
==========================================

This script tests the mock API endpoints to ensure they work correctly.
Run this after starting the mock server with: uv run python mock_swecha_api.py
"""

import json
import requests
import time

# Mock server configuration
MOCK_API_BASE = "http://localhost:8080"

def test_mock_api():
    """Test all mock API endpoints"""
    print("🧪 Testing Mock Swecha Corpus API")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(1)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{MOCK_API_BASE}/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   📝 {response.json()['message']}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 2: Health check
    try:
        response = requests.get(f"{MOCK_API_BASE}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   💚 Status: {response.json()['status']}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: Stats endpoint
    try:
        response = requests.get(f"{MOCK_API_BASE}/stats", timeout=5)
        print(f"✅ Stats endpoint: {response.status_code}")
        if response.status_code == 200:
            stats = response.json()
            print(f"   📊 Total contributions: {stats['total_contributions']}")
    except Exception as e:
        print(f"❌ Stats endpoint failed: {e}")
    
    # Test 4: Text contribution
    try:
        test_data = {
            "text": "ఇది ఒక టెస్ట్ వాక్యం",
            "language_code": "te",
            "metadata": {"source": "test", "quality": "high"}
        }
        response = requests.post(
            f"{MOCK_API_BASE}/contribute", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"✅ Text contribution: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   📤 Contribution ID: {result['contribution_id'][:8]}...")
    except Exception as e:
        print(f"❌ Text contribution failed: {e}")
    
    # Test 5: Get texts
    try:
        response = requests.get(f"{MOCK_API_BASE}/texts?limit=5", timeout=5)
        print(f"✅ Get texts: {response.status_code}")
        if response.status_code == 200:
            texts = response.json()
            print(f"   📚 Found {texts['total']} texts")
    except Exception as e:
        print(f"❌ Get texts failed: {e}")
    
    # Test 6: Search corpus
    try:
        response = requests.get(f"{MOCK_API_BASE}/search?query=టెస్ట్", timeout=5)
        print(f"✅ Search corpus: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print(f"   🔍 Found {results['total_found']} matches")
    except Exception as e:
        print(f"❌ Search corpus failed: {e}")
    
    # Test 7: Documentation
    try:
        response = requests.get(f"{MOCK_API_BASE}/docs", timeout=5)
        print(f"✅ API docs: {response.status_code}")
        if response.status_code == 200:
            print(f"   📚 API documentation available")
    except Exception as e:
        print(f"❌ API docs failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Mock API testing completed!")
    print(f"🌐 API Documentation: {MOCK_API_BASE}/docs")
    print(f"🔧 Admin Reset: {MOCK_API_BASE}/admin/reset")

if __name__ == "__main__":
    test_mock_api()
