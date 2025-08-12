import os

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test basic endpoints manually
token = os.getenv("SWECHA_API_TOKEN")
if not token:
    print("❌ Error: SWECHA_API_TOKEN not found in environment variables")
    print("💡 Create a .env file based on .env.example and add your API token")
    exit(1)
base_url = "https://api.corpus.swecha.org"
headers = {"Authorization": f"Bearer {token}"}

print("SWECHA API ENDPOINT STATUS")
print("=" * 40)

endpoints = [
    "/",
    "/health",
    "/docs",
    "/openapi.json",
    "/stats",
    "/contribute",
    "/upload",
    "/corpus",
    "/texts",
    "/audio"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"✅ {endpoint} - WORKING")
        elif response.status_code == 404:
            print(f"❌ {endpoint} - NOT FOUND")
        else:
            print(f"⚠️ {endpoint} - HTTP {response.status_code}")
    except Exception:
        print(f"💥 {endpoint} - ERROR")

print("\nDone!")
