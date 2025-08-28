import os
import uuid
from datetime import datetime
from typing import Any, Dict

import pandas as pd
import streamlit as st
import streamlit.components.v1 as st_components

from src.ai.llama_summarizer import AdvancedAISummarizer
from src.ai.ocr_reader import OCRReader

# Import custom modules
from src.ai.whisper_transcriber import WhisperTranscriber
from src.api.swecha_auth_manager import SwechaIntegrationManager
from src.utils.export_utils import ExportUtils
from src.utils.swecha_storage import SwechaStorageManager
from src.utils.text_processor import TranscriptionProcessor

# Page config
st.set_page_config(
    page_title="WhispNote - AI Voice Notes",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize session state
def init_session_state() -> None:
    if "notes" not in st.session_state:
        st.session_state.notes = []
    if "current_note" not in st.session_state:
        st.session_state.current_note = None
    if "privacy_consent" not in st.session_state:
        st.session_state.privacy_consent = False
    if "corpus_contributions" not in st.session_state:
        st.session_state.corpus_contributions = 0

    # Swecha authentication state
    if "swecha_logged_in" not in st.session_state:
        st.session_state.swecha_logged_in = False
    if "swecha_token" not in st.session_state:
        st.session_state.swecha_token = None
    if "swecha_user_data" not in st.session_state:
        st.session_state.swecha_user_data = {}
    if "show_swecha_login" not in st.session_state:
        st.session_state.show_swecha_login = False
    if "show_swecha_signup" not in st.session_state:
        st.session_state.show_swecha_signup = False
    if "swecha_notes" not in st.session_state:
        st.session_state.swecha_notes = {}


# Initialize components
@st.cache_resource
def load_components() -> Dict[str, Any]:
    """Load all components with error handling"""
    components = {}

    try:
        components["transcriber"] = WhisperTranscriber()
    except Exception as e:
        st.error(f"Failed to load Whisper transcriber: {str(e)}")
        components["transcriber"] = None

    try:
        components["llama_ai"] = AdvancedAISummarizer()
        st.success("🦙 LLaMA 3.1 AI processor loaded successfully!")
    except Exception as e:
        st.error(f"Failed to load LLaMA AI processor: {str(e)}")
        components["llama_ai"] = None

    try:
        components["ocr_reader"] = OCRReader()
    except Exception as e:
        st.warning(f"Failed to load OCR reader: {str(e)}")
        components["ocr_reader"] = None

    try:
        components["storage"] = SwechaStorageManager()
    except Exception as e:
        st.error(f"Failed to load storage manager: {str(e)}")
        components["storage"] = None

    try:
        components["export_utils"] = ExportUtils()
    except Exception as e:
        st.warning(f"Failed to load export utils: {str(e)}")
        components["export_utils"] = None

    try:
        components["text_processor"] = TranscriptionProcessor()
    except Exception as e:
        st.warning(f"Failed to load text processor: {str(e)}")
        components["text_processor"] = None

    try:
        components["swecha"] = SwechaIntegrationManager()
    except Exception as e:
        st.error(f"Failed to load Swecha integration: {str(e)}")
        components["swecha"] = None

    return components


def main() -> None:
    init_session_state()
    components = load_components()

    # Custom CSS
    st.markdown(
        """
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .note-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .privacy-notice {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .corpus-stats {
        background-color: #f0f8f0;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header
    st.markdown("<h1 class='main-header'>🎙️ WhispNote</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #666;'>AI-Powered Multilingual Voice Notes</p>",
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        # Language selection
        language_options = {
            "Hindi": "hi",
            "Telugu": "te",
            "Tamil": "ta",
            "Bengali": "bn",
            "Marathi": "mr",
            "Gujarati": "gu",
            "Kannada": "kn",
            "Malayalam": "ml",
            "Punjabi": "pa",
            "English": "en",
        }

        selected_language = st.selectbox(
            "Select Language",
            options=list(language_options.keys()),
            index=9,  # Default to English
        )
        language_code = language_options[selected_language]

        # Privacy settings
        st.subheader("Privacy Settings")
        privacy_consent = st.checkbox(
            "I consent to contribute my data to the multilingual corpus",
            value=st.session_state.privacy_consent,
            help="Your audio and transcription will be anonymized and used to improve AI for Indian languages",
        )
        st.session_state.privacy_consent = privacy_consent

        if privacy_consent:
            st.success("✅ Contributing to corpus")
        else:
            st.info("🔒 Private mode - data stays local")

        # Swecha API Integration
        st.subheader("🌟 Swecha Corpus")
        swecha_manager = components["swecha"]

        if swecha_manager.is_logged_in():
            swecha_manager.show_user_info()
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔐 Login to Swecha"):
                    st.session_state.show_swecha_login = True
                    st.session_state.show_swecha_signup = False
            with col2:
                if st.button("📝 Sign Up for Swecha"):
                    st.session_state.show_swecha_signup = True
                    st.session_state.show_swecha_login = False

        # Show login form if requested
        if st.session_state.get('show_swecha_login', False) and swecha_manager.show_login_form():
            st.session_state.show_swecha_login = False

        # Show signup form if requested
        if st.session_state.get('show_swecha_signup', False) and swecha_manager.show_signup_form():
            st.session_state.show_swecha_signup = False

        # Privacy Information Section
        st.subheader("🔒 Privacy & Storage")
        with st.expander("Storage Information", expanded=True):
            st.markdown("""
            **WhispNote uses Swecha API for all data storage:**

            • **Cloud Storage:** All notes stored securely via Swecha API
            • **Account Required:** Create a free Swecha account or login to access all features
            • **Secure Authentication:** Bearer token-based authentication
            • **Telugu Corpus:** Your contributions help build the Swecha Telugu language corpus
            • **Data Privacy:** Your data is handled according to Swecha's privacy policy
            • **Open Source:** Transparent and community-driven
            """)

        # App info
        st.subheader("About")
        st.info("""
        **WhispNote** is a cloud-based voice note app powered by Swecha that:
        - Records and transcribes speech in Indian languages
        - Summarizes content using AI
        - Extracts keywords and topics
        - Supports OCR for image text
        - Contributes to Telugu language corpus
        """)

    # Check authentication status
    swecha_manager = components["swecha"]
    if not swecha_manager.is_logged_in():
        st.warning("🔐 **Authentication Required**")
        st.info("""
        ### Welcome to WhispNote! 🎙️

        To access all features and contribute to the Swecha Telugu corpus, please:

        - **Login** if you already have a Swecha account
        - **Sign Up** to create a new free account

        Use the sidebar authentication options to get started.
        """)
        st.stop()

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🎙️ Record", "📝 My Notes", "📊 Summarize", "🔍 OCR", "📈 Stats"]
    )

    with tab1:
        st.header("Record Voice Note")

        # Choose recording method
        recording_method = st.radio(
            "Choose recording method:",
            ("🎙️ Record with Device", "📁 Upload Audio File"),
            horizontal=True,
        )

        if recording_method == "🎙️ Record with Device":
            st.subheader("Device Recording Instructions")

            # Instructions for recording
            st.info("""
            **How to record audio:**
            1. Use your device's built-in voice recorder app
            2. Record your voice note in your preferred language
            3. Save the recording as an audio file (WAV, MP3, etc.)
            4. Upload the file below using the file uploader

            **Popular voice recording apps:**
            - 📱 **Mobile**: Voice Recorder, Voice Memos (iOS), Samsung Voice Recorder
            - 💻 **Windows**: Voice Recorder app, Audacity
            - 🖥️ **Mac**: Voice Memos, QuickTime Player
            - 🐧 **Linux**: GNOME Sound Recorder, Audacity
            """)

            st.markdown("---")

            # File uploader for device recordings
            device_audio = st.file_uploader(
                "Upload your device recording here:",
                type=["wav", "mp3", "ogg", "m4a", "flac", "aac"],
                help="Upload the audio file you recorded with your device",
                key="device_recording_upload",
            )

            if device_audio is not None:
                st.audio(device_audio)

                # Save uploaded file temporarily
                temp_audio_path = f"temp_device_audio_{uuid.uuid4().hex}.wav"
                with open(temp_audio_path, "wb") as f:
                    f.write(device_audio.read())

                # Transcription
                st.subheader("Step 2: Transcribe Recording")
                if st.button("🔤 Transcribe Device Recording", type="primary"):
                    with st.spinner(
                        f"Transcribing device recording in {selected_language}..."
                    ):
                        try:
                            # Step 1: Transcribe
                            transcription = components["transcriber"].transcribe(
                                temp_audio_path, language=language_code
                            )

                            if transcription:
                                # Store transcription in session state
                                st.session_state["device_transcription"] = transcription
                                st.session_state["device_audio_path"] = temp_audio_path
                                st.session_state["device_language_code"] = language_code
                                st.success("✅ Transcription completed!")
                                st.rerun()

                        except Exception as e:
                            st.error(f"Error during transcription: {str(e)}")

                        finally:
                            # Clean up temp file
                            if os.path.exists(temp_audio_path):
                                os.remove(temp_audio_path)

                # Show processing UI if transcription exists
                if "device_transcription" in st.session_state:
                    st.subheader("Step 3: Review and Clean Text")
                    transcription = st.session_state["device_transcription"]
                    language_code = st.session_state["device_language_code"]

                    # Processing options
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        processing_method = st.radio(
                            "Choose processing method:",
                            ["🔧 Traditional NLP", "🤖 AI-Powered (Llama 3.1 405B)"],
                            help="Traditional: Fast, rule-based cleaning. AI: Advanced context-aware enhancement.",
                            key="device_processing_method"
                        )

                    with col2:
                        if st.button("🧹 Process Text", type="primary", key="device_process_text"):
                            use_ai = processing_method.startswith("🤖")

                            with st.spinner(f"{'🤖 AI processing' if use_ai else '🔧 Traditional processing'}..."):
                                cleaning_result = components["text_processor"].clean_transcription(
                                    transcription, language=language_code, use_ai=use_ai
                                )

                            st.session_state["current_cleaning_result"] = cleaning_result

                    # Show results if available
                    if "current_cleaning_result" in st.session_state:
                        cleaning_result = st.session_state["current_cleaning_result"]

                        # Show processing method used
                        method_used = cleaning_result.get('processing_method', 'traditional_nlp')
                        if method_used == 'ai_enhanced':
                            st.success(f"✨ Enhanced with {cleaning_result.get('ai_model', 'AI')}")
                        else:
                            st.info("🔧 Processed with traditional NLP methods")

                        # Show cleaning statistics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Original Words", cleaning_result['word_count_original'])
                        with col2:
                            st.metric("Cleaned Words", cleaning_result['word_count_cleaned'])
                        with col3:
                            st.metric("Confidence", f"{cleaning_result['confidence_score']:.1%}")
                        with col4:
                            reduction = cleaning_result.get('reduction_percentage', 0)
                            st.metric("Reduction", f"{reduction:.1f}%")

                        # Show improvements made
                        if cleaning_result.get('processing_steps'):
                            with st.expander("🔍 Processing Details", expanded=False):
                                for step in cleaning_result['processing_steps']:
                                    st.text(f"✓ {step}")

                        # Show spelling/grammar corrections
                        if cleaning_result.get('spelling_corrections'):
                            with st.expander(f"📝 Spelling Corrections ({len(cleaning_result['spelling_corrections'])})", expanded=False):
                                for correction in cleaning_result['spelling_corrections'][:10]:
                                    st.text(f"• {correction['original']} → {correction['corrected']}")

                        # Show what was removed (for traditional processing)
                        if cleaning_result.get('removed_elements'):
                            with st.expander(f"🗑️ Removed {len(cleaning_result['removed_elements'])} elements", expanded=False):
                                for item in cleaning_result['removed_elements'][:10]:
                                    st.text(f"• {item}")
                                if len(cleaning_result['removed_elements']) > 10:
                                    st.text(f"... and {len(cleaning_result['removed_elements']) - 10} more")

                        # Editable text areas for comparison
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("🔍 Original Transcription")
                            st.text_area(
                                "Original:",
                                value=transcription,  # Use the original transcription
                                height=150,
                                key="device_original_transcription",
                                disabled=True
                            )

                        with col2:
                            st.subheader("✨ Enhanced Transcription")
                            transcription_text = st.text_area(
                                "Enhanced (editable):",
                                value=cleaning_result['cleaned'],
                                height=150,
                                key="device_transcription_edit",
                                help="Review and edit the enhanced transcription before saving"
                            )
                    else:
                        # No processing done yet, show original transcription for editing
                        st.subheader("📝 Transcription")
                        transcription_text = st.text_area(
                            "Transcribed text (click 'Process Text' above to enhance):",
                            value=transcription,
                            height=150,
                            key="device_raw_transcription",
                            help="Raw transcription - use processing options above to enhance"
                        )

                    # Step 4: Save and Summarize
                    st.subheader("Step 4: Save and Process")

                    col1, col2 = st.columns(2)

                    with col1:
                        # Save note option
                        if st.button(
                            "📝 Save Note", key="save_device_recording", type="primary"
                        ):
                            # Get the final transcription text safely
                            if "current_cleaning_result" in st.session_state:
                                # Try to get edited transcription, fallback to cleaned version
                                transcription_text = st.session_state.get("device_transcription_edit", st.session_state["current_cleaning_result"].get('cleaned', transcription))
                                final_transcription = transcription_text
                            else:
                                # Try to get raw transcription edit, fallback to original
                                transcription_text = st.session_state.get("device_raw_transcription", transcription)
                                final_transcription = transcription_text

                            # Validate we have required data
                            if not final_transcription or not final_transcription.strip():
                                st.error("❌ No transcription text to save!")
                            elif not transcription or not transcription.strip():
                                st.error("❌ Original transcription is missing!")
                            else:
                                # Generate summary and keywords before saving
                                with st.spinner("🔄 Generating summary and keywords..."):
                                    try:
                                        # Save audio file permanently
                                        permanent_audio_path = f"whispnote_data/audio/audio_{uuid.uuid4().hex}_{device_audio.name}"
                                        os.makedirs(os.path.dirname(permanent_audio_path), exist_ok=True)

                                        # Copy temp audio to permanent location
                                        import shutil
                                        if "device_audio_path" in st.session_state and os.path.exists(st.session_state["device_audio_path"]):
                                            shutil.copy2(st.session_state["device_audio_path"], permanent_audio_path)
                                        else:
                                            # If temp file is gone, recreate from uploaded file
                                            try:
                                                device_audio.seek(0)  # Reset file pointer
                                                with open(permanent_audio_path, "wb") as f:
                                                    f.write(device_audio.read())
                                            except Exception as audio_error:
                                                # If we can't read the uploaded file, skip audio saving
                                                st.warning(f"Could not save audio file: {str(audio_error)}")
                                                permanent_audio_path = None

                                        # Generate summary and keywords with error handling
                                        summary = None
                                        keywords = []

                                        # Use LLaMA 3.1 for AI-powered summary and keyword extraction
                                        if components["llama_ai"] and final_transcription and len(final_transcription.split()) > 10:
                                            try:
                                                st.info("� Using LLaMA 3.1 for AI-powered summary and keyword extraction...")
                                                # Use the combined method for efficiency
                                                summary, keywords = components["llama_ai"].generate_summary_and_keywords(
                                                    final_transcription, language=language_code
                                                )
                                                if summary:
                                                    st.success("✅ LLaMA 3.1 processing completed!")
                                            except Exception as llama_error:
                                                st.warning(f"LLaMA AI processing failed: {str(llama_error)}")
                                                summary = None
                                                keywords = []

                                        # If no summary/keywords generated, show info
                                        if not summary:
                                            st.info("💡 Add OpenRouter API key to enable advanced AI summarization")
                                        if not keywords:
                                            st.info("💡 Add OpenRouter API key to enable advanced AI keyword extraction")

                                        # Create note data with both original and enhanced transcriptions
                                        note_data = {
                                            "id": str(uuid.uuid4()),
                                            "timestamp": datetime.now().isoformat(),
                                            "language": selected_language,
                                            "language_code": language_code,
                                            "transcription": final_transcription,  # This is the final/enhanced version
                                            "original_transcription": transcription,  # Store original transcription
                                            "enhanced_transcription": final_transcription if "current_cleaning_result" in st.session_state else None,
                                            "audio_file": device_audio.name,
                                            "audio_path": permanent_audio_path,
                                            "summary": summary,
                                            "keywords": keywords,
                                            "tags": ["device-recording"],
                                            "processing_method": "ai_enhanced" if "current_cleaning_result" in st.session_state and st.session_state["current_cleaning_result"].get('processing_method') == 'ai_enhanced' else "traditional",
                                            "summary_ai_model": "llama-3.1-405b" if summary and components["llama_ai"] else None,
                                            "keywords_ai_model": "llama-3.1-405b" if keywords and components["llama_ai"] else None
                                        }

                                        # Add cleaning stats if available
                                        if "current_cleaning_result" in st.session_state:
                                            cleaning_result = st.session_state["current_cleaning_result"]
                                            note_data["cleaning_stats"] = {
                                                "original_length": cleaning_result.get('word_count_original', 0),
                                                "cleaned_length": cleaning_result.get('word_count_cleaned', 0),
                                                "confidence_score": cleaning_result.get('confidence_score', 0.0),
                                                "reduction_percentage": cleaning_result.get('reduction_percentage', 0.0),
                                                "processing_method": cleaning_result.get('processing_method', 'traditional'),
                                                "ai_model": cleaning_result.get('ai_model', None)
                                            }

                                            # Add AI-specific data if available
                                            if cleaning_result.get('processing_method') == 'ai_enhanced':
                                                note_data["ai_improvements"] = cleaning_result.get('processing_steps', [])
                                                note_data["ai_confidence"] = cleaning_result.get('confidence_score', 0.0)

                                        # Save note
                                        components["storage"].save_note(note_data)

                                        st.success("📝 Note saved successfully!")
                                        st.session_state.corpus_contributions += 1

                                        # Show summary and keywords
                                        if summary:
                                            st.subheader("📋 Generated Summary")
                                            st.info(summary)

                                        if keywords:
                                            st.subheader("🔑 Key Topics")
                                            keyword_tags = " ".join([f"`{kw}`" for kw in keywords[:5]])
                                            st.markdown(keyword_tags)

                                        st.success("✅ Note automatically saved to Swecha corpus!")

                                        # Keep session state so user can see the saved note
                                        # Note: Session state will be cleared on page refresh or new recording

                                    except Exception as save_error:
                                        st.error(f"Error saving note: {str(save_error)}")
                                        st.error("Please try again or contact support if the problem persists.")

                    with col2:
                        # Quick summary preview
                        if st.button("👁️ Preview Summary", key="preview_summary_device"):
                            final_transcription = transcription_text if "current_cleaning_result" in st.session_state else transcription
                            if final_transcription and len(final_transcription.split()) > 10:
                                if components["llama_ai"]:
                                    with st.spinner("Generating preview..."):
                                        try:
                                            preview_summary = components["llama_ai"].generate_summary(
                                                final_transcription, language_code=language_code
                                            )
                                            if preview_summary:
                                                st.info(f"📋 Preview: {preview_summary}")
                                            else:
                                                st.warning("Could not generate summary preview")
                                        except Exception as e:
                                            st.error(f"Summary preview failed: {str(e)}")
                                else:
                                    st.warning("Summary feature not available (model loading failed)")
                            else:
                                st.warning("Text too short for summary")

            # Add browser-based recording option
            st.markdown("---")
            st.subheader("Browser Recording")

            # HTML for browser recording
            browser_recording_html = """
            <div style="padding: 20px; border: 2px dashed #ccc; border-radius: 10px; text-align: center;">
                <button id="recordButton" onclick="toggleRecording()" style="
                    background-color: #ff4444;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                ">🎙️ Start Recording</button>
                <br><br>
                <div id="status">Click "Start Recording" to begin</div>
                <audio id="audioPlayback" controls style="display: none; margin-top: 10px;"></audio>
            </div>

            <script>
            let mediaRecorder;
            let audioChunks = [];
            let isRecording = false;

            async function toggleRecording() {
                const button = document.getElementById('recordButton');
                const status = document.getElementById('status');

                if (!isRecording) {
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        mediaRecorder = new MediaRecorder(stream);

                        mediaRecorder.ondataavailable = event => {
                            audioChunks.push(event.data);
                        };

                        mediaRecorder.onstop = () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            const audioUrl = URL.createObjectURL(audioBlob);
                            const audio = document.getElementById('audioPlayback');
                            audio.src = audioUrl;
                            audio.style.display = 'block';

                            // Reset
                            audioChunks = [];
                            status.textContent = 'Recording completed! You can play it back above.';
                        };

                        mediaRecorder.start();
                        isRecording = true;
                        button.textContent = '⏹️ Stop Recording';
                        button.style.backgroundColor = '#444444';
                        status.textContent = '🔴 Recording... Click "Stop Recording" when finished';

                    } catch (err) {
                        status.textContent = 'Error: Could not access microphone. Please check permissions.';
                        console.error('Error accessing microphone:', err);
                    }
                } else {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    isRecording = false;
                    button.textContent = '🎙️ Start Recording';
                    button.style.backgroundColor = '#ff4444';
                    status.textContent = 'Processing recording...';
                }
            }
            </script>
            """

            st_components.html(browser_recording_html, height=200)

            st.info("""
            **Note**: Browser recording allows direct audio capture in your web browser.
            You can also use your device's voice recorder app and upload the file for additional flexibility.
            """)

        else:  # Upload Audio File
            st.subheader("Upload Audio File")

            # File uploader for audio
            uploaded_audio = st.file_uploader(
                "Upload audio file from your computer:",
                type=["wav", "mp3", "ogg", "m4a", "flac", "aac"],
                help="Select an audio file from your computer to transcribe",
            )

            if uploaded_audio is not None:
                st.audio(uploaded_audio)

                # Save uploaded file temporarily
                temp_audio_path = f"temp_audio_{uuid.uuid4().hex}.wav"
                with open(temp_audio_path, "wb") as f:
                    f.write(uploaded_audio.read())

                # Transcription
                st.subheader("Step 2: Transcribe")
                if st.button("🔤 Transcribe Audio", type="primary"):
                    with st.spinner(f"Transcribing audio in {selected_language}..."):
                        try:
                            transcription = components["transcriber"].transcribe(
                                temp_audio_path, language=language_code
                            )

                            if transcription:
                                st.success("✅ Transcription completed!")

                                # Display transcription
                                transcription_text = st.text_area(
                                    "Transcription (editable):",
                                    value=transcription,
                                    height=150,
                                    key="upload_transcription_edit",
                                )

                                # Create note
                                if st.button("💾 Save Note", key="save_uploaded_audio"):
                                    with st.spinner("🔄 Processing note with AI..."):
                                        # Save audio file permanently
                                        permanent_audio_path = f"whispnote_data/audio/audio_{uuid.uuid4().hex}_{uploaded_audio.name}"
                                        os.makedirs(os.path.dirname(permanent_audio_path), exist_ok=True)

                                        # Save uploaded audio to permanent location
                                        with open(permanent_audio_path, "wb") as f:
                                            uploaded_audio.seek(0)  # Reset file pointer
                                            f.write(uploaded_audio.read())

                                        # Generate summary and keywords using LLaMA AI
                                        summary = None
                                        keywords = []

                                        # Use LLaMA 3.1 for AI-powered summary and keyword extraction
                                        if components["llama_ai"] and transcription_text and len(transcription_text.split()) > 10:
                                            try:
                                                st.info("� Using LLaMA 3.1 for AI-powered summary and keyword extraction...")
                                                summary, keywords = components["llama_ai"].generate_summary_and_keywords(
                                                    transcription_text, language=language_code
                                                )
                                                if summary:
                                                    st.success("✅ LLaMA 3.1 processing completed!")
                                            except Exception as llama_error:
                                                st.warning(f"LLaMA AI processing failed: {str(llama_error)}")

                                        # If no summary/keywords generated, show info
                                        if not summary:
                                            st.info("💡 Add OpenRouter API key to enable advanced AI summarization")
                                        if not keywords:
                                            st.info("💡 Add OpenRouter API key to enable advanced AI keyword extraction")

                                        note_data = {
                                            "id": str(uuid.uuid4()),
                                            "timestamp": datetime.now().isoformat(),
                                            "language": selected_language,
                                            "language_code": language_code,
                                            "transcription": transcription_text,
                                            "original_transcription": transcription,
                                            "enhanced_transcription": None,  # No enhancement done for upload method
                                            "audio_file": uploaded_audio.name,
                                            "audio_path": permanent_audio_path,
                                            "summary": summary,
                                            "keywords": keywords,
                                            "tags": ["uploaded-audio"],
                                            "processing_method": "llama_ai" if summary and keywords else "none",
                                            "ai_model": "llama-3.1-405b" if summary and keywords else None
                                        }

                                        # Save note
                                        components["storage"].save_note(note_data)
                                        st.session_state.corpus_contributions += 1

                                        st.success("📝 Note saved successfully!")

                                        # Show generated summary and keywords
                                        if summary:
                                            st.subheader("📋 Generated Summary")
                                            st.info(summary)

                                        if keywords:
                                            st.subheader("🔑 Key Topics")
                                            keyword_tags = " ".join([f"`{kw}`" for kw in keywords[:5]])
                                            st.markdown(keyword_tags)

                                        st.success("✅ Note automatically saved to Swecha corpus!")

                        except Exception as e:
                            st.error(f"Error during transcription: {str(e)}")

                        finally:
                            # Clean up temp file
                            if os.path.exists(temp_audio_path):
                                os.remove(temp_audio_path)

    with tab2:
        st.header("My Notes")

        # Load and display notes
        notes = components["storage"].load_notes()

        if not notes:
            st.info("📝 No notes yet. Record your first voice note!")
        else:
            # Search and filter
            col1, col2 = st.columns([2, 1])
            with col1:
                search_query = st.text_input(
                    "🔍 Search notes...",
                    placeholder="Search by content, language, or tags",
                )
            with col2:
                language_filter = st.selectbox(
                    "Filter by language", ["All"] + list(language_options.keys())
                )

            # Filter notes
            filtered_notes = notes
            if search_query:
                filtered_notes = [
                    note
                    for note in filtered_notes
                    if search_query.lower() in note.get("transcription", "").lower()
                ]
            if language_filter != "All":
                filtered_notes = [
                    note
                    for note in filtered_notes
                    if note.get("language") == language_filter
                ]

            # Display notes - Focus on INPUT DATA
            for note in reversed(filtered_notes):  # Show newest first
                with st.expander(
                    f"🎙️ {note.get('language', 'Unknown')} - {note.get('timestamp', '')[:16]}"
                ):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Highlight this is INPUT DATA section
                        st.markdown("### 📥 **Input Data**")

                        # Show audio information prominently
                        if note.get("audio_file"):
                            st.info(f"🎵 **Audio File:** {note.get('audio_file')}")

                        # Show language and processing info
                        st.write(f"**Language:** {note.get('language', 'Unknown')} ({note.get('language_code', '')})")

                        # Show recording method
                        tags = note.get("tags", [])
                        if "device-recording" in tags:
                            st.write("📱 **Source:** Device Recording")
                        elif "uploaded-audio" in tags:
                            st.write("📁 **Source:** Uploaded Audio File")
                        elif "OCR" in tags:
                            st.write("🔍 **Source:** OCR Text Extraction")

                        # FOCUS ON ORIGINAL INPUT - show original transcription prominently
                        st.markdown("### 📝 **Original Transcription (Input)**")
                        original_text = note.get("original_transcription") or note.get("transcription", "")
                        if original_text:
                            st.text_area(
                                "Raw input text:",
                                value=original_text,
                                height=150,
                                disabled=True,
                                key=f"input_display_{note.get('id', '')}"
                            )
                        else:
                            st.warning("No original transcription available")

                        # Show word count and basic stats for input
                        if original_text:
                            word_count = len(original_text.split())
                            char_count = len(original_text)
                            st.write(f"📊 **Input Stats:** {word_count} words, {char_count} characters")

                        # Show audio player if audio file is available
                        if note.get("audio_path") and os.path.exists(note.get("audio_path")):
                            st.write("**🎵 Audio Recording:**")
                            with open(note.get("audio_path"), "rb") as audio_file:
                                st.audio(audio_file.read())
                        elif note.get("audio_file"):
                            st.write(f"**Audio File:** {note.get('audio_file')} (file not found)")

                        # Note about AI outputs
                        if note.get("summary") or note.get("keywords"):
                            st.success("🤖 **AI outputs available** - Check the 'Summarize' tab for AI-generated summaries and keywords")

                        # Corpus upload for input data
                        st.markdown("### 🌐 **Corpus Contribution**")
                        st.info("💡 Upload your input data to contribute to the corpus database")

                        if st.button("📤 Upload Input to Corpus", key=f"corpus_input_{note['id']}"):
                            with st.spinner("Uploading input data to corpus..."):
                                try:
                                    # Check if user is authenticated
                                    swecha_status = components["storage"].get_swecha_status()
                                    if not swecha_status.get("authenticated", False):
                                        st.error("❌ Please log in to Swecha to upload to corpus")
                                        st.info("Use the sidebar to authenticate with your Swecha account")
                                    else:
                                        # Upload the note to Swecha API
                                        success = components["storage"]._save_note_to_swecha(note)
                                        if success:
                                            st.success("✅ Input data uploaded to corpus database!")
                                            st.info("🎯 Your original transcription is now part of the knowledge base!")

                                            # Mark as uploaded in local storage
                                            note["uploaded_to_corpus"] = True
                                            note["corpus_upload_date"] = datetime.now().isoformat()
                                            components["storage"]._save_note_locally(note)
                                        else:
                                            st.error("❌ Failed to upload to corpus. Please try again.")
                                except Exception as e:
                                    st.error(f"❌ Error uploading to corpus: {str(e)}")
                                    st.info("Please check your internet connection and try again.")

                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{note['id']}"):
                            components["storage"].delete_note(note["id"])
                            st.rerun()

                        if st.button("📤 Export Input", key=f"export_{note['id']}"):
                            # Export functionality - focus on input data
                            export_data = components["export_utils"].export_note(
                                note, format="markdown"
                            )
                            st.download_button(
                                "⬇️ Download Input MD",
                                export_data,
                                file_name=f"input_note_{note['id'][:8]}.md",
                                mime="text/markdown",
                                key=f"download_input_{note['id']}",
                            )

    with tab3:
        st.header("🤖 AI Outputs & Summarization")
        st.info("📤 **This section displays AI-generated outputs:** summaries, keywords, enhanced transcriptions, and processing insights")

        # Load notes for AI processing
        notes = components["storage"].load_notes()
        if notes:
            # Filter notes that have some AI processing available or can be processed
            note_options = {
                f"{note.get('timestamp', '')[:16]} - {note.get('language', '')}": note
                for note in notes
            }

            selected_note_key = st.selectbox(
                "📋 Select a note to view/generate AI outputs:",
                list(note_options.keys()),
                help="Choose a note to see AI summaries, keywords, and enhanced transcriptions"
            )

            if selected_note_key:
                selected_note = note_options[selected_note_key]

                # Reference to source (brief)
                with st.expander("📝 Source Input Reference"):
                    st.write(f"**Language:** {selected_note.get('language', 'Unknown')}")
                    original_text = selected_note.get("original_transcription") or selected_note.get("transcription", "")
                    if original_text:
                        word_count = len(original_text.split())
                        st.write(f"**Input length:** {word_count} words")
                        st.text_area("Input preview:", original_text[:200] + "..." if len(original_text) > 200 else original_text, height=80, disabled=True)
                    else:
                        st.warning("No input text available")

                # FOCUS ON AI OUTPUTS
                st.markdown("### 🤖 **AI-Generated Outputs**")

                # Show existing AI outputs prominently
                ai_outputs_exist = False

                # Display AI Summary if available
                if selected_note.get("summary"):
                    ai_outputs_exist = True
                    st.success("✨ **AI Summary Available**")
                    st.markdown("#### 📄 AI Summary")
                    st.info(selected_note.get("summary"))

                    # Show summary stats
                    original_text = selected_note.get("original_transcription") or selected_note.get("transcription", "")
                    if original_text:
                        original_words = len(original_text.split())
                        summary_words = len(selected_note.get("summary", "").split())
                        compression = (summary_words / original_words) if original_words > 0 else 0

                        col_sum1, col_sum2, col_sum3 = st.columns(3)
                        with col_sum1:
                            st.metric("Original Words", original_words)
                        with col_sum2:
                            st.metric("Summary Words", summary_words)
                        with col_sum3:
                            st.metric("Compression", f"{compression:.1%}")

                # Display AI Keywords if available
                if selected_note.get("keywords"):
                    ai_outputs_exist = True
                    st.success("🔍 **AI Keywords Available**")
                    st.markdown("#### 🏷️ AI-Extracted Keywords")
                    keywords_text = ", ".join(selected_note.get("keywords", []))
                    st.write(f"**Keywords:** {keywords_text}")

                # Display Enhanced Transcription if available
                if selected_note.get("enhanced_transcription") and selected_note.get("original_transcription"):
                    ai_outputs_exist = True
                    st.success("✨ **AI-Enhanced Transcription Available**")
                    st.markdown("#### 📝 AI Enhancement")

                    col_enh1, col_enh2 = st.columns(2)
                    with col_enh1:
                        st.write("**Original:**")
                        st.text_area("", selected_note.get("original_transcription", ""), height=120, disabled=True, key="orig_disp")
                    with col_enh2:
                        st.write("**AI Enhanced:**")
                        st.text_area("", selected_note.get("enhanced_transcription", ""), height=120, disabled=True, key="enh_disp")

                    # Show AI improvements if available
                    if selected_note.get("ai_improvements"):
                        with st.expander("🔍 AI Improvements Made"):
                            for improvement in selected_note.get("ai_improvements", []):
                                st.write(f"• {improvement}")

                # Show AI processing stats if available
                if selected_note.get("cleaning_stats"):
                    ai_outputs_exist = True
                    cleaning_stats = selected_note.get("cleaning_stats")
                    st.success("📊 **AI Processing Statistics Available**")
                    with st.expander("📈 AI Processing Details"):
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("Original Length", cleaning_stats.get('original_length', 0))
                        with col_stat2:
                            st.metric("Enhanced Length", cleaning_stats.get('cleaned_length', 0))
                        with col_stat3:
                            st.metric("AI Confidence", f"{cleaning_stats.get('confidence_score', 0):.1%}")

                        if cleaning_stats.get('ai_model'):
                            st.info(f"🤖 Processed using: {cleaning_stats.get('ai_model')}")

                # If no AI outputs exist yet, show generation options
                if not ai_outputs_exist:
                    st.warning("⚠️ No AI outputs available for this note yet. Generate them below:")

                # AI Generation Options
                st.markdown("### 🚀 **Generate New AI Outputs**")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📝 AI Summary Generation")
                    summary_method = st.radio(
                        "Summarization method:",
                        ["🤖 LLaMA 3.1 405B (AI)"],
                        key="summary_method"
                    )

                    if st.button("📝 Generate/Update Summary", type="primary"):
                        with st.spinner("🤖 LLaMA generating summary..."):
                            try:
                                if components["llama_ai"]:
                                    # Use LLaMA AI summarization
                                    ai_result = components["llama_ai"].summarize_text(
                                        selected_note.get("transcription", ""),
                                        selected_note.get("language_code", "en")
                                    )
                                    summary = ai_result['summary']

                                    # Show new AI summary
                                    st.success("✨ New AI Summary generated!")
                                    st.markdown("#### 📄 Fresh AI Summary")
                                    st.info(summary)

                                    # Show additional AI insights
                                    if ai_result.get('key_points'):
                                        with st.expander("🎯 AI-Identified Key Points"):
                                            for point in ai_result['key_points']:
                                                st.write(f"• {point}")

                                    # Update note with summary
                                    selected_note["summary"] = summary
                                    components["storage"].update_note(selected_note)
                                    st.success("💾 Summary saved! Refresh to see in outputs above.")

                                else:
                                    st.error("❌ LLaMA AI not available for summarization")

                            except Exception as e:
                                st.error(f"❌ Error generating summary: {str(e)}")

                with col2:
                    st.markdown("#### 🔍 AI Keyword Extraction")
                    keyword_method = st.radio(
                        "Keyword extraction method:",
                        ["🤖 LLaMA 3.1 405B (AI)"],
                        key="keyword_method"
                    )

                    if st.button("🔍 Generate/Update Keywords", type="primary"):
                        with st.spinner("🤖 LLaMA extracting keywords..."):
                            try:
                                if components["llama_ai"]:
                                    # Use LLaMA keyword extraction
                                    ai_result = components["llama_ai"].extract_keywords(
                                        selected_note.get("transcription", ""),
                                        max_keywords=10
                                    )

                                    keywords = [kw['term'] for kw in ai_result.get('keywords', [])]

                                    st.success("✨ New AI Keywords extracted!")
                                    st.markdown("#### 🏷️ Fresh AI Keywords")
                                    st.write(f"**Keywords:** {', '.join(keywords)}")

                                    # Show detailed keyword analysis
                                    if ai_result.get('keywords'):
                                        with st.expander("🎯 Detailed AI Keyword Analysis"):
                                            for kw in ai_result['keywords'][:5]:  # Top 5
                                                relevance = kw.get('relevance', 0.5)
                                                st.write(f"**{kw['term']}** - Relevance: {relevance:.1%} ({kw.get('type', 'unknown')})")

                                    if ai_result.get('main_topics'):
                                        st.write("**AI-Identified Topics:**")
                                        st.write(", ".join(ai_result['main_topics']))

                                    if ai_result.get('text_category'):
                                        st.write(f"**AI Category:** {ai_result['text_category']}")

                                    # Update note with keywords
                                    selected_note["keywords"] = keywords
                                    components["storage"].update_note(selected_note)
                                    st.success("💾 Keywords saved! Refresh to see in outputs above.")

                                else:
                                    st.error("❌ LLaMA AI not available for keyword extraction")

                            except Exception as e:
                                st.error(f"❌ Error extracting keywords: {str(e)}")

                # Corpus upload section for outputs
                st.markdown("### 🌐 **Corpus Contribution**")
                if ai_outputs_exist:
                    if st.button("📤 Upload AI Outputs to Corpus Database", type="secondary"):
                        with st.spinner("Uploading AI outputs to corpus..."):
                            try:
                                # Check if user is authenticated
                                swecha_status = components["storage"].get_swecha_status()
                                if not swecha_status.get("authenticated", False):
                                    st.error("❌ Please log in to Swecha to upload to corpus")
                                    st.info("Use the sidebar to authenticate with your Swecha account")
                                else:
                                    # Create a comprehensive record with AI outputs
                                    ai_record = {
                                        "id": f"ai_output_{selected_note.get('id', uuid.uuid4().hex)}",
                                        "original_transcription": selected_note.get("original_transcription") or selected_note.get("transcription", ""),
                                        "enhanced_transcription": selected_note.get("enhanced_transcription", ""),
                                        "summary": selected_note.get("summary", ""),
                                        "keywords": selected_note.get("keywords", []),
                                        "ai_improvements": selected_note.get("ai_improvements", []),
                                        "cleaning_stats": selected_note.get("cleaning_stats", {}),
                                        "language": selected_note.get("language", "Unknown"),
                                        "language_code": selected_note.get("language_code", "te"),
                                        "processing_method": "ai_enhanced",
                                        "timestamp": datetime.now().isoformat(),
                                        "note_type": "ai_processed_output"
                                    }

                                    # Upload AI-enhanced data to corpus
                                    success = components["storage"]._save_note_to_swecha(ai_record)
                                    if success:
                                        st.success("✅ AI outputs uploaded to corpus database!")
                                        st.info("🎯 Your AI summaries and keywords are now part of the knowledge base!")

                                        # Mark original note as having AI outputs uploaded
                                        selected_note["ai_outputs_uploaded"] = True
                                        selected_note["ai_upload_date"] = datetime.now().isoformat()
                                        components["storage"].update_note(selected_note)
                                    else:
                                        st.error("❌ Failed to upload AI outputs to corpus. Please try again.")
                            except Exception as e:
                                st.error(f"❌ Error uploading to corpus: {str(e)}")
                                st.info("Please check your internet connection and try again.")
                else:
                    st.info("💡 Generate AI outputs first, then contribute them to the corpus database!")

        else:
            st.info("📝 No notes available. Create some voice notes first to generate AI outputs!")

    with tab4:
        st.header("OCR - Extract Text from Images")

        uploaded_image = st.file_uploader(
            "Upload an image to extract text",
            type=["png", "jpg", "jpeg", "tiff", "bmp"],
            help="Upload an image containing text to extract it using OCR",
        )

        if uploaded_image is not None:
            st.image(uploaded_image, caption="Uploaded Image", width=400)

            if st.button("🔍 Extract Text from Image"):
                with st.spinner("Processing image with OCR..."):
                    try:
                        # Save uploaded image temporarily
                        temp_image_path = f"temp_image_{uuid.uuid4().hex}.png"
                        with open(temp_image_path, "wb") as f:
                            f.write(uploaded_image.read())

                        # Extract text
                        extracted_text = components["ocr_reader"].extract_text(
                            temp_image_path
                        )

                        if extracted_text.strip():
                            st.success("✅ Text extracted successfully!")

                            # Editable text area
                            final_text = st.text_area(
                                "Extracted Text (editable):",
                                value=extracted_text,
                                height=200,
                                key="ocr_text_edit",
                            )

                            # Option to save as note
                            if st.button("💾 Save as Voice Note"):
                                with st.spinner("🔄 Processing OCR text with AI..."):
                                    # Generate summary and keywords using LLaMA AI
                                    summary = None
                                    keywords = []

                                    # Use LLaMA 3.1 for AI-powered summary and keyword extraction
                                    if components["llama_ai"] and final_text and len(final_text.split()) > 10:
                                        try:
                                            st.info("� Using LLaMA 3.1 for AI-powered summary and keyword extraction...")
                                            summary, keywords = components["llama_ai"].generate_summary_and_keywords(
                                                final_text, language="en"
                                            )
                                            if summary:
                                                st.success("✅ LLaMA 3.1 processing completed!")
                                        except Exception as llama_error:
                                            st.warning(f"LLaMA AI processing failed: {str(llama_error)}")

                                    # If no summary/keywords generated, show info
                                    if not summary:
                                        st.info("💡 Add OpenRouter API key to enable advanced AI summarization")
                                    if not keywords:
                                        st.info("💡 Add OpenRouter API key to enable advanced AI keyword extraction")

                                    note_data = {
                                        "id": str(uuid.uuid4()),
                                        "timestamp": datetime.now().isoformat(),
                                        "language": "OCR Text",
                                        "language_code": "en",
                                        "transcription": final_text,
                                        "audio_file": None,
                                        "summary": summary,
                                        "keywords": keywords,
                                        "tags": ["OCR"],
                                        "source": "OCR",
                                        "processing_method": "llama_ai" if summary and keywords else "none",
                                        "ai_model": "llama-3.1-405b" if summary and keywords else None
                                    }

                                    components["storage"].save_note(note_data)
                                    st.success("📝 OCR text saved as note!")

                                    # Show generated summary and keywords
                                    if summary:
                                        st.subheader("📋 Generated Summary")
                                        st.info(summary)

                                    if keywords:
                                        st.subheader("🔑 Key Topics")
                                        keyword_tags = " ".join([f"`{kw}`" for kw in keywords[:5]])
                                        st.markdown(keyword_tags)

                                    # Note: OCR text cannot be uploaded to Swecha as it requires audio
                                    st.info("💡 Tip: OCR notes cannot be uploaded to Swecha corpus as they don't have audio recordings.")
                        else:
                            st.warning(
                                "No text found in the image. Please try with a clearer image."
                            )

                    except Exception as e:
                        st.error(f"Error during OCR processing: {str(e)}")

                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_image_path):
                            os.remove(temp_image_path)

    with tab5:
        st.header("📊 My Contribution Statistics")

        # Privacy notice - prominently displayed at the top
        st.markdown("### 🔒 Privacy Information")
        st.info("""
        **Your personal statistics are private and secure:**

        • **Personal Data:** Only you can see your contribution statistics
        • **Local Storage:** All notes are stored locally on your device
        • **Opt-in Corpus:** Data is only contributed to the corpus with your explicit consent
        • **Anonymized:** Contributed data is anonymized and contains no personal information
        • **Offline First:** App works completely offline
        """)
        st.markdown("---")

        # Check Swecha API connection and user authentication
        swecha_status = components["storage"].get_swecha_status()

        if swecha_status.get("connected", False) and swecha_status.get("authenticated", False):
            # User is authenticated - show comprehensive dashboard
            st.success("✅ **Connected to Swecha Corpus Platform**")

            # User Profile Section
            st.markdown("### 👤 **User Profile**")
            user_info = swecha_status.get('user_info', {})

            col1, col2 = st.columns([2, 1])
            with col1:
                st.info(f"**Name:** {user_info.get('name', 'Unknown')}")
                st.info(f"**Phone:** {user_info.get('phone', 'Unknown')}")
                if user_info.get('email'):
                    st.info(f"**Email:** {user_info.get('email')}")
                st.info(f"**Member since:** {user_info.get('created_at', 'Unknown')[:10] if user_info.get('created_at') else 'Unknown'}")

            with col2:
                if user_info.get('roles'):
                    roles = [role.get('name', 'user') for role in user_info.get('roles', [])]
                    role_badges = ""
                    for role in roles:
                        if role == 'admin':
                            role_badges += "🔧 **Admin** "
                        elif role == 'reviewer':
                            role_badges += "👁️ **Reviewer** "
                        else:
                            role_badges += "👤 **User** "
                    st.markdown(f"**Roles:** {role_badges}")

            st.markdown("---")

            # Contribution Statistics
            st.markdown("### 📈 **Your Contributions to Telugu Corpus**")

            # Fetch user contributions from Swecha API
            try:
                with st.spinner("Loading your contribution statistics..."):
                    contributions = components["storage"].get_user_contributions()

                if contributions:
                    # Main contribution metrics - Top row
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        total_contributions = contributions.get('total_contributions', 0)
                        st.metric("🎯 Total Contributions", total_contributions)

                    with col2:
                        audio_count = contributions.get('contributions_by_media_type', {}).get('audio', 0)
                        st.metric("🎵 Audio Files", audio_count)

                    with col3:
                        text_count = contributions.get('contributions_by_media_type', {}).get('text', 0)
                        st.metric("📝 Text Records", text_count)

                    with col4:
                        audio_duration = contributions.get('audio_duration', 0)
                        duration_mins = round(audio_duration / 60, 1) if audio_duration else 0
                        st.metric("⏱️ Audio Duration", f"{duration_mins} mins")

                    # Additional media type metrics - Second row
                    st.markdown("#### 📊 **Media Type Breakdown**")
                    media_col1, media_col2, media_col3, media_col4 = st.columns(4)

                    with media_col1:
                        video_count = contributions.get('contributions_by_media_type', {}).get('video', 0)
                        st.metric("🎬 Video Files", video_count)

                    with media_col2:
                        image_count = contributions.get('contributions_by_media_type', {}).get('image', 0)
                        st.metric("🖼️ Image Files", image_count)

                    with media_col3:
                        video_duration = contributions.get('video_duration', 0)
                        video_duration_mins = round(video_duration / 60, 1) if video_duration else 0
                        st.metric("🎞️ Video Duration", f"{video_duration_mins} mins")

                    with media_col4:
                        # Calculate total file size across all media types
                        total_size = 0
                        for media_type in ['audio_contributions', 'text_contributions', 'video_contributions', 'image_contributions']:
                            if contributions.get(media_type):
                                for contrib in contributions[media_type]:
                                    total_size += contrib.get('size', 0)

                        # Convert to human readable format
                        if total_size > 1024*1024*1024:  # GB
                            size_str = f"{total_size/(1024*1024*1024):.1f} GB"
                        elif total_size > 1024*1024:  # MB
                            size_str = f"{total_size/(1024*1024):.1f} MB"
                        elif total_size > 1024:  # KB
                            size_str = f"{total_size/1024:.1f} KB"
                        else:
                            size_str = f"{total_size} bytes"

                        st.metric("💾 Total Data Size", size_str)

                    # Detailed contribution breakdown
                    st.markdown("#### 📊 **Detailed Contribution Breakdown**")

                    # Media type distribution
                    media_stats = contributions.get('contributions_by_media_type', {})
                    if any(media_stats.values()):
                        media_df = pd.DataFrame([
                            {'Media Type': 'Audio', 'Count': media_stats.get('audio', 0)},
                            {'Media Type': 'Text', 'Count': media_stats.get('text', 0)},
                            {'Media Type': 'Video', 'Count': media_stats.get('video', 0)},
                            {'Media Type': 'Image', 'Count': media_stats.get('image', 0)}
                        ])
                        media_df = media_df[media_df['Count'] > 0]  # Only show non-zero counts

                        if not media_df.empty:
                            st.bar_chart(media_df.set_index('Media Type'))

                    # Recent contributions
                    st.markdown("#### 📝 **Recent Contributions**")

                    # Audio contributions
                    if contributions.get('audio_contributions'):
                        with st.expander("🎵 **Audio Contributions**", expanded=True):
                            for contrib in contributions['audio_contributions'][:5]:  # Show recent 5
                                col_a, col_b, col_c = st.columns([3, 1, 1])
                                with col_a:
                                    st.write(f"**{contrib.get('title', 'Untitled')}**")
                                    if contrib.get('description'):
                                        st.caption(contrib['description'][:100] + "..." if len(contrib.get('description', '')) > 100 else contrib.get('description', ''))
                                with col_b:
                                    duration = contrib.get('duration', 0)
                                    if duration:
                                        st.write(f"⏱️ {duration}s")
                                    st.write(f"📊 {contrib.get('size', 0)} bytes")
                                with col_c:
                                    status = "✅ Reviewed" if contrib.get('reviewed') else "⏳ Pending"
                                    st.write(status)
                                    timestamp = contrib.get('timestamp', '')[:10] if contrib.get('timestamp') else 'Unknown'
                                    st.caption(timestamp)
                                st.markdown("---")

                    # Text contributions
                    if contributions.get('text_contributions'):
                        with st.expander("📝 **Text Contributions**", expanded=False):
                            for contrib in contributions['text_contributions'][:5]:  # Show recent 5
                                col_a, col_b, col_c = st.columns([3, 1, 1])
                                with col_a:
                                    st.write(f"**{contrib.get('title', 'Untitled')}**")
                                    if contrib.get('description'):
                                        st.caption(contrib['description'][:100] + "..." if len(contrib.get('description', '')) > 100 else contrib.get('description', ''))
                                with col_b:
                                    st.write(f"📊 {contrib.get('size', 0)} bytes")
                                with col_c:
                                    status = "✅ Reviewed" if contrib.get('reviewed') else "⏳ Pending"
                                    st.write(status)
                                    timestamp = contrib.get('timestamp', '')[:10] if contrib.get('timestamp') else 'Unknown'
                                    st.caption(timestamp)
                                st.markdown("---")

                    # Video contributions
                    if contributions.get('video_contributions'):
                        with st.expander("🎬 **Video Contributions**", expanded=False):
                            for contrib in contributions['video_contributions'][:5]:  # Show recent 5
                                col_a, col_b, col_c = st.columns([3, 1, 1])
                                with col_a:
                                    st.write(f"**{contrib.get('title', 'Untitled')}**")
                                    if contrib.get('description'):
                                        st.caption(contrib['description'][:100] + "..." if len(contrib.get('description', '')) > 100 else contrib.get('description', ''))
                                with col_b:
                                    duration = contrib.get('duration', 0)
                                    if duration:
                                        st.write(f"⏱️ {duration}s")
                                    st.write(f"📊 {contrib.get('size', 0)} bytes")
                                with col_c:
                                    status = "✅ Reviewed" if contrib.get('reviewed') else "⏳ Pending"
                                    st.write(status)
                                    timestamp = contrib.get('timestamp', '')[:10] if contrib.get('timestamp') else 'Unknown'
                                    st.caption(timestamp)
                                st.markdown("---")

                    # Image contributions
                    if contributions.get('image_contributions'):
                        with st.expander("🖼️ **Image Contributions**", expanded=False):
                            for contrib in contributions['image_contributions'][:5]:  # Show recent 5
                                col_a, col_b, col_c = st.columns([3, 1, 1])
                                with col_a:
                                    st.write(f"**{contrib.get('title', 'Untitled')}**")
                                    if contrib.get('description'):
                                        st.caption(contrib['description'][:100] + "..." if len(contrib.get('description', '')) > 100 else contrib.get('description', ''))
                                with col_b:
                                    dimensions = contrib.get('dimensions')
                                    if dimensions:
                                        st.write(f"📐 {dimensions}")
                                    st.write(f"📊 {contrib.get('size', 0)} bytes")
                                with col_c:
                                    status = "✅ Reviewed" if contrib.get('reviewed') else "⏳ Pending"
                                    st.write(status)
                                    timestamp = contrib.get('timestamp', '')[:10] if contrib.get('timestamp') else 'Unknown'
                                    st.caption(timestamp)
                                st.markdown("---")

                    # Show message if no contributions found in any category
                    has_any_contributions = any([
                        contributions.get('audio_contributions'),
                        contributions.get('text_contributions'),
                        contributions.get('video_contributions'),
                        contributions.get('image_contributions')
                    ])

                    if not has_any_contributions:
                        st.info("📋 **No recent contributions found.** Your contributions will appear here once you start uploading content to the corpus.")

                    # Achievement badges
                    st.markdown("#### 🏆 **Achievement Badges**")
                    badges_col1, badges_col2, badges_col3 = st.columns(3)

                    with badges_col1:
                        if total_contributions >= 10:
                            st.success("🌟 **Contributor** - 10+ contributions")
                        elif total_contributions >= 5:
                            st.info("⭐ **Helper** - 5+ contributions")
                        elif total_contributions >= 1:
                            st.info("🎯 **Starter** - First contribution!")

                    with badges_col2:
                        if audio_duration >= 3600:  # 1 hour
                            st.success("🎵 **Audio Master** - 1+ hour of audio")
                        elif audio_duration >= 1800:  # 30 minutes
                            st.info("🎤 **Voice Contributor** - 30+ min audio")

                    with badges_col3:
                        # Multi-media badge - check for multiple contribution types
                        media_types_count = sum(1 for media_type in ['audio', 'text', 'video', 'image']
                                               if media_stats.get(media_type, 0) > 0)

                        if media_types_count >= 4:
                            st.success("🎭 **Multi-Media Master** - All 4 media types!")
                        elif media_types_count >= 3:
                            st.success("🎨 **Multi-Media Pro** - 3+ media types")
                        elif media_types_count >= 2:
                            st.info("🎪 **Multi-Media** - 2+ media types")

                        # Additional specialized badges
                        video_count = media_stats.get('video', 0)
                        image_count = media_stats.get('image', 0)

                        if video_count >= 5:
                            st.success("🎬 **Video Creator** - 5+ videos")
                        elif image_count >= 10:
                            st.success("🖼️ **Image Collector** - 10+ images")

                else:
                    st.info("📊 **No contributions found yet.** Start contributing to see your statistics!")
                    st.markdown("""
                    **How to contribute:**
                    1. 🎙️ Record voice notes using the 'Record' tab
                    2. 📤 Upload them to the corpus using the upload buttons
                    3. 📝 Your contributions will appear here with statistics
                    """)

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
                local_notes = components["storage"].load_notes()
                if local_notes:
                    local_col1, local_col2 = st.columns(2)
                    with local_col1:
                        st.metric("📝 Local Notes", len(local_notes))
                    with local_col2:
                        pending = len([n for n in local_notes if not n.get('uploaded_to_corpus', False)])
                        st.metric("📤 Pending Uploads", pending)

        else:
            # User not authenticated - show limited local stats
            st.warning("🔐 **Please authenticate with Swecha to view your contribution statistics**")

            # Show local statistics only
            st.markdown("### 📱 **Local Statistics** (This Device Only)")

            # Load local statistics
            stats = components["storage"].get_corpus_stats()
            local_notes = components["storage"].load_notes()

            # Display local stats
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("📝 Local Notes", len(local_notes))

            with col2:
                pending_uploads = len([n for n in local_notes if not n.get('uploaded_to_corpus', False)])
                st.metric("📤 Pending Uploads", pending_uploads)

            with col3:
                local_languages = set(note.get('language', 'Unknown') for note in local_notes)
                st.metric("🌐 Languages Used", len(local_languages))

            with col4:
                # Calculate total audio duration from local notes
                total_duration = 0
                for note in local_notes:
                    if note.get("audio_path") and os.path.exists(note.get("audio_path")):
                        # This is a rough estimate - in real implementation you'd get actual audio duration
                        total_duration += 2  # Assume 2 minutes average per note
                st.metric("⏱️ Estimated Duration", f"{total_duration:.1f} min")

            # Language distribution for local notes
            if local_notes:
                st.markdown("#### 📊 **Local Language Distribution**")
                lang_counts = {}
                for note in local_notes:
                    lang = note.get('language', 'Unknown')
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1

                if lang_counts:
                    lang_df = pd.DataFrame(
                        list(lang_counts.items()), columns=["Language", "Count"]
                    )
                    st.bar_chart(lang_df.set_index("Language"))

            # Authentication help
            st.markdown("---")
            st.markdown("### 🔑 **Get Full Statistics**")
            st.info("""
            **To unlock full contribution statistics and corpus insights:**

            1. 📱 Use the sidebar to **Sign Up** or **Log In** with Swecha
            2. 🔐 Complete the authentication process
            3. 📊 View your complete contribution history and statistics
            4. 🏆 Earn achievement badges for your contributions
            5. 📈 Track your impact on the Telugu language corpus
            """)

        # Personal performance insights (only for authenticated users)
        if swecha_status.get("connected", False) and swecha_status.get("authenticated", False):
            st.markdown("---")
            st.markdown("### 📈 **Personal Performance Insights**")

            try:
                contributions = components["storage"].get_user_contributions()
                if contributions and contributions.get('total_contributions', 0) > 0:
                    # Show user's ranking and percentile (if available from API)
                    insights_col1, insights_col2 = st.columns(2)

                    with insights_col1:
                        # Contribution trend
                        st.info("📊 **Your Impact:** Your contributions are helping preserve and advance Telugu language technology!")

                        # Contribution quality metrics
                        total_contribs = contributions.get('total_contributions', 0)
                        audio_hours = round(contributions.get('audio_duration', 0) / 3600, 2)

                        if total_contribs > 20:
                            st.success(f"🏆 **Super Contributor:** {total_contribs} contributions! You're making a significant impact.")
                        elif total_contribs > 10:
                            st.success(f"⭐ **Active Contributor:** {total_contribs} contributions! Keep up the great work.")
                        elif total_contribs > 5:
                            st.info(f"🎯 **Growing Contributor:** {total_contribs} contributions! You're on the right track.")
                        else:
                            st.info(f"🌱 **New Contributor:** {total_contribs} contributions! Every contribution matters.")

                    with insights_col2:
                        # Personal goals and suggestions
                        st.markdown("#### 🎯 **Personal Goals**")

                        if audio_hours < 1:
                            st.write("� **Next milestone:** Reach 1 hour of audio contributions")
                            progress = min(audio_hours / 1.0, 1.0)
                            st.progress(progress)
                            st.caption(f"Progress: {audio_hours:.2f} / 1.0 hours")
                        elif audio_hours < 5:
                            st.write("� **Next milestone:** Reach 5 hours of audio contributions")
                            progress = min(audio_hours / 5.0, 1.0)
                            st.progress(progress)
                            st.caption(f"Progress: {audio_hours:.2f} / 5.0 hours")
                        else:
                            st.success("🏆 **Audio Champion:** 5+ hours contributed!")

                        if total_contribs < 50:
                            remaining = 50 - total_contribs
                            st.write(f"� **Challenge:** {remaining} more contributions to reach 50!")
                        else:
                            st.success("🎉 **Milestone Master:** 50+ contributions achieved!")

                else:
                    st.info("📊 **Start your contribution journey:** Upload your first note to see personalized insights!")

            except Exception as e:
                st.info("📊 **Personal insights will appear here once you start contributing to the corpus.**")

        # Quick actions
        st.markdown("---")
        st.markdown("### ⚡ **Quick Actions**")

        action_col1, action_col2, action_col3 = st.columns(3)

        with action_col1:
            if st.button("🎙️ **Record New Note**", help="Go to Record tab"):
                # This would switch to the Record tab (requires state management)
                st.info("Switch to the 'Record' tab to create a new voice note!")

        with action_col2:
            if st.button("📤 **Upload My Notes**", help="Upload all my pending notes to corpus"):
                # This would trigger upload of all local notes
                pending_notes = [n for n in components["storage"].load_notes() if not n.get('uploaded_to_corpus', False)]
                if pending_notes:
                    st.info(f"Found {len(pending_notes)} of your notes ready to upload!")
                else:
                    st.info("No pending uploads found.")

        with action_col3:
            if st.button("🔄 **Refresh My Stats**", help="Reload your personal statistics"):
                st.rerun()


if __name__ == "__main__":
    main()
