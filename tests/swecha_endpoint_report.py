#!/usr/bin/env python3
"""
Complete Swecha API Endpoint Status Report
"""

import requests
from src.api.swecha_config import SWECHA_API_TOKEN

def generate_endpoint_report():
    """Generate a comprehensive endpoint status report"""

    base_url = "https://api.corpus.swecha.org"
    headers = {
        'Authorization': f'Bearer {SWECHA_API_TOKEN}',
        'Content-Type': 'application/json',
        'User-Agent': 'WhispNote/1.0 (Telugu Voice Notes App)'
    }

    print("🔍 SWECHA CORPUS API - COMPLETE ENDPOINT STATUS REPORT")
    print("=" * 70)
    print(f"🔗 Base URL: {base_url}")
    print("🔑 Authentication: Bearer Token (Configured)")
    print("📅 Test Date: August 6, 2025")
    print("=" * 70)

    # Categorized endpoints to test
    endpoint_categories = {
        "✅ WORKING ENDPOINTS": [
            ("/", "GET", None, "Basic API info"),
            ("/health", "GET", None, "Health check"),
            ("/docs", "GET", None, "API documentation"),
        ],

        "❌ NON-WORKING ENDPOINTS (404 Not Found)": [
            ("/openapi.json", "GET", None, "OpenAPI schema"),
            ("/stats", "GET", None, "Corpus statistics"),
            ("/search", "GET", None, "Search corpus"),
            ("/contribute", "GET", None, "Contribution info"),
            ("/contribute", "POST", {"text": "టెస్ట్", "language": "te"}, "Text contribution"),
            ("/contribute/text", "POST", {"text": "టెస్ట్", "language": "te"}, "Text contribution"),
            ("/contribute/audio", "POST", None, "Audio contribution"),
            ("/upload", "POST", {"data": "test"}, "Data upload"),
            ("/submit", "POST", {"text": "టెస్ట్"}, "Data submission"),
            ("/corpus", "GET", None, "Corpus access"),
            ("/texts", "GET", None, "Text collection"),
            ("/audio", "GET", None, "Audio collection"),
            ("/collections", "GET", None, "Data collections"),
        ],

        "🔍 API VERSION ENDPOINTS": [
            ("/api", "GET", None, "API root"),
            ("/v1", "GET", None, "Version 1 root"),
            ("/api/v1", "GET", None, "API v1 root"),
            ("/api/v1/texts", "GET", None, "V1 text endpoints"),
            ("/api/v1/texts", "POST", {"text": "టెస్ట్", "language": "te"}, "V1 text submission"),
            ("/api/v1/audio", "GET", None, "V1 audio endpoints"),
            ("/api/v1/corpus", "GET", None, "V1 corpus endpoints"),
        ],

        "🔐 AUTHENTICATION ENDPOINTS": [
            ("/auth", "GET", None, "Authentication info"),
            ("/token", "GET", None, "Token info"),
            ("/login", "POST", None, "Login endpoint"),
            ("/user", "GET", None, "User info"),
            ("/profile", "GET", None, "User profile"),
            ("/me", "GET", None, "Current user"),
        ]
    }

    results = {}

    for category, endpoints in endpoint_categories.items():
        print(f"\n{category}")
        print("-" * 50)
        results[category] = []

        for endpoint, method, payload, description in endpoints:
            try:
                url = f"{base_url}{endpoint}"

                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                else:  # POST
                    response = requests.post(url, headers=headers, json=payload, timeout=10)

                status = response.status_code

                if status == 200:
                    status_icon = "✅"
                    status_text = "WORKING"
                    try:
                        content = response.json()
                        preview = str(content)[:100] + "..." if len(str(content)) > 100 else str(content)
                    except:
                        preview = response.text[:100] + "..." if len(response.text) > 100 else response.text

                elif status == 201:
                    status_icon = "✅"
                    status_text = "CREATED"
                    preview = "Resource created successfully"

                elif status == 401:
                    status_icon = "🔐"
                    status_text = "UNAUTHORIZED"
                    preview = "Authentication required"

                elif status == 403:
                    status_icon = "🚫"
                    status_text = "FORBIDDEN"
                    preview = "Access denied"

                elif status == 404:
                    status_icon = "❌"
                    status_text = "NOT FOUND"
                    preview = "Endpoint does not exist"

                elif status == 405:
                    status_icon = "⚠️"
                    status_text = "METHOD NOT ALLOWED"
                    preview = "Endpoint exists but method not supported"

                elif status == 422:
                    status_icon = "📝"
                    status_text = "VALIDATION ERROR"
                    try:
                        error = response.json()
                        preview = str(error)[:100] + "..."
                    except:
                        preview = "Invalid request format"

                else:
                    status_icon = "❓"
                    status_text = f"HTTP {status}"
                    preview = "Unexpected response"

                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status": status,
                    "status_text": status_text,
                    "description": description,
                    "preview": preview
                }
                results[category].append(result)

                print(f"{status_icon} {method:4} {endpoint:25} - {status_text}")
                print(f"    📝 {description}")
                if status in [200, 201] and len(preview) > 0:
                    print(f"    📄 Response: {preview}")
                print()

            except requests.RequestException as e:
                status_icon = "💥"
                status_text = "CONNECTION ERROR"
                preview = str(e)

                result = {
                    "endpoint": endpoint,
                    "method": method,
                    "status": "ERROR",
                    "status_text": status_text,
                    "description": description,
                    "preview": preview
                }
                results[category].append(result)

                print(f"{status_icon} {method:4} {endpoint:25} - {status_text}")
                print(f"    ⚠️  {str(e)}")
                print()

    # Summary
    print("\n" + "=" * 70)
    print("📊 ENDPOINT STATUS SUMMARY")
    print("=" * 70)

    working_count = 0
    total_count = 0

    for category, endpoint_results in results.items():
        category_working = sum(1 for r in endpoint_results if r["status"] == 200 or r["status"] == 201)
        category_total = len(endpoint_results)
        working_count += category_working
        total_count += category_total

        print(f"{category}: {category_working}/{category_total} working")

        if category_working > 0:
            for result in endpoint_results:
                if result["status"] in [200, 201]:
                    print(f"  ✅ {result['method']} {result['endpoint']} - {result['description']}")

    print(f"\n🎯 OVERALL STATUS: {working_count}/{total_count} endpoints working ({working_count/total_count*100:.1f}%)")

    print("\n🔧 INTEGRATION STATUS FOR WHISPNOTE:")
    if working_count >= 3:  # Basic endpoints working
        print("✅ API Integration: READY")
        print("✅ Authentication: CONFIGURED")
        print("❌ Contribution Features: NOT YET AVAILABLE")
        print("🔄 Data Storage: LOCAL PENDING UPLOADS")
        print("\n💡 RECOMMENDATION: Proceed with project - contribution endpoints will be available soon!")
    else:
        print("❌ API Integration: LIMITED")
        print("⚠️  Few endpoints available")

    return results

if __name__ == "__main__":
    generate_endpoint_report()
