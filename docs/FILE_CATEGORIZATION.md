# 📂 WhispNote File Categorization

## 🎯 Core Application Files

### 🚀 Main Application

- **`app.py`** - Main Streamlit application with 5-tab interface
- **`main.py`** - Alternative entry point or main module

### 🧠 AI/ML Processing Modules

- **`whisper_transcriber.py`** - Speech-to-text using OpenAI Whisper
- **`summarizer.py`** - Text summarization using IndicBART
- **`keyword_extractor.py`** - Keyword extraction using KeyBERT
- **`ocr_reader.py`** - Image text extraction using Tesseract/EasyOCR

### 💾 Data Management

- **`storage.py`** - Local data persistence and management
- **`export_utils.py`** - Export functionality for various formats

### 🌐 API Integration

- **`swecha_api.py`** - Swecha Telugu Corpus API integration
- **`swecha_config.py`** - Swecha API configuration and tokens

---

## 🧪 Testing & Quality Assurance

### 🔬 Test Files

- **`test_swecha_api.py`** - Swecha API integration tests
- **`test_auth_endpoints.py`** - Authentication endpoint tests
- **`test_comprehensive_endpoints.py`** - Comprehensive endpoint testing
- **`quick_test.py`** - Quick functionality verification
- **`swecha_endpoint_report.py`** - API endpoint status reporting

---

## 📚 Documentation

### 📖 Primary Documentation

- **`Readme.md`** - Main project README with comprehensive guide
- **`PROJECT_OVERVIEW.md`** - High-level project architecture and vision
- **`TECH_STACK.md`** - Technical stack and dependencies overview

### 📋 Project Management

- **`CONTRIBUTING.md`** - Contribution guidelines and workflows
- **`CHANGELOG.md`** - Version history and release notes
- **`LICENSE.md`** - AGPL-3.0 license terms and conditions

---

## ⚙️ Configuration & Dependencies

### 📦 Package Management

- **`pyproject.toml`** - UV project configuration and metadata
- **`requirements.txt`** - Python dependencies list
- **`uv.lock`** - UV dependency lock file
- **`.python-version`** - Python version specification

### 🚀 Launchers

- **`run.bat`** - Windows batch launcher script
- **`run.sh`** - Unix/Linux shell launcher script

---

## 🖥️ IDE & Development Tools

### 💻 VS Code Configuration (`.vscode/`)

- **`settings.json`** - Workspace settings and preferences
- **`extensions.json`** - Recommended VS Code extensions
- **`launch.json`** - Debug configurations
- **`tasks.json`** - Build and automation tasks

### 🔧 Development Environment

- **`.gitignore`** - Git ignore patterns
- **`.venv/`** - Python virtual environment directory

---

## 🏗️ GitLab CI/CD & Templates

### 📋 Issue Templates (`.gitlab/issue_templates/`)

- **`bug_report.md`** - Structured bug reporting template
- **`feature_request.md`** - Feature proposal template
- **`documentation.md`** - Documentation improvement template

### 🔀 Merge Request Templates (`.gitlab/merge_request_templates/`)

- **`default.md`** - General merge request template
- **`bug_fix.md`** - Bug fix specific template

### 🔄 GitLab Configuration

- **`.gitlab/`** - GitLab CI/CD and template directory

---

## 💽 Data & Storage

### 📁 Application Data (`whispnote_data/`)

- **`config.json`** - Application configuration settings
- **`notes/`** - Stored voice notes and transcriptions
- **`audio/`** - Audio file storage
- **`corpus/`** - Language corpus data
- **`pending_swecha_uploads/`** - Queued Telugu contributions

---

## 🗑️ Generated & Cache Files

### 🔄 Build Artifacts

- **`__pycache__/`** - Python bytecode cache
- **`.git/`** - Git repository metadata

---

## 📊 File Statistics Summary

| Category             | File Count   | Description                        |
| -------------------- | ------------ | ---------------------------------- |
| **Core Application** | 7 files      | Main app and AI processing modules |
| **Testing**          | 5 files      | Test suites and quality assurance  |
| **Documentation**    | 6 files      | Project docs and guides            |
| **Configuration**    | 6 files      | Dependencies and project setup     |
| **IDE Tools**        | 4 files      | VS Code workspace configuration    |
| **GitLab Templates** | 5 files      | CI/CD and collaboration templates  |
| **Data Storage**     | 5 items      | Local data and configuration       |
| **Generated Files**  | 3 items      | Cache and build artifacts          |
| **Total**            | **41 items** | Complete project structure         |

---

## 🎯 File Purpose Matrix

### 🟢 Essential Files (Cannot be deleted)

- `app.py`, `whisper_transcriber.py`, `summarizer.py`
- `pyproject.toml`, `requirements.txt`
- `Readme.md`, `LICENSE.md`

### 🟡 Important Files (Significant functionality)

- All AI/ML modules, API integration files
- Documentation suite, VS Code configuration
- Test files, GitLab templates

### 🔵 Optional Files (Nice to have)

- Launcher scripts (`run.bat`, `run.sh`)
- Cache directories, generated files
- Alternative entry points

### 🟠 Configuration Files (Environment specific)

- `.python-version`, `uv.lock`
- VS Code settings, GitLab templates
- Data storage configurations

---

## 🔍 Quick Navigation Guide

### For Developers

```
📂 Start Here: app.py (main application)
📂 Core Logic: whisper_transcriber.py, summarizer.py
📂 Setup: pyproject.toml, .vscode/
📂 Tests: test_*.py files
```

### For Users

```
📂 Getting Started: Readme.md
📂 Contributing: CONTRIBUTING.md
📂 License: LICENSE.md
📂 Run App: run.bat (Windows) or run.sh (Unix)
```

### For Maintainers

```
📂 Project Status: CHANGELOG.md, PROJECT_OVERVIEW.md
📂 CI/CD: .gitlab/ directory
📂 Dependencies: pyproject.toml, uv.lock
📂 Data: whispnote_data/ directory
```

---

_This categorization helps understand the project structure and locate specific functionality quickly._
