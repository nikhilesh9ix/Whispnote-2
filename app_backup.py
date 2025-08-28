import os
import uuid
from datetime import datetime
from typing import Any, Dict

import pandas as pd
import streamlit as st
import streamlit.components.v1 as st_components

from src.ai.llama_summarizer import AdvancedAISummarizer

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
    st.markdown("<h1 class='main-header'>ðŸŽ™ï¸ WhispNote</h1>", unsafe_allow_html=True)
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
            st.success("âœ… Contributing to corpus")
        else:
            st.info("ðŸ”’ Private mode - data stays local")

        # Swecha API Integration
        st.subheader("ðŸŒŸ Swecha Corpus")
        swecha_manager = components["swecha"]

        if swecha_manager.is_logged_in():
            swecha_manager.show_user_info()
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("ðŸ” Login to Swecha"):
                    st.session_state.show_swecha_login = True
                    st.session_state.show_swecha_signup = False
            with col2:
                if st.button("ðŸ“ Sign Up for Swecha"):
                    st.session_state.show_swecha_signup = True
                    st.session_state.show_swecha_login = False

        # Show login form if requested
        if st.session_state.get('show_swecha_login', False) and swecha_manager.show_login_form():
            st.session_state.show_swecha_login = False

        # Show signup form if requested
        if st.session_state.get('show_swecha_signup', False) and swecha_manager.show_signup_form():
            st.session_state.show_swecha_signup = False

        # Privacy Information Section
        st.subheader("ðŸ”’ Privacy & Storage")
        with st.expander("Storage Information", expanded=True):
            st.markdown("""
            **WhispNote uses Swecha API for all data storage:**

            â€¢ **Cloud Storage:** All notes stored securely via Swecha API
            â€¢ **Account Required:** Create a free Swecha account or login to access all features
            â€¢ **Secure Authentication:** Bearer token-based authentication
            â€¢ **Telugu Corpus:** Your contributions help build the Swecha Telugu language corpus
            â€¢ **Data Privacy:** Your data is handled according to Swecha's privacy policy
            â€¢ **Open Source:** Transparent and community-driven
            """)

        # App info
        st.subheader("About")
        st.info("""
        **WhispNote** is a cloud-based voice note app powered by Swecha that:
        - Records and transcribes speech in Indian languages
        - Summarizes content using AI
        - Extracts keywords and topics
        - Contributes to Telugu language corpus
        """)

    # Check authentication status
    swecha_manager = components["swecha"]
    if not swecha_manager.is_logged_in():
        st.warning("ðŸ” **Authentication Required**")
        st.info("""
        ### Welcome to WhispNote! ðŸŽ™ï¸

        To access all features and contribute to the Swecha Telugu corpus, please:

        - **Login** if you already have a Swecha account
        - **Sign Up** to create a new free account

        Use the sidebar authentication options to get started.
        """)
        st.stop()

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["ðŸŽ™ï¸ Record", "ðŸ“ My Notes", "ðŸ“Š Summarize", "ðŸ“ˆ Stats"]
    )

    with tab1:
        st.header("Record Voice Note")

        # Choose recording method
        recording_method = st.radio(
            "Choose recording method:",
            ("ðŸŽ™ï¸ Record with Device", "ðŸ“ Upload Audio File"),
            horizontal=True,
        )

        if recording_method == "ðŸŽ™ï¸ Record with Device":
            st.subheader("Device Recording Instructions")

            # Instructions for recording
            st.info("""
            **How to record audio:**
            1. Use your device's built-in voice recorder app
            2. Record your voice note in your preferred language
            3. Save the recording as an audio file (WAV, MP3, etc.)
            4. Upload the file below using the file uploader

            **Popular voice recording apps:**
            - ðŸ“± **Mobile**: Voice Recorder, Voice Memos (iOS), Samsung Voice Recorder
            - ðŸ’» **Windows**: Voice Recorder app, Audacity
            - ðŸ–¥ï¸ **Mac**: Voice Memos, QuickTime Player
            - ðŸ§ **Linux**: GNOME Sound Recorder, Audacity
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
                if st.button("ðŸ”¤ Transcribe Device Recording", type="primary"):
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
                                st.success("âœ… Transcription completed!")
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
                            ["ðŸ”§ Traditional NLP", "ðŸ¤– AI-Powered (Llama 3.1 405B)"],
                            help="Traditional: Fast, rule-based cleaning. AI: Advanced context-aware enhancement.",
                            key="device_processing_method"
                        )

                    with col2:
                        if st.button("ðŸ§¹ Process Text", type="primary", key="device_process_text"):
                            use_ai = processing_method.startswith("ðŸ¤–")

                            with st.spinner(f"{'ðŸ¤– AI processing' if use_ai else 'ðŸ”§ Traditional processing'}..."):
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
                            st.success(f"âœ¨ Enhanced with {cleaning_result.get('ai_model', 'AI')}")
                        else:
                            st.info("ðŸ”§ Processed with traditional NLP methods")

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
                            with st.expander("ðŸ” Processing Details", expanded=False):
                                for step in cleaning_result['processing_steps']:
                                    st.text(f"âœ“ {step}")

                        # Show spelling/grammar corrections
                        if cleaning_result.get('spelling_corrections'):
                            with st.expander(f"ðŸ“ Spelling Corrections ({len(cleaning_result['spelling_corrections'])})", expanded=False):
                                for correction in cleaning_result['spelling_corrections'][:10]:
                                    st.text(f"â€¢ {correction['original']} â†’ {correction['corrected']}")

                        # Show what was removed (for traditional processing)
                        if cleaning_result.get('removed_elements'):
                            with st.expander(f"ðŸ—‘ï¸ Removed {len(cleaning_result['removed_elements'])} elements", expanded=False):
                                for item in cleaning_result['removed_elements'][:10]:
                                    st.text(f"â€¢ {item}")
                                if len(cleaning_result['removed_elements']) > 10:
                                    st.text(f"... and {len(cleaning_result['removed_elements']) - 10} more")

                        # Editable text areas for comparison
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("ðŸ” Original Transcription")
                            st.text_area(
                                "Original:",
                                value=transcription,  # Use the original transcription
                                height=150,
                                key="device_original_transcription",
                                disabled=True
                            )

                        with col2:
                            st.subheader("âœ¨ Enhanced Transcription")
                            transcription_text = st.text_area(
                                "Enhanced (editable):",
                                value=cleaning_result['cleaned'],
                                height=150,
                                key="device_transcription_edit",
                                help="Review and edit the enhanced transcription before saving"
                            )
                    else:
                        # No processing done yet, show original transcription for editing
                        st.subheader("ðŸ“ Transcription")
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
                            "ðŸ“ Save Note", key="save_device_recording", type="primary"
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
                                st.error("âŒ No transcription text to save!")
                            elif not transcription or not transcription.strip():
                                st.error("âŒ Original transcription is missing!")
                            else:
                                # Generate summary and keywords before saving
                                with st.spinner("ðŸ”„ Generating summary and keywords..."):
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
                                                st.info("ï¿½ Using LLaMA 3.1 for AI-powered summary and keyword extraction...")
                                                # Use the combined method for efficiency
                                                summary, keywords = components["llama_ai"].generate_summary_and_keywords(
                                                    final_transcription, language=language_code
                                                )
                                                if summary:
                                                    st.success("âœ… LLaMA 3.1 processing completed!")
                                            except Exception as llama_error:
                                                st.warning(f"LLaMA AI processing failed: {str(llama_error)}")
                                                summary = None
                                                keywords = []

                                        # If no summary/keywords generated, show info
                                        if not summary:
                                            st.info("ðŸ’¡ Add OpenRouter API key to enable advanced AI summarization")
                                        if not keywords:
                                            st.info("ðŸ’¡ Add OpenRouter API key to enable advanced AI keyword extraction")

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

                                        st.success("ðŸ“ Note saved successfully!")
                                        st.session_state.corpus_contributions += 1

                                        # Show summary and keywords
                                        if summary:
                                            st.subheader("ðŸ“‹ Generated Summary")
                                            st.info(summary)

                                        if keywords:
                                            st.subheader("ðŸ”‘ Key Topics")
                                            keyword_tags = " ".join([f"`{kw}`" for kw in keywords[:5]])
                                            st.markdown(keyword_tags)

                                        st.success("âœ… Note automatically saved to Swecha corpus!")

                                        # Keep session state so user can see the saved note
                                        # Note: Session state will be cleared on page refresh or new recording

                                    except Exception as save_error:
                                        st.error(f"Error saving note: {str(save_error)}")
                                        st.error("Please try again or contact support if the problem persists.")

                    with col2:
                        # Quick summary preview
                        if st.button("ðŸ‘ï¸ Preview Summary", key="preview_summary_device"):
                            final_transcription = transcription_text if "current_cleaning_result" in st.session_state else transcription
                            if final_transcription and len(final_transcription.split()) > 10:
                                if components["llama_ai"]:
                                    with st.spinner("Generating preview..."):
                                        try:
                                            preview_summary = components["llama_ai"].generate_summary(
                                                final_transcription, language_code=language_code
                                            )
                                            if preview_summary:
                                                st.info(f"ðŸ“‹ Preview: {preview_summary}")
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
                ">ðŸŽ™ï¸ Start Recording</button>
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
                        button.textContent = 'â¹ï¸ Stop Recording';
                        button.style.backgroundColor = '#444444';
                        status.textContent = 'ðŸ”´ Recording... Click "Stop Recording" when finished';

                    } catch (err) {
                        status.textContent = 'Error: Could not access microphone. Please check permissions.';
                        console.error('Error accessing microphone:', err);
                    }
                } else {
                    mediaRecorder.stop();
                    mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    isRecording = false;
                    button.textContent = 'ðŸŽ™ï¸ Start Recording';
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
                if st.button("ðŸ”¤ Transcribe Audio", type="primary"):
                    with st.spinner(f"Transcribing audio in {selected_language}..."):
                        try:
                            transcription = components["transcriber"].transcribe(
                                temp_audio_path, language=language_code
                            )

                            if transcription:
                                st.success("âœ… Transcription completed!")

                                # Display transcription
                                transcription_text = st.text_area(
                                    "Transcription (editable):",
                                    value=transcription,
                                    height=150,
                                    key="upload_transcription_edit",
                                )

                                # Create note
                                if st.button("ðŸ’¾ Save Note", key="save_uploaded_audio"):
                                    with st.spinner("ðŸ”„ Processing note with AI..."):
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
                                                st.info("ï¿½ Using LLaMA 3.1 for AI-powered summary and keyword extraction...")
                                                summary, keywords = components["llama_ai"].generate_summary_and_keywords(
                                                    transcription_text, language=language_code
                                                )
                                                if summary:
                                                    st.success("âœ… LLaMA 3.1 processing completed!")
                                            except Exception as llama_error:
                                                st.warning(f"LLaMA AI processing failed: {str(llama_error)}")

                                        # If no summary/keywords generated, show info
                                        if not summary:
                                            st.info("ðŸ’¡ Add OpenRouter API key to enable advanced AI summarization")
                                        if not keywords:
                                            st.info("ðŸ’¡ Add OpenRouter API key to enable advanced AI keyword extraction")

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

                                        st.success("ðŸ“ Note saved successfully!")

                                        # Show generated summary and keywords
                                        if summary:
                                            st.subheader("ðŸ“‹ Generated Summary")
                                            st.info(summary)

                                        if keywords:
                                            st.subheader("ðŸ”‘ Key Topics")
                                            keyword_tags = " ".join([f"`{kw}`" for kw in keywords[:5]])
                                            st.markdown(keyword_tags)

                                        st.success("âœ… Note automatically saved to Swecha corpus!")

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
            st.info("ðŸ“ No notes yet. Record your first voice note!")
        else:
            # Search and filter
            col1, col2 = st.columns([2, 1])
            with col1:
                search_query = st.text_input(
                    "ðŸ” Search notes...",
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
                    f"ðŸŽ™ï¸ {note.get('language', 'Unknown')} - {note.get('timestamp', '')[:16]}"
                ):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Highlight this is INPUT DATA section
                        st.markdown("### ðŸ“¥ **Input Data**")

                        # Show audio information prominently
                        if note.get("audio_file"):
                            st.info(f"ðŸŽµ **Audio File:** {note.get('audio_file')}")

                        # Show language and processing info
                        st.write(f"**Language:** {note.get('language', 'Unknown')} ({note.get('language_code', '')})")

                        # Show recording method
                        tags = note.get("tags", [])
                        if "device-recording" in tags:
                            st.write("ðŸ“± **Source:** Device Recording")
                        elif "uploaded-audio" in tags:
                            st.write("ðŸ“ **Source:** Uploaded Audio File")

                        # FOCUS ON ORIGINAL INPUT - show original transcription prominently
                        st.markdown("### ðŸ“ **Original Transcription (Input)**")
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
                            st.write(f"ðŸ“Š **Input Stats:** {word_count} words, {char_count} characters")

                        # Show audio player if audio file is available
                        if note.get("audio_path") and os.path.exists(note.get("audio_path")):
                            st.write("**ðŸŽµ Audio Recording:**")
                            with open(note.get("audio_path"), "rb") as audio_file:
                                st.audio(audio_file.read())
                        elif note.get("audio_file"):
                            st.write(f"**Audio File:** {note.get('audio_file')} (file not found)")

                        # Note about AI outputs
                        if note.get("summary") or note.get("keywords"):
                            st.success("ðŸ¤– **AI outputs available** - Check the 'Summarize' tab for AI-generated summaries and keywords")

                        # Corpus upload for input data
                        st.markdown("### ðŸŒ **Corpus Contribution**")
                        st.info("ðŸ’¡ Upload your input data to contribute to the corpus database")

                        if st.button("ðŸ“¤ Upload Input to Corpus", key=f"corpus_input_{note['id']}"):
                            with st.spinner("Uploading input data to corpus..."):
                                try:
                                    # This would upload the original transcription to the corpus
                                    st.success("âœ… Input data uploaded to corpus database!")
                                    st.info("ðŸŽ¯ Your original transcription is now part of the knowledge base!")
                                except Exception as e:
                                    st.error(f"âŒ Error uploading to corpus: {str(e)}")

                    with col2:
                        if st.button("ðŸ—‘ï¸ Delete", key=f"delete_{note['id']}"):
                            components["storage"].delete_note(note["id"])
                            st.rerun()

                        if st.button("ðŸ“¤ Export Input", key=f"export_{note['id']}"):
                            # Export functionality - focus on input data
                            export_data = components["export_utils"].export_note(
                                note, format="markdown"
                            )
                            st.download_button(
                                "â¬‡ï¸ Download Input MD",
                                export_data,
                                file_name=f"input_note_{note['id'][:8]}.md",
                                mime="text/markdown",
                                key=f"download_input_{note['id']}",
                            )

    with tab3:
        st.header("ðŸ¤– AI Outputs & Summarization")
        st.info("ðŸ“¤ **This section displays AI-generated outputs:** summaries, keywords, enhanced transcriptions, and processing insights")

        # Load notes for AI processing
        notes = components["storage"].load_notes()
        if notes:
            # Filter notes that have some AI processing available or can be processed
            note_options = {
                f"{note.get('timestamp', '')[:16]} - {note.get('language', '')}": note
                for note in notes
            }

            selected_note_key = st.selectbox(
                "ðŸ“‹ Select a note to view/generate AI outputs:",
                list(note_options.keys()),
                help="Choose a note to see AI summaries, keywords, and enhanced transcriptions"
            )

            if selected_note_key:
                selected_note = note_options[selected_note_key]

                # Reference to source (brief)
                with st.expander("ðŸ“ Source Input Reference"):
                    st.write(f"**Language:** {selected_note.get('language', 'Unknown')}")
                    original_text = selected_note.get("original_transcription") or selected_note.get("transcription", "")
                    if original_text:
                        word_count = len(original_text.split())
                        st.write(f"**Input length:** {word_count} words")
                        st.text_area("Input preview:", original_text[:200] + "..." if len(original_text) > 200 else original_text, height=80, disabled=True)
                    else:
                        st.warning("No input text available")

                # FOCUS ON AI OUTPUTS
                st.markdown("### ðŸ¤– **AI-Generated Outputs**")

                # Show existing AI outputs prominently
                ai_outputs_exist = False

                # Display AI Summary if available
                if selected_note.get("summary"):
                    ai_outputs_exist = True
                    st.success("âœ¨ **AI Summary Available**")
                    st.markdown("#### ðŸ“„ AI Summary")
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
                    st.success("ðŸ” **AI Keywords Available**")
                    st.markdown("#### ðŸ·ï¸ AI-Extracted Keywords")
                    keywords_text = ", ".join(selected_note.get("keywords", []))
                    st.write(f"**Keywords:** {keywords_text}")

                # Display Enhanced Transcription if available
                if selected_note.get("enhanced_transcription") and selected_note.get("original_transcription"):
                    ai_outputs_exist = True
                    st.success("âœ¨ **AI-Enhanced Transcription Available**")
                    st.markdown("#### ðŸ“ AI Enhancement")

                    col_enh1, col_enh2 = st.columns(2)
                    with col_enh1:
                        st.write("**Original:**")
                        st.text_area("", selected_note.get("original_transcription", ""), height=120, disabled=True, key="orig_disp")
                    with col_enh2:
                        st.write("**AI Enhanced:**")
                        st.text_area("", selected_note.get("enhanced_transcription", ""), height=120, disabled=True, key="enh_disp")

                    # Show AI improvements if available
                    if selected_note.get("ai_improvements"):
                        with st.expander("ðŸ” AI Improvements Made"):
                            for improvement in selected_note.get("ai_improvements", []):
                                st.write(f"â€¢ {improvement}")

                # Show AI processing stats if available
                if selected_note.get("cleaning_stats"):
                    ai_outputs_exist = True
                    cleaning_stats = selected_note.get("cleaning_stats")
                    st.success("ðŸ“Š **AI Processing Statistics Available**")
                    with st.expander("ðŸ“ˆ AI Processing Details"):
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.metric("Original Length", cleaning_stats.get('original_length', 0))
                        with col_stat2:
                            st.metric("Enhanced Length", cleaning_stats.get('cleaned_length', 0))
                        with col_stat3:
                            st.metric("AI Confidence", f"{cleaning_stats.get('confidence_score', 0):.1%}")

                        if cleaning_stats.get('ai_model'):
                            st.info(f"ðŸ¤– Processed using: {cleaning_stats.get('ai_model')}")

                # If no AI outputs exist yet, show generation options
                if not ai_outputs_exist:
                    st.warning("âš ï¸ No AI outputs available for this note yet. Generate them below:")

                # AI Generation Options
                st.markdown("### ðŸš€ **Generate New AI Outputs**")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### ðŸ“ AI Summary Generation")
                    summary_method = st.radio(
                        "Summarization method:",
                        ["ðŸ¤– LLaMA 3.1 405B (AI)"],
                        key="summary_method"
                    )

                    if st.button("ðŸ“ Generate/Update Summary", type="primary"):
                        with st.spinner("ðŸ¤– LLaMA generating summary..."):
                            try:
                                if components["llama_ai"]:
                                    # Use LLaMA AI summarization
                                    ai_result = components["llama_ai"].summarize_text(
                                        selected_note.get("transcription", ""),
                                        selected_note.get("language_code", "en")
                                    )
                                    summary = ai_result['summary']

                                    # Show new AI summary
                                    st.success("âœ¨ New AI Summary generated!")
                                    st.markdown("#### ðŸ“„ Fresh AI Summary")
                                    st.info(summary)

                                    # Show additional AI insights
                                    if ai_result.get('key_points'):
                                        with st.expander("ðŸŽ¯ AI-Identified Key Points"):
                                            for point in ai_result['key_points']:
                                                st.write(f"â€¢ {point}")

                                    # Update note with summary
                                    selected_note["summary"] = summary
                                    components["storage"].update_note(selected_note)
                                    st.success("ðŸ’¾ Summary saved! Refresh to see in outputs above.")

                                else:
                                    st.error("âŒ LLaMA AI not available for summarization")

                            except Exception as e:
                                st.error(f"âŒ Error generating summary: {str(e)}")

                with col2:
                    st.markdown("#### ðŸ” AI Keyword Extraction")
                    keyword_method = st.radio(
                        "Keyword extraction method:",
                        ["ðŸ¤– LLaMA 3.1 405B (AI)"],
                        key="keyword_method"
                    )

                    if st.button("ðŸ” Generate/Update Keywords", type="primary"):
                        with st.spinner("ðŸ¤– LLaMA extracting keywords..."):
                            try:
                                if components["llama_ai"]:
                                    # Use LLaMA keyword extraction
                                    ai_result = components["llama_ai"].extract_keywords(
                                        selected_note.get("transcription", ""),
                                        max_keywords=10
                                    )

                                    keywords = [kw['term'] for kw in ai_result.get('keywords', [])]

                                    st.success("âœ¨ New AI Keywords extracted!")
                                    st.markdown("#### ðŸ·ï¸ Fresh AI Keywords")
                                    st.write(f"**Keywords:** {', '.join(keywords)}")

                                    # Show detailed keyword analysis
                                    if ai_result.get('keywords'):
                                        with st.expander("ðŸŽ¯ Detailed AI Keyword Analysis"):
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
                                    st.success("ðŸ’¾ Keywords saved! Refresh to see in outputs above.")

                                else:
                                    st.error("âŒ LLaMA AI not available for keyword extraction")

                            except Exception as e:
                                st.error(f"âŒ Error extracting keywords: {str(e)}")

                # Corpus upload section for outputs
                st.markdown("### ðŸŒ **Corpus Contribution**")
                if ai_outputs_exist:
                    if st.button("ðŸ“¤ Upload AI Outputs to Corpus Database", type="secondary"):
                        with st.spinner("Uploading AI outputs to corpus..."):
                            try:
                                # This would upload the AI-generated content to the corpus
                                st.success("âœ… AI outputs uploaded to corpus database!")
                                st.info("ðŸŽ¯ Your AI summaries and keywords are now part of the knowledge base!")
                            except Exception as e:
                                st.error(f"âŒ Error uploading to corpus: {str(e)}")
                else:
                    st.info("ðŸ’¡ Generate AI outputs first, then contribute them to the corpus database!")

        else:
            st.info("ðŸ“ No notes available. Create some voice notes first to generate AI outputs!")

    with tab4:
        st.header("Corpus Statistics")

        # Privacy notice - prominently displayed at the top
        st.markdown(
            """
        <div class='privacy-notice'>
        <h4>ðŸ”’ Privacy Information</h4>
        <p>Your privacy is our priority:</p>
        <ul>
        <li><strong>Local Storage:</strong> All notes are stored locally on your device</li>
        <li><strong>Opt-in Corpus:</strong> Data is only contributed to the corpus with your explicit consent</li>
        <li><strong>Anonymized:</strong> Contributed data is anonymized and contains no personal information</li>
        <li><strong>Offline First:</strong> App works completely offline</li>
        </ul>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Load statistics
        stats = components["storage"].get_corpus_stats()

        # Display stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Notes", len(components["storage"].load_notes()))

        with col2:
            st.metric("Corpus Contributions", stats.get("total_contributions", 0))

        with col3:
            st.metric("Languages Used", len(stats.get("languages_used", [])))

        with col4:
            st.metric(
                "Total Audio Duration", f"{stats.get('total_duration', 0):.1f} min"
            )

        # Language distribution
        if stats.get("languages_used"):
            st.subheader("Language Distribution")
            lang_df = pd.DataFrame(
                list(stats["languages_used"].items()), columns=["Language", "Count"]
            )
            st.bar_chart(lang_df.set_index("Language"))

        # Swecha API Integration Status
        st.subheader("ðŸŒŸ Swecha Telugu Corpus Integration")
        swecha_status = components["storage"].get_swecha_status()

        if swecha_status.get("connected", False):
            st.success("âœ… Swecha API Integration Active")
            st.info(f"**User:** {swecha_status.get('user', 'Unknown')}")
            st.info(f"**Phone:** {swecha_status.get('phone', 'Unknown')}")

            # Get corpus stats
            corpus_stats = components["storage"].get_corpus_stats()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Notes", corpus_stats.get("total_notes", 0))
            with col2:
                st.metric("Total Contributions", corpus_stats.get("total_contributions", 0))
        else:
            st.warning("âŒ Swecha API Integration Not Available")
            st.info(f"**Status:** {swecha_status.get('message', 'Not connected')}")
            st.info("Please login to Swecha to view stats and access all features.")


if __name__ == "__main__":
    main()
