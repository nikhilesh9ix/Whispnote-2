import requests

# Test basic endpoints manually
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ1ODA1ODgsInN1YiI6IjgzMDAzYzQwLThmYzAtNDg4ZS1iMDgzLTA3NTViZDAzNTIwMSJ9.S02P9mEBhHkom4HT5yDFqmMGX3PRLNEUJ_eEYcH3zXQ"
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
