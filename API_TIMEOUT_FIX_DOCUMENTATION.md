# Swecha API Timeout Fix - Complete Implementation

## 🔧 Problem Analysis

The original error was:
```
Error fetching contributions: HTTPSConnectionPool(host='api.corpus.swecha.org', port=443): Read timed out. (read timeout=10)
```

This indicated that the API requests were timing out after 10 seconds, which is too short for the Swecha API endpoints that may involve complex data processing.

## 📋 OpenAPI Specification Analysis

After reviewing the provided OpenAPI 3.1.0 specification for the Swecha Corpus API, I identified the correct endpoints and their requirements:

### Key Endpoints Used:
- `GET /api/v1/auth/me` - Get current user information
- `GET /api/v1/users/{user_id}/contributions` - Get all user contributions
- `GET /api/v1/users/{user_id}/contributions/{media_type}` - Get contributions by media type
- `POST /api/v1/tasks/generate-statistics` - Generate corpus statistics (task-based)
- `GET /api/v1/tasks/status/{task_id}` - Check task status

### Authentication Required:
All endpoints require Bearer token authentication via the `Authorization` header.

## 🔨 Fixes Implemented

### 1. Increased Timeout Values
**File:** `src/utils/swecha_storage.py`

```python
# Before: timeout=10
user_response = self.session.get(
    f"{self.base_url}/auth/me",
    headers=headers,
    timeout=30  # Increased from 10s to 30s
)

contributions_response = self.session.get(
    f"{self.base_url}/users/{user_id}/contributions",
    headers=headers,
    timeout=30  # Increased from 10s to 30s
)

# For statistics generation (more complex operation)
stats_response = self.session.post(
    f"{self.base_url}/tasks/generate-statistics",
    headers=headers,
    params={"user_specific": False},
    timeout=45  # Increased to 45s for complex operations
)
```

### 2. Enhanced Error Handling
**File:** `src/utils/swecha_storage.py`

```python
except requests.exceptions.Timeout:
    st.error("⏱️ Request timed out. Please check your internet connection and try again.")
    return None
except requests.exceptions.ConnectionError:
    st.error("🌐 Connection error. Please check your internet connection.")
    return None
except requests.exceptions.RequestException as e:
    st.error(f"❌ Error fetching contributions: {str(e)}")
    return None
```

### 3. Retry Strategy with Backoff
**File:** `src/utils/swecha_storage.py`

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "POST"],
    backoff_factor=1
)

adapter = HTTPAdapter(max_retries=retry_strategy)
self.session.mount("http://", adapter)
self.session.mount("https://", adapter)
```

### 4. Task-Based Statistics Generation
**File:** `src/utils/swecha_storage.py`

Since the statistics endpoint follows a task-based pattern (POST to create task, then poll for results):

```python
def get_global_corpus_stats(self) -> Optional[Dict[str, Any]]:
    # Step 1: Start statistics generation task
    stats_response = self.session.post(
        f"{self.base_url}/tasks/generate-statistics",
        headers=headers,
        params={"user_specific": False},
        timeout=45
    )

    if stats_response.status_code == 200:
        task_data = stats_response.json()
        task_id = task_data.get('task_id')

        # Step 2: Poll for task completion
        for _ in range(10):  # Check up to 10 times
            time.sleep(2)  # Wait 2 seconds between checks

            task_status_response = self.session.get(
                f"{self.base_url}/tasks/status/{task_id}",
                headers=headers,
                timeout=15
            )

            if task_status_response.status_code == 200:
                task_status = task_status_response.json()
                if task_status.get('status') == 'SUCCESS':
                    return task_status.get('result')
```

### 5. Improved UI Error Messages
**File:** `app.py`

```python
except Exception as e:
    error_message = str(e)
    if "timeout" in error_message.lower():
        st.error("⏱️ **Request timed out while loading your contributions.**")
        st.info("📡 This usually means the server is busy. Please try again in a few moments.")
        st.markdown("""
        **Troubleshooting tips:**
        - Check your internet connection
        - Wait a few minutes and refresh the page
        - Try switching to a different network if possible
        """)
    elif "connection" in error_message.lower():
        st.error("🌐 **Connection error while loading contributions.**")
        st.info("📡 Please check your internet connection and try again.")
    else:
        st.error(f"❌ **Error loading contributions:** {error_message}")
        st.info("📞 If this persists, please contact support or try again later.")

    # Show fallback local statistics
    st.markdown("---")
    st.info("📱 **Showing local device statistics as fallback:**")
```

### 6. Session Configuration Improvements
**File:** `src/utils/swecha_storage.py`

```python
# Set default headers
self.session.headers.update({
    'User-Agent': 'WhispNote/2.0 (Telugu Voice Notes App)',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
})
```

## 📊 API Response Data Structure

Based on the OpenAPI specification, the expected response structures are:

### ContributionRead Response:
```json
{
  "user_id": "uuid",
  "total_contributions": 123,
  "contributions_by_media_type": {
    "text": 45,
    "audio": 67,
    "image": 8,
    "video": 3
  },
  "audio_contributions": [...],
  "text_contributions": [...],
  "audio_duration": 3600,
  "video_duration": 240
}
```

### ContributionFilterRead Response (by media type):
```json
{
  "user_id": "uuid",
  "total_contributions": 67,
  "contributions": [
    {
      "id": "uuid",
      "title": "Audio Recording",
      "size": 2048576,
      "duration": 120,
      "reviewed": true,
      "timestamp": "2025-08-28T10:30:00Z"
    }
  ]
}
```

## 🧪 Testing

Created `test_api_timeout_fix.py` to verify all fixes:

```bash
uv run python test_api_timeout_fix.py
```

**Test Results:**
- ✅ API health check passed
- ✅ Timeout configuration verified
- ✅ Retry strategy implemented
- ✅ Error handling working correctly
- ✅ Correct API endpoints validated

## 🚀 Expected Improvements

1. **Reduced Timeouts:** 30-45 second timeouts should handle slow server responses
2. **Better Error Messages:** Users get specific guidance based on error type
3. **Automatic Retries:** Network hiccups are handled automatically
4. **Graceful Degradation:** Local statistics shown as fallback
5. **Task-Based Operations:** Proper handling of async statistics generation

## 📝 Usage Instructions

1. **For Users:** The Stats tab should now work much more reliably
2. **For Developers:** All API calls include proper timeout and retry handling
3. **For Testing:** Use the test script to verify functionality

## 🔄 Future Enhancements

1. **Caching:** Implement response caching for frequently accessed data
2. **Progressive Loading:** Load basic stats first, then detailed contributions
3. **WebSocket Integration:** Real-time updates for active contributions
4. **Offline Mode:** Enhanced local statistics when API is unavailable

## 📞 Support

If timeout issues persist:
1. Check network connectivity
2. Verify authentication token validity
3. Monitor server status at `https://api.corpus.swecha.org/health`
4. Contact API support if server-side issues are detected

---

*Last Updated: August 28, 2025*
*WhispNote 2.0 - Telugu Voice Notes Application*
