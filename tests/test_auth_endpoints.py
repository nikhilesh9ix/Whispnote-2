#!/usr/bin/env python3
"""
Advanced test script for Swecha API with bearer token
"""

import json

import requests

from src.api.swecha_config import SWECHA_API_TOKEN


def test_endpoints_with_auth():
    """Test various endpoints with authentication"""

    base_url = "https://api.corpus.swecha.org"
    headers = {
        "Authorization": f"Bearer {SWECHA_API_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "WhispNote/1.0 (Telugu Voice Notes App)",
    }

    # List of endpoints to test
    endpoints = [
        ("/", "GET", None),
        ("/docs", "GET", None),
        ("/openapi.json", "GET", None),
        ("/health", "GET", None),
        ("/status", "GET", None),
        ("/api", "GET", None),
        ("/v1", "GET", None),
        ("/corpus", "GET", None),
        ("/collections", "GET", None),
        ("/texts", "GET", None),
        ("/audio", "GET", None),
        ("/upload", "POST", {"test": "data"}),
        ("/submit", "POST", {"test": "data"}),
        ("/contribute", "POST", {"text": "టెస్ట్", "language": "te"}),
        ("/add", "POST", {"text": "టెస్ట్", "language": "te"}),
        ("/texts/add", "POST", {"text": "టెస్ట్", "language": "te"}),
        ("/corpus/add", "POST", {"text": "టెస్ట్", "language": "te"}),
    ]

    print("🔍 Testing Swecha API Endpoints with Bearer Token")
    print("=" * 60)
    print(f"🔑 Using token: {SWECHA_API_TOKEN[:20]}...")
    print()

    working_endpoints = []

    for endpoint, method, payload in endpoints:
        try:
            url = f"{base_url}{endpoint}"

            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:  # POST
                response = requests.post(url, headers=headers, json=payload, timeout=10)

            status = response.status_code

            if status == 200:
                print(f"✅ {method} {endpoint} - SUCCESS")
                try:
                    content = response.json()
                    print(f"   Response: {json.dumps(content, indent=2)[:200]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
                working_endpoints.append((endpoint, method))

            elif status == 201:
                print(f"✅ {method} {endpoint} - CREATED")
                working_endpoints.append((endpoint, method))

            elif status == 401:
                print(f"🔐 {method} {endpoint} - UNAUTHORIZED (token issue)")

            elif status == 403:
                print(f"🚫 {method} {endpoint} - FORBIDDEN")

            elif status == 404:
                print(f"❌ {method} {endpoint} - NOT FOUND")

            elif status == 405:
                print(f"⚠️  {method} {endpoint} - METHOD NOT ALLOWED")

            elif status == 422:
                print(f"📝 {method} {endpoint} - VALIDATION ERROR")
                try:
                    error = response.json()
                    print(f"   Error: {error}")
                except:
                    pass

            else:
                print(f"❓ {method} {endpoint} - HTTP {status}")

        except requests.RequestException as e:
            print(f"💥 {method} {endpoint} - CONNECTION ERROR: {e}")

        print()

    print("=" * 60)
    print("📋 Summary of Working Endpoints:")
    if working_endpoints:
        for endpoint, method in working_endpoints:
            print(f"  ✅ {method} {endpoint}")
    else:
        print("  ❌ No working endpoints found")


if __name__ == "__main__":
    test_endpoints_with_auth()
