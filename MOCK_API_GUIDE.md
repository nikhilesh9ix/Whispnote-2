# Mock Swecha Corpus API Server

## 🎯 Purpose

This mock server implements all the missing Swecha corpus API endpoints for local development and testing of WhispNote integration. It simulates the endpoints that will eventually be available at `https://api.corpus.swecha.org`.

## 🚀 Quick Start

### 1. Start the Mock Server

```bash
# Install enhanced dependencies (includes FastAPI, uvicorn)
uv sync --group enhanced

# Start the mock server
uv run python mock_swecha_api.py
```

The server will start at: **http://localhost:8080**

### 2. Configure WhispNote to Use Mock Server

Create a `.env` file or update your existing one:

```bash
# Copy from template
cp .env.example .env

# Edit .env and add:
USE_MOCK_SWECHA_API=true
```

### 3. Test the API

```bash
# Test all endpoints
uv run python test_mock_api.py

# Or manually test
curl http://localhost:8080/health
```

## 📡 Available Endpoints

### ✅ Working Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive API documentation |
| `GET` | `/redoc` | Alternative documentation |
| `GET` | `/stats` | Corpus statistics |
| `POST` | `/contribute` | Submit text contributions |
| `POST` | `/contribute/audio` | Submit audio + transcription |
| `GET` | `/corpus` | Corpus overview |
| `GET` | `/texts` | List text contributions |
| `GET` | `/audio` | List audio contributions |
| `GET` | `/search` | Search corpus data |
| `GET` | `/auth` | Authentication info |
| `GET` | `/user` | User information |

### 🔧 Admin Endpoints (Development Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/reset` | Clear all stored data |
| `GET` | `/admin/export` | Export all corpus data |

## 🧪 Testing Examples

### Text Contribution

```bash
curl -X POST http://localhost:8080/contribute \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ఇది ఒక టెస్ట్ వాక్యం",
    "language_code": "te",
    "metadata": {"source": "test"}
  }'
```

### Audio Contribution

```bash
curl -X POST http://localhost:8080/contribute/audio \
  -F "audio=@test_audio.wav" \
  -F "transcription=ఇది ఆడియో టెస్ట్" \
  -F "language_code=te"
```

### Search Corpus

```bash
curl "http://localhost:8080/search?query=టెస్ట్&language=te"
```

## 📊 WhispNote Integration

When using the mock server, WhispNote will:

1. **✅ Accept Contributions**: Text and audio submissions work normally
2. **✅ Store Data**: All contributions are stored in memory
3. **✅ Provide Feedback**: Returns proper success/error responses
4. **✅ Enable Testing**: Full API compatibility for development

### Integration Test

```bash
# Start WhispNote with mock API
USE_MOCK_SWECHA_API=true uv run streamlit run app.py

# Check integration status in WhispNote UI
# Contributions will be sent to mock server instead of production
```

## 💾 Data Storage

- **Memory-based**: Data is stored in memory during server runtime
- **Non-persistent**: Data is lost when server stops (development only)
- **Reset capability**: Use `/admin/reset` to clear all data
- **Export function**: Use `/admin/export` to dump all stored data

## 🔐 Authentication

- **Development Mode**: No authentication required
- **Token Simulation**: Accepts any bearer token for compatibility
- **Production Ready**: Easy to switch to real API with environment variables

## 🎯 Benefits

1. **🚀 Fast Development**: Test corpus features without waiting for production API
2. **🔧 Offline Capable**: Work on WhispNote features without internet
3. **📝 Full API Coverage**: All expected endpoints are implemented
4. **🧪 Easy Testing**: Comprehensive test suite included
5. **📱 UI Testing**: Complete WhispNote workflow testing possible

## 🔄 Switching to Production

When the real Swecha API becomes available:

1. Remove or comment out `USE_MOCK_SWECHA_API=true` from `.env`
2. Add your real `SWECHA_API_TOKEN` to `.env`
3. Restart WhispNote - it will automatically use the production API
4. Existing pending contributions will be submitted to the real API

## 📚 API Documentation

- **Interactive Docs**: http://localhost:8080/docs
- **ReDoc Format**: http://localhost:8080/redoc
- **OpenAPI Schema**: Available through FastAPI documentation

## 🐛 Troubleshooting

### Server Won't Start

```bash
# Install missing dependencies
uv add --optional enhanced fastapi uvicorn pydantic python-multipart

# Check for port conflicts
netstat -an | grep :8080
```

### WhispNote Not Using Mock API

```bash
# Verify environment variable
echo $USE_MOCK_SWECHA_API

# Check .env file
cat .env | grep USE_MOCK_SWECHA_API

# Restart WhispNote after changing .env
```

### API Responses Not Working

```bash
# Test server directly
curl http://localhost:8080/health

# Check server logs for errors
# Logs appear in terminal where server is running
```

## 📋 Development Notes

- **FastAPI Framework**: Modern Python API framework with automatic documentation
- **Pydantic Models**: Type validation and serialization
- **CORS Enabled**: Supports cross-origin requests for web UI testing
- **Error Handling**: Comprehensive exception handling and logging
- **Type Hints**: Full type annotations for better development experience

---

🎉 **Happy Development!** The mock server provides a complete testing environment for WhispNote corpus integration features.
