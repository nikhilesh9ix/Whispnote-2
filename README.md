# 🔊 WhispNote – Speak Freely. Learn Smartly.

**WhispNote** is an open-source, AI-powered voice note app that transforms your spoken thoughts into organized, intelligent notes — while contributing (with consent) to a growing multilingual corpus for Indian language AI research.

Designed for students, educators, creators, and everyday thinkers, WhispNote is your **AI companion for capturing, summarizing, and rediscovering knowledge** through voice.

---

## ✨ Key Features

### 🎙️ Voice Note Recording
- Record in any Indian language — no typing needed
- Simple, minimal interface for quick capture
- Works **offline-first** and syncs when back online
- Add optional images (e.g., lecture notes, book pages)

### 🤖 AI Superpowers
- **Transcription**: Converts speech to text using [Whisper](https://github.com/openai/whisper)
- **Summarization**: Multiple styles using [IndicBART](https://huggingface.co/ai4bharat/indicbart) or BART/T5
- **Keyword & Topic Extraction**: Powered by KeyBERT or BERTopic
- **OCR for Images**: Use [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) to convert photos into editable text

### 🧠 Study & Productivity Tools
- Smart note organization with tags, topics, and timestamps
- Custom markdown annotations, linked notes (`[[like this]]`), and comments
- AI-generated revision reminders and spaced repetition
- Built-in to-do and task manager from within your notes

### 🎯 Corpus Contribution
- Contribute your voice and text to a public Indian language corpus (with consent)
- App prompts encourage meaningful stories, proverbs, lectures, etc.
- View live stats of the corpus being built

### 📦 Exports & Sharing
- Export your notes as PDF, DOCX, Markdown, or plain text
- Share with study groups, classmates, or collaborators
- Google Drive / Notion / Calendar integrations (upcoming)

### 🛡️ Private by Default
- Local storage, explicit opt-in for corpus contributions
- Detailed consent and privacy settings built into the UI

---

## 🧱 Tech Stack

| Layer         | Technology                         |
|--------------|-------------------------------------|
| Frontend     | [Streamlit](https://streamlit.io/) |
| AI Models    | Whisper, IndicBART, Tesseract, KeyBERT |
| Backend      | Python                              |
| Hosting      | Hugging Face Spaces                 |
| Code Repo    | [code.swecha.org](https://code.swecha.org) |
