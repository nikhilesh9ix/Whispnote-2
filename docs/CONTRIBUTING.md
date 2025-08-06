# Contributing to WhispNote 🤝

Thank you for your interest in contributing to WhispNote! This document provides guidelines and information for contributors.

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**

- Harassment, trolling, or derogatory comments
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## How to Contribute

### Reporting Issues

- **Security Issues**: Report privately via email
- **Bug Reports**: Use the bug report template
- **Feature Requests**: Use the feature request template
- **Documentation**: Use the documentation template

### Development Setup

#### Prerequisites

- Python 3.8+
- UV package manager or pip
- Git
- VS Code (recommended)

#### Setup Steps

```bash
# 1. Fork the repository on GitLab

# 2. Clone your fork
git clone https://code.swecha.org/yourusername/whispnote.git
cd whispnote

# 3. Set up upstream remote
git remote add upstream https://code.swecha.org/soai2025/techleads/soai-techlead-hackathon/whispnote.git

# 4. Install dependencies with UV
uv sync

# 5. Install development dependencies
uv add --dev pytest black ruff mypy pre-commit

# 6. Set up pre-commit hooks
uv run pre-commit install

# 7. Run tests to verify setup
uv run pytest
```

#### Alternative: pip setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Development Workflow

#### 1. Create a Feature Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
```

#### 2. Development Guidelines

**Code Style:**

- Follow PEP 8 for Python code
- Use Black for code formatting
- Use Ruff for linting
- Add type hints where appropriate
- Write descriptive docstrings

**Testing:**

- Write tests for new functionality
- Maintain or improve test coverage
- Run tests before committing: `uv run pytest`

**Documentation:**

- Update README.md if needed
- Add docstrings to new functions/classes
- Update CHANGELOG.md for user-facing changes

#### 3. Commit Guidelines

```bash
# Format code
uv run black .
uv run ruff check . --fix

# Run tests
uv run pytest

# Commit with descriptive message
git add .
git commit -m "feat: add voice recording validation

- Add input validation for audio files
- Improve error handling for unsupported formats
- Update tests for new validation logic"
```

**Commit Message Format:**

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### 4. Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_transcriber.py

# Run tests with verbose output
uv run pytest -v
```

#### 5. Submit Merge Request

1. Push your branch: `git push origin feature/your-feature-name`
2. Open a merge request on GitLab
3. Use the appropriate MR template
4. Link related issues
5. Request review from maintainers

### Project Structure

```
whispnote2/
├── 📂 src/                        # Source code modules
│   ├── __init__.py                # Main package init
│   ├── 🧠 ai/                     # AI/ML processing modules
│   │   ├── __init__.py
│   │   ├── whisper_transcriber.py # Speech-to-text (Whisper)
│   │   ├── summarizer.py          # Text summarization (IndicBART)
│   │   ├── keyword_extractor.py   # Keyword extraction (KeyBERT)
│   │   └── ocr_reader.py          # Image OCR (Tesseract/EasyOCR)
│   ├── 🌐 api/                    # External API integrations
│   │   ├── __init__.py
│   │   ├── swecha_api.py          # Swecha Corpus API
│   │   └── swecha_config.py       # API configuration
│   └── 🔧 utils/                  # Utility modules
│       ├── __init__.py
│       ├── storage.py             # Data persistence
│       └── export_utils.py        # Export functionality
├── 🧪 tests/                      # Test suite
│   ├── test_swecha_api.py         # API integration tests
│   ├── test_auth_endpoints.py     # Authentication tests
│   ├── test_comprehensive_endpoints.py # Comprehensive endpoint tests
│   ├── quick_test.py              # Quick functionality test
│   └── swecha_endpoint_report.py  # Endpoint status reporting
├── 📚 docs/                       # Documentation
│   ├── CONTRIBUTING.md            # This file
│   ├── CHANGELOG.md               # Version history
│   ├── PROJECT_OVERVIEW.md        # Project architecture
│   ├── TECH_STACK.md              # Technical stack info
│   ├── LICENSE.md                 # AGPL-3.0 license
│   └── FILE_CATEGORIZATION.md     # File organization guide
├── 🚀 scripts/                    # Launcher scripts
│   ├── run.bat                    # Windows launcher
│   └── run.sh                     # Unix/Linux launcher
├── 🖥️ .vscode/                    # VS Code configuration
│   ├── settings.json              # Workspace settings
│   ├── extensions.json            # Recommended extensions
│   ├── launch.json                # Debug configurations
│   └── tasks.json                 # Build tasks
├── 🔧 .gitlab/                    # GitLab CI/CD
│   ├── issue_templates/           # Issue templates
│   └── merge_request_templates/   # MR templates
├── 💾 whispnote_data/             # Application data
│   ├── config.json               # App configuration
│   ├── notes/                    # Stored notes
│   ├── audio/                    # Audio files
│   ├── corpus/                   # Language corpus
│   └── pending_swecha_uploads/   # Queued uploads
├── 📱 app.py                      # Main Streamlit application
├── main.py                       # Alternative entry point
├── 📖 Readme.md                   # Main project README
├── ⚙️ pyproject.toml              # Project configuration (UV)
├── requirements.txt              # Dependencies (pip)
├── uv.lock                       # UV lock file
├── .python-version               # Python version
├── .gitignore                    # Git ignore patterns
├── __pycache__/                  # Python cache (generated)
└── .venv/                        # Virtual environment
```

### Adding New Features

#### Voice Processing Features

1. **Audio Preprocessing**: Enhance audio quality before transcription
2. **Speaker Identification**: Detect multiple speakers in recordings
3. **Real-time Transcription**: Live transcription during recording

#### AI/ML Enhancements

1. **Custom Models**: Add support for domain-specific models
2. **Language Detection**: Improve automatic language detection
3. **Sentiment Analysis**: Add emotion/sentiment detection

#### UI/UX Improvements

1. **Mobile Responsiveness**: Optimize for mobile devices
2. **Dark Mode**: Add theme switching
3. **Accessibility**: Improve screen reader support

#### Integration Features

1. **Cloud Storage**: Add cloud backup options
2. **API Integrations**: Connect with external services
3. **Export Formats**: Add new export options

### Code Quality Standards

#### Python Code

- **Type Hints**: Use type annotations
- **Docstrings**: Follow Google or NumPy style
- **Error Handling**: Implement proper exception handling
- **Logging**: Use structured logging
- **Security**: Validate all inputs

#### Example Function:

```python
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def transcribe_audio(
    audio_path: str,
    language: str = "auto"
) -> Dict[str, Any]:
    """
    Transcribe audio file to text using Whisper.

    Args:
        audio_path: Path to audio file
        language: Language code or "auto" for detection

    Returns:
        Dictionary containing transcription and metadata

    Raises:
        FileNotFoundError: If audio file doesn't exist
        ValueError: If language code is invalid
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise
```

#### Testing Standards

```python
import pytest
from unittest.mock import Mock, patch
from src.ai.whisper_transcriber import WhisperTranscriber

def test_transcribe_audio_success():
    """Test successful audio transcription."""
    # Arrange
    transcriber = WhisperTranscriber()
    audio_path = "test_audio.wav"
    expected_result = {"text": "Hello world", "confidence": 0.95}

    # Act
    with patch('whisper.load_model') as mock_model:
        mock_model.return_value.transcribe.return_value = expected_result
        result = transcriber.transcribe(audio_path)

    # Assert
    assert result["text"] == "Hello world"
    assert result["confidence"] == 0.95

def test_transcribe_audio_file_not_found():
    """Test transcription with missing file."""
    # Arrange
    transcriber = WhisperTranscriber()
    audio_path = "nonexistent.wav"

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        transcriber.transcribe(audio_path)
```

### Documentation

#### Types of Documentation

1. **API Documentation**: Function/class docstrings
2. **User Guide**: Usage instructions and tutorials
3. **Developer Guide**: Architecture and development setup
4. **Changelog**: User-facing changes and releases

#### Writing Guidelines

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Update existing docs when making changes

### Review Process

#### For Contributors

1. **Self-Review**: Review your own changes first
2. **Test Coverage**: Ensure adequate test coverage
3. **Documentation**: Update relevant documentation
4. **Breaking Changes**: Clearly mark and document

#### For Reviewers

1. **Code Quality**: Check adherence to standards
2. **Functionality**: Verify features work as expected
3. **Performance**: Consider performance implications
4. **Security**: Review for security issues

### Release Process

1. **Version Bump**: Update version in pyproject.toml
2. **Changelog**: Update CHANGELOG.md
3. **Testing**: Run full test suite
4. **Documentation**: Update documentation
5. **Tag Release**: Create git tag
6. **Deploy**: Deploy to relevant platforms

### Community

#### Communication Channels

- **Issues**: For bug reports and feature requests
- **Merge Requests**: For code review and discussion
- **Discussions**: For general questions and ideas

#### Recognition

- Contributors are recognized in CHANGELOG.md
- Significant contributions may be highlighted in releases
- All contributors are welcome in our community

### Getting Help

#### For Development Issues

1. Check existing issues and documentation
2. Search previous discussions
3. Create a new issue with detailed information
4. Tag relevant maintainers if urgent

#### For Questions

1. Check the FAQ in documentation
2. Search existing discussions
3. Ask in project discussions
4. Contact maintainers directly for sensitive issues

## Thank You! 🙏

Your contributions help make WhispNote better for everyone. Whether you're reporting bugs, suggesting features, improving documentation, or contributing code, every contribution is valuable and appreciated!

---

**Happy Contributing!** 🚀
