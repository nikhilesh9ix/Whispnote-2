# 📁 WhispNote Organized File Structure

## 📍 **Repository Information**

- **Official Repository**: [https://code.swecha.org/soai2025/techleads/soai-techlead-hackathon/whispnote](https://code.swecha.org/soai2025/techleads/soai-techlead-hackathon/whispnote)
- **License**: AGPL-3.0
- **Maintainer**: Swecha Team
- **Project Type**: AI-powered multilingual voice notes application

## 🎯 **New Project Structure**

```
whispnote2/
├── 📂 src/                              # Source code modules
│   ├── __init__.py                      # Main package init
│   ├── 🧠 ai/                           # AI/ML processing modules
│   │   ├── __init__.py
│   │   ├── whisper_transcriber.py       # Speech-to-text (Whisper)
│   │   ├── summarizer.py                # Text summarization (IndicBART)
│   │   ├── keyword_extractor.py         # Keyword extraction (KeyBERT)
│   │   └── ocr_reader.py                # Image OCR (Tesseract/EasyOCR)
│   ├── 🌐 api/                          # External API integrations
│   │   ├── __init__.py
│   │   ├── swecha_api.py                # Swecha Corpus API
│   │   └── swecha_config.py             # API configuration
│   └── 🔧 utils/                        # Utility modules
│       ├── __init__.py
│       ├── storage.py                   # Data persistence
│       └── export_utils.py              # Export functionality
├── 🧪 tests/                            # Test suite
│   ├── test_swecha_api.py               # API integration tests
│   ├── test_auth_endpoints.py           # Authentication tests
│   ├── test_comprehensive_endpoints.py  # Comprehensive endpoint tests
│   ├── quick_test.py                    # Quick functionality test
│   └── swecha_endpoint_report.py        # Endpoint status reporting
├── 📚 docs/                             # Documentation
│   ├── CONTRIBUTING.md                  # Contribution guidelines
│   ├── CHANGELOG.md                     # Version history
│   ├── PROJECT_OVERVIEW.md              # Project architecture
│   ├── TECH_STACK.md                    # Technical stack info
│   ├── LICENSE.md                       # AGPL-3.0 license
│   └── FILE_CATEGORIZATION.md           # File organization guide
├── 🚀 scripts/                          # Launcher scripts
│   ├── run.bat                          # Windows launcher
│   └── run.sh                           # Unix/Linux launcher
├── 🖥️ .vscode/                          # VS Code configuration
│   ├── settings.json                    # Workspace settings
│   ├── extensions.json                  # Recommended extensions
│   ├── launch.json                      # Debug configurations
│   └── tasks.json                       # Build tasks
├── 🔧 .gitlab/                          # GitLab CI/CD
│   ├── issue_templates/                 # Issue templates
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── documentation.md
│   └── merge_request_templates/         # MR templates
│       ├── default.md
│       └── bug_fix.md
├── 💾 whispnote_data/                   # Application data
│   ├── config.json                     # App configuration
│   ├── notes/                          # Stored notes
│   ├── audio/                          # Audio files
│   ├── corpus/                         # Language corpus
│   └── pending_swecha_uploads/         # Queued uploads
├── 📱 app.py                            # Main Streamlit application
├── main.py                              # Alternative entry point
├── 📖 Readme.md                         # Main project README
├── ⚙️ pyproject.toml                    # Project configuration (UV)
├── requirements.txt                     # Dependencies (pip)
├── uv.lock                              # UV lock file
├── .python-version                      # Python version
├── .gitignore                           # Git ignore patterns
├── __pycache__/                         # Python cache (generated)
└── .venv/                               # Virtual environment
```

## 🎯 **Benefits of New Structure**

### 🧩 **Modular Organization**

- **Logical separation** of concerns
- **Clear dependencies** between modules
- **Easy navigation** for developers
- **Scalable architecture** for future growth

### 📦 **Python Package Structure**

- **Proper Python packages** with `__init__.py` files
- **Clean import paths** (`from src.ai.whisper_transcriber import...`)
- **Package documentation** in each module
- **Version management** centralized

### 🔧 **Development Experience**

- **IDE support** improved with proper package structure
- **Testing organization** with dedicated test directory
- **Documentation centralization** in docs folder
- **Script organization** in scripts directory

### 🏗️ **Professional Standards**

- **Industry-standard** project layout
- **Open source best practices** followed
- **Contribution-friendly** structure
- **Maintainable codebase** organization

## 📊 **Import Path Changes**

### ✅ **Updated Import Statements**

#### In `app.py`:

```python
# OLD imports
from whisper_transcriber import WhisperTranscriber
from summarizer import IndicBARTSummarizer
from keyword_extractor import KeywordExtractor
from ocr_reader import OCRReader
from storage import StorageManager
from export_utils import ExportUtils

# NEW imports
from src.ai.whisper_transcriber import WhisperTranscriber
from src.ai.summarizer import IndicBARTSummarizer
from src.ai.keyword_extractor import KeywordExtractor
from src.ai.ocr_reader import OCRReader
from src.utils.storage import StorageManager
from src.utils.export_utils import ExportUtils
```

#### In test files:

```python
# OLD imports
from swecha_api import WhispNoteSwechaIntegration
from swecha_config import SWECHA_API_TOKEN

# NEW imports
from src.api.swecha_api import WhispNoteSwechaIntegration
from src.api.swecha_config import SWECHA_API_TOKEN
```

### 📝 **Updated Configuration**

#### `pyproject.toml` changes:

- **Version**: Updated to `2.0.0`
- **License**: Changed to `AGPL-3.0`
- **Authors**: Updated to Swecha Team
- **README**: Updated path reference

## 🚀 **Running the Application**

### Method 1: Direct execution

```bash
python app.py
# OR
uv run streamlit run app.py
```

### Method 2: Using launcher scripts

```bash
# Windows
scripts\run.bat

# Unix/Linux/macOS
scripts/run.sh
```

### Method 3: UV task runner

```bash
uv run streamlit run app.py --server.port 8506
```

## 🧪 **Running Tests**

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_swecha_api.py

# With UV
uv run pytest tests/
```

## 📂 **Directory Purposes**

| Directory         | Purpose       | Contents                         |
| ----------------- | ------------- | -------------------------------- |
| `src/ai/`         | AI/ML modules | Whisper, IndicBART, KeyBERT, OCR |
| `src/api/`        | External APIs | Swecha integration, config       |
| `src/utils/`      | Utilities     | Storage, export, helpers         |
| `tests/`          | Test suite    | Unit tests, integration tests    |
| `docs/`           | Documentation | Guides, architecture, license    |
| `scripts/`        | Launchers     | Platform-specific run scripts    |
| `.vscode/`        | IDE config    | VS Code workspace settings       |
| `.gitlab/`        | CI/CD         | Templates, automation            |
| `whispnote_data/` | App data      | Notes, audio, configuration      |

## 🔄 **Migration Complete**

✅ **All files successfully organized**
✅ **Import paths updated**
✅ **Package structure created**
✅ **Configuration updated**
✅ **Documentation reorganized**
✅ **Repository URLs updated**

## 🚀 **Quick Start with New Structure**

```bash
# Clone the repository
git clone https://code.swecha.org/soai2025/techleads/soai-techlead-hackathon/whispnote.git
cd whispnote

# Install dependencies with UV (recommended)
uv sync

# Run the application
uv run streamlit run app.py --server.port 8506

# Or use launcher scripts
# Windows: scripts\run.bat
# Unix/Linux: scripts/run.sh
```

The WhispNote project now follows modern Python project standards with a clean, maintainable, and professional structure! 🎉
