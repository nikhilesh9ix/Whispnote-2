#!/usr/bin/env python3
"""
Test more comprehensive endpoint patterns for Swecha API
"""

import requests
import json
from src.api.swecha_config import SWECHA_API_TOKEN

def test_comprehensive_endpoints():
    """Test comprehensive endpoint patterns"""

    base_url = "https://api.corpus.swecha.org"
    headers = {
        'Authorization': f'Bearer {SWECHA_API_TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'WhispNote/1.0 (Telugu Voice Notes App)'
    }

    # More comprehensive endpoint patterns
    test_patterns = [
        # REST API patterns
        ("/api/v1/texts", "GET"),
        ("/api/v1/texts", "POST"),
        ("/api/v1/audio", "GET"),
        ("/api/v1/audio", "POST"),
        ("/api/v1/corpus", "GET"),
        ("/api/v1/corpus", "POST"),

        # Alternative patterns
        ("/v1/texts", "GET"),
        ("/v1/texts", "POST"),
        ("/v1/contribute", "GET"),
        ("/v1/contribute", "POST"),

        # Direct resource patterns
        ("/text", "POST"),
        ("/audio", "POST"),
        ("/data", "POST"),
        ("/telugu", "POST"),

        # FastAPI/Django patterns
        ("/texts/", "GET"),
        ("/texts/", "POST"),
        ("/audio/", "GET"),
        ("/audio/", "POST"),

        # Info endpoints
        ("/info", "GET"),
        ("/version", "GET"),
        ("/endpoints", "GET"),
        ("/schema", "GET"),

        # User/Auth endpoints
        ("/user", "GET"),
        ("/profile", "GET"),
        ("/me", "GET"),

    ]

    print("🔍 Comprehensive Swecha API Endpoint Testing")
    print("=" * 60)

    working_endpoints = []

    for endpoint, method in test_patterns:
        try:
            url = f"{base_url}{endpoint}"

            # Sample payload for POST requests
            sample_payload = {
                "text": "ఇది ఒక తెలుగు వాక్యం",
                "language": "te",
                "metadata": {
                    "source": "WhispNote",
                    "method": "test"
                }
            }

            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:  # POST
                response = requests.post(url, headers=headers, json=sample_payload, timeout=10)

            status = response.status_code

            if status in [200, 201]:
                print(f"✅ {method} {endpoint} - SUCCESS (HTTP {status})")
                try:
                    content = response.json()
                    if len(str(content)) > 200:
                        print(f"   Response: {json.dumps(content, indent=2)[:200]}...")
                    else:
                        print(f"   Response: {json.dumps(content, indent=2)}")
                except:
                    print(f"   Response: {response.text[:150]}...")
                working_endpoints.append((endpoint, method, status))

            elif status == 422:
                print(f"📝 {method} {endpoint} - VALIDATION ERROR (need correct payload)")
                try:
                    error = response.json()
                    print(f"   Details: {error}")
                except:
                    pass
                working_endpoints.append((endpoint, method, status))

            elif status in [401, 403]:
                print(f"🔐 {method} {endpoint} - AUTH ERROR (HTTP {status})")

            elif status == 404:
                pass  # Don't print 404s to reduce noise

            elif status == 405:
                print(f"⚠️  {method} {endpoint} - METHOD NOT ALLOWED (endpoint exists!)")
                working_endpoints.append((endpoint, "OTHER", status))

            else:
                print(f"❓ {method} {endpoint} - HTTP {status}")
                if status not in [404]:
                    working_endpoints.append((endpoint, method, status))

        except requests.RequestException:
            pass  # Skip connection errors

    print("\n" + "=" * 60)
    print("🎯 Potentially Working Endpoints:")
    if working_endpoints:
        for endpoint, method, status in working_endpoints:
            if status in [200, 201]:
                print(f"  ✅ {method} {endpoint} - WORKING")
            elif status == 422:
                print(f"  📝 {method} {endpoint} - NEEDS CORRECT PAYLOAD")
            elif status == 405:
                print(f"  ⚠️  {endpoint} - EXISTS BUT WRONG METHOD")
            else:
                print(f"  ❓ {method} {endpoint} - HTTP {status}")
    else:
        print("  ❌ No additional working endpoints found")

    return working_endpoints

if __name__ == "__main__":
    endpoints = test_comprehensive_endpoints()
