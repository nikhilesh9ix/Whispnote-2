# WhispNote 2.0 - Quick Reference Guide

## 🎯 **Project Summary**
WhispNote is an AI-powered multilingual voice note application that converts speech to text, enhances the content using NLP, and contributes to the Swecha Telugu corpus.

## 🔧 **Core Technologies**
- **Frontend**: Streamlit + WebRTC
- **AI**: OpenAI Whisper + IndicBART + KeyBERT
- **NLP**: TextBlob + LanguageTool + NLTK
- **Storage**: Swecha API (external database)
- **Export**: PDF, DOCX, TXT, JSON

## 📋 **8-Step Process Flow**

1. **Authentication** → Swecha login/signup with JWT tokens
2. **Audio Capture** → WebRTC microphone recording
3. **Speech-to-Text** → Whisper transcription (90+ languages)
4. **Text Enhancement** → NLP pipeline (spell/grammar check)
5. **User Review** → Interactive editing interface
6. **AI Processing** → Summarization + keyword extraction
7. **Storage** → Swecha API database contribution
8. **Export** → Multiple format document generation

## 🛠 **Tech Stack Breakdown**

### AI/ML Models
- **Whisper**: Speech recognition (tiny to large models)
- **IndicBART**: Indian language summarization
- **KeyBERT**: Semantic keyword extraction
- **TextBlob**: Spell checking
- **LanguageTool**: Grammar checking

### Infrastructure
- **Python 3.8+**: Core language
- **UV**: Fast package management
- **Streamlit**: Web framework
- **PyTorch**: ML framework
- **Bearer Token**: API authentication

### Supported Languages
English, Hindi, Telugu, Tamil, Bengali, Gujarati, Marathi, Punjabi, Malayalam, Kannada, Urdu, Nepali + 80 more

## 🚀 **Quick Setup**
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup project
git clone <repo>
cd whispnote2
uv sync

# Download NLTK data
uv run python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"

# Run app
uv run streamlit run app.py --server.port 8506
```

## 📊 **Performance Metrics**
- **Transcription**: 1-5 seconds per audio minute
- **Text Processing**: <1 second
- **Accuracy**: 85-95% for clear speech
- **Memory**: 2-8GB depending on Whisper model

## 🎯 **Key Features**
- Real-time multilingual transcription
- Intelligent text cleaning and enhancement
- Swecha corpus contribution
- Multiple export formats
- User authentication and session management
- OCR support for images
- Keyword extraction and summarization

## 🔒 **Security & Privacy**
- No local data storage
- HTTPS/TLS encryption
- JWT token authentication
- User consent for corpus contribution
- Input validation and sanitization

## 📈 **Use Cases**
- Meeting transcription
- Study notes and lectures
- Content creation
- Accessibility tools
- Language learning
- Research documentation
- Telugu corpus building

## 🤝 **Contributing**
- **License**: AGPL-3.0
- **Repository**: Active GitHub development
- **Community**: Swecha open source project
- **Corpus**: Telugu language preservation

---
**Version**: 2.0.0 | **Updated**: August 27, 2025 | **Status**: Active Development
