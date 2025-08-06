@echo off
REM WhispNote Launcher Script for Windows

echo 🎙️ Starting WhispNote - AI-Powered Multilingual Voice Notes
echo ============================================================
echo.
echo 📦 Using uv for dependency management...
echo 🚀 Launching Streamlit application...
echo.

REM Run the WhispNote application
uv run streamlit run app.py
