# 🎙️ WhispNote

**AI-Powered Multilingual Voice Notes for Indian Languages**

WhispNote is an offline-first, privacy-focused voice note application that leverages state-of-the-art AI models to transcribe, summarize, and organize voice notes in multiple Indian languages. Built with Streamlit, it provides a clean, intuitive interface for capturing and managing multilingual voice content.

## ✨ Features

### 🎤 Voice Recording & Transcription

- **Multilingual Support**: Hindi, Telugu, Tamil, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi, and English
- **Whisper Integration**: High-accuracy speech-to-text using OpenAI's Whisper model
- **Audio Format Support**: WAV, MP3, OGG, M4A, FLAC
- **Language Auto-detection**: Automatically detect the spoken language

### 📝 AI-Powered Text Processing

- **Smart Summarization**: Generate concise summaries using IndicBART
- **Keyword Extraction**: Automatically extract key topics and phrases using KeyBERT
- **Content Analysis**: Get insights into your voice notes with word frequency analysis

### 🔍 OCR Capabilities

- **Image Text Extraction**: Extract text from images using Tesseract and EasyOCR
- **Multilingual OCR**: Support for text in various Indian languages
- **Image Preprocessing**: Automatic image enhancement for better OCR accuracy

### 💾 Smart Storage & Organization

- **Offline-First**: All data stored locally by default
- **Note Management**: Search, filter, and organize notes by language, date, or content
- **Tagging System**: Add custom tags to categorize your notes
- **Privacy Controls**: Explicit consent required for any data sharing

### 📤 Flexible Export Options

- **Multiple Formats**: Export to Markdown, PDF, DOCX, TXT, or JSON
- **Batch Export**: Export multiple notes at once
- **Archive Creation**: Generate ZIP files with all your notes in various formats

### 📊 Corpus Contribution (Optional)

- **Language Research**: Contribute anonymized data to improve AI for Indian languages
- **Opt-in Only**: Data contribution requires explicit user consent
- **Statistics Dashboard**: Track contributions and corpus growth
- **Privacy-First**: All contributed data is anonymized

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- [UV](https://github.com/astral-sh/uv) installed (recommended) OR pip package manager
- Optional: GPU for faster processing

### Installation with UV (Recommended)

**UV** provides fast dependency resolution and management. Install it first:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or on Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

1. **Clone the repository**

```bash
git clone https://code.swecha.org/soai2025/techleads/soai-techlead-hackathon/whispnote.git
cd whispnote
```

2. **Install dependencies with UV**

```bash
# UV automatically creates virtual environment and installs dependencies
uv sync
```

3. **Run WhispNote with UV**

```bash
# Start the application
uv run streamlit run app.py

# Or use the provided launcher scripts
# Windows:
run.bat

# Linux/macOS:
./run.sh
```

### Alternative Installation with pip

1. **Clone the repository**

```bash
git clone https://code.swecha.org/soai2025/techleads/soai-techlead-hackathon/whispnote.git
cd whispnote
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Install system dependencies**

For OCR functionality:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-hin tesseract-ocr-tel

# macOS
brew install tesseract tesseract-lang

# Windows
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
```

For audio processing:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg portaudio19-dev

# macOS
brew install ffmpeg portaudio

# Windows
# Download FFmpeg from: https://ffmpeg.org/download.html
```

### Running WhispNote

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 🎯 Usage Guide

### Recording Voice Notes

1. **Select Language**: Choose your preferred language from the sidebar
2. **Upload Audio**: Use the file uploader to add your audio file
3. **Transcribe**: Click "Transcribe Audio" to convert speech to text
4. **Review & Edit**: Edit the transcription if needed
5. **Save**: Save your note to local storage

### Managing Notes

- **View Notes**: Navigate to the "My Notes" tab to see all saved notes
- **Search**: Use the search bar to find specific notes
- **Filter**: Filter notes by language
- **Export**: Export individual notes or create archives

### Text Processing

- **Summarization**: Use the "Summarize" tab to generate AI summaries
- **Keywords**: Extract important keywords and topics
- **Analysis**: Get insights into your note content

### OCR Processing

- **Upload Image**: Add images containing text
- **Extract Text**: Use OCR to convert image text to editable content
- **Save as Note**: Convert OCR results into voice notes

### Privacy Settings

- **Local Storage**: All notes are stored locally by default
- **Corpus Contribution**: Opt-in to contribute anonymized data for research
- **Data Control**: Full control over what data is shared

## 🔧 Configuration

### Model Configuration

Edit the model settings in the respective modules:

```python
# whisper_transcriber.py
transcriber = WhisperTranscriber(model_size="base")  # Options: tiny, base, small, medium, large

# summarizer.py
summarizer = IndicBARTSummarizer(model_name="ai4bharat/indicbart-ss")

# keyword_extractor.py
extractor = KeywordExtractor(model_name='sentence-transformers/all-MiniLM-L6-v2')
```

### Storage Configuration

```python
# storage.py
storage = StorageManager(base_dir="whispnote_data")  # Change storage location
```

## 📁 Project Structure

```
whispnote/
├── app.py                 # Main Streamlit application
├── whisper_transcriber.py # Speech-to-text functionality
├── summarizer.py          # Text summarization using IndicBART
├── keyword_extractor.py   # Keyword extraction using KeyBERT
├── ocr_reader.py          # OCR functionality
├── storage.py             # Data storage and management
├── export_utils.py        # Export functionality
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── CONTRIBUTING.md       # Contribution guidelines
├── LICENSE               # License file
└── whispnote_data/       # Local data storage (created automatically)
    ├── notes/            # Saved voice notes
    ├── corpus/           # Contributed corpus data (if opted-in)
    └── audio/            # Audio file storage
```

## 🌐 Deployment

### Streamlit Community Cloud

1. Push your code to GitLab
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitLab repository
4. Deploy with one click

### Hugging Face Spaces

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Choose Streamlit as the SDK
3. Upload your code
4. Add secrets for any API keys in Settings

### Local Network Deployment

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a virtual environment
3. Install development dependencies
4. Make your changes
5. Submit a merge request

### Areas for Contribution

- **Language Support**: Add support for more Indian languages
- **Model Integration**: Integrate new AI models for better accuracy
- **UI/UX**: Improve the user interface and experience
- **Performance**: Optimize processing speed and memory usage
- **Documentation**: Improve documentation and tutorials

## 📊 Supported Languages

| Language  | Code | Whisper | IndicBART | OCR |
| --------- | ---- | ------- | --------- | --- |
| English   | en   | ✅      | ✅        | ✅  |
| Hindi     | hi   | ✅      | ✅        | ✅  |
| Telugu    | te   | ✅      | ✅        | ✅  |
| Tamil     | ta   | ✅      | ✅        | ✅  |
| Bengali   | bn   | ✅      | ✅        | ✅  |
| Marathi   | mr   | ✅      | ✅        | ✅  |
| Gujarati  | gu   | ✅      | ✅        | ✅  |
| Kannada   | kn   | ✅      | ✅        | ✅  |
| Malayalam | ml   | ✅      | ✅        | ✅  |
| Punjabi   | pa   | ✅      | ✅        | ✅  |

## 🔒 Privacy & Security

### Data Privacy

- **Local Storage**: All notes are stored locally by default
- **No Tracking**: No user analytics or tracking
- **Explicit Consent**: Data sharing requires explicit user consent
- **Anonymization**: All contributed data is anonymized

### Security Features

- **Offline Capability**: Works completely offline
- **No External Dependencies**: Core functionality doesn't require internet
- **Open Source**: Full transparency with open-source code

## 📈 Performance

### System Requirements

- **Minimum**: 4GB RAM, 2GB storage
- **Recommended**: 8GB RAM, 5GB storage, GPU (optional)
- **Storage**: ~1GB for AI models, varies by usage

### Optimization Tips

- Use smaller Whisper models (tiny/base) for faster processing
- Enable GPU acceleration if available
- Regular cleanup of old temporary files

## 🐛 Troubleshooting

### Common Issues

**Whisper Model Loading Error**

```bash
# Solution: Install torch audio
pip install torchaudio
```

**OCR Not Working**

```bash
# Solution: Install Tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Windows: Download from UB-Mannheim
```

**Audio Processing Error**

```bash
# Solution: Install audio dependencies
pip install librosa soundfile pydub
```

### Getting Help

- Create an issue on GitHub
- Check the troubleshooting section
- Review system requirements
- Ensure all dependencies are installed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for the Whisper speech recognition model
- **AI4Bharat** for IndicBART multilingual models
- **Google** for Tesseract OCR
- **Streamlit** for the amazing web framework
- **Contributors** who help make WhispNote better

## 🚀 Roadmap

### Upcoming Features

- [ ] Real-time voice recording interface
- [ ] Advanced note linking and cross-references
- [ ] Voice note playback with synchronized transcripts
- [ ] Collaborative features for shared notebooks
- [ ] Advanced search with semantic similarity
- [ ] Integration with cloud storage providers
- [ ] Mobile app development
- [ ] API endpoints for third-party integrations

### Model Improvements

- [ ] Fine-tuned models for Indian English accents
- [ ] Improved punctuation and capitalization
- [ ] Better handling of code-switching
- [ ] Support for regional dialects

---

**Built with ❤️ for the Indian language community**

_WhispNote - Where your voice meets AI_
