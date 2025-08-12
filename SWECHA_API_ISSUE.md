# GitHub Issue: Swecha Corpus API

## 🎯 Issue Title
```
feat(api): Implement core corpus contribution endpoints for Telugu text submission
```

## 📋 Issue Template

```markdown
---
name: API Issue
about: Report an issue or suggest an improvement related to the backend API endpoints.
title: "[API]: feat(api): Implement core corpus contribution endpoints for Telugu text submission"
labels: "api"
assignees: ''

---

title: "feat(api): Implement core corpus contribution endpoints for Telugu text submission"

## 🔌 API Issue

### Describe the API issue

The Swecha Telugu Corpus API currently lacks the core functionality endpoints required for corpus contribution. While basic infrastructure endpoints (health, docs, root) are operational, all contribution-related endpoints return 404 "Not Found". This prevents applications like WhispNote from contributing Telugu text data to the corpus collection.

### API Endpoint (if applicable)

**Missing/Non-functional endpoints:**
- `POST /contribute` - Main contribution endpoint
- `POST /upload` - File upload functionality
- `GET /corpus` - Corpus data retrieval
- `POST /corpus` - Corpus data submission
- `GET /texts` - Text data management
- `POST /texts` - Text data submission
- `GET /audio` - Audio data management
- `POST /audio` - Audio data submission
- `GET /stats` - Corpus statistics
- `GET /api/v1/*` - Versioned API endpoints

**Working endpoints:**
- `GET /` - Welcome message ✅
- `GET /health` - Health check ✅
- `GET /docs` - API documentation ✅
- `GET /redoc` - Alternative documentation ✅

### Request/Response examples (if applicable)

**Current Behavior (404 Error):**
```bash
POST https://api.corpus.swecha.org/contribute
Content-Type: application/json

{
  "text": "ఇది ఒక టెస్ట్ వాక్యం తెలుగులో",
  "language": "te",
  "source": "whispnote_test",
  "user_consent": true,
  "metadata": {
    "test": true,
    "timestamp": "2025-08-12T23:13:25",
    "app_version": "2.0.0"
  }
}

Response: 404 Not Found
{
  "detail": "Not Found"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Text contribution accepted",
  "contribution_id": "contrib_12345",
  "corpus_stats": {
    "total_contributions": 1250,
    "total_words": 45670
  }
}
```

### Expected behavior

The API should provide functional endpoints for:

1. **Text Contribution** (`POST /contribute`):
   - Accept Telugu text submissions with metadata
   - Validate text quality and language
   - Store contributions with proper attribution
   - Return contribution confirmation with ID

2. **Corpus Management** (`GET/POST /corpus`):
   - Retrieve corpus statistics and metadata
   - Submit structured corpus data
   - Support bulk operations

3. **Authentication** (if required):
   - Bearer token validation
   - Rate limiting per user/application
   - Proper error responses for auth failures

4. **API Versioning** (`/api/v1/`):
   - Consistent URL structure
   - Version-specific documentation
   - Backward compatibility support

### Additional context

**Test Results Summary:**
- **API Availability**: 100% (server operational)
- **Functional Endpoints**: 4/17 (23.5%)
- **Average Response Time**: ~250ms (good performance)

**Integration Impact:**
- WhispNote app has implemented proper error handling and queuing
- Currently 2 pending contributions queued locally waiting for API
- Integration code is ready and tested - just waiting for endpoints

**Technical Requirements:**
- FastAPI framework (already in use)
- JSON request/response format
- HTTPS support (already implemented)
- Proper HTTP status codes (200, 201, 400, 401, 500)

**Priority**: **High** - This blocks the primary functionality of corpus contribution applications.

**Related Files:**
- API Test Report: [SWECHA_API_TEST_REPORT.md](https://github.com/nikhilesh9ix/Whispnote-2/blob/main/SWECHA_API_TEST_REPORT.md)
- Test Results: `swecha_api_test_report_20250812_231331.json`

> 📌 **Follow semantic issue titling convention**: `<type>(<scope>): <description>` (e.g., `feat(api): add user registration endpoint` or `fix(records): handle null values`).
```

## 📊 Supporting Data

### Test Environment
- **Date**: August 12, 2025
- **Time**: 23:13:22 - 23:13:31 UTC
- **Test Duration**: ~9 seconds
- **API Version**: 0.1.0

### Detailed Test Results
- **Total Endpoints Tested**: 17
- **Working Endpoints**: 4 (23.5%)
- **Failed Endpoints**: 13 (76.5%)
- **Average Response Time**: ~250ms
- **API Availability**: 100%

### Error Analysis
All contribution-related endpoints return the same error:
```json
{
  "detail": "Not Found"
}
```

This indicates that the endpoints are not implemented rather than experiencing runtime errors.

## 🎯 Next Steps

1. **Submit this issue** to the Swecha API repository
2. **Monitor API development** progress
3. **Test endpoints periodically** to detect when they become available
4. **Update WhispNote integration** once endpoints are implemented

## 📁 Related Files

- `SWECHA_API_TEST_REPORT.md` - Comprehensive test results
- `tests/comprehensive_api_test.py` - API testing script
- `swecha_api_test_report_20250812_231331.json` - Raw test data
- `src/api/swecha_api.py` - WhispNote integration code

---

**Generated by**: WhispNote API Test Suite v2.0.0
**For**: Swecha Telugu Corpus API Issue Reporting
