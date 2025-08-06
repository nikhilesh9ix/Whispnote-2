import os
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st

from src.ai.keyword_extractor import KeywordExtractor
from src.ai.ocr_reader import OCRReader
from src.ai.summarizer import IndicBARTSummarizer

# Import custom modules
from src.ai.whisper_transcriber import WhisperTranscriber
from src.utils.export_utils import ExportUtils
from src.utils.storage import StorageManager

# Page config
st.set_page_config(
    page_title="WhispNote - AI Voice Notes",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize session state
def init_session_state():
    if "notes" not in st.session_state:
        st.session_state.notes = []
    if "current_note" not in st.session_state:
        st.session_state.current_note = None
    if "privacy_consent" not in st.session_state:
        st.session_state.privacy_consent = False
    if "corpus_contributions" not in st.session_state:
        st.session_state.corpus_contributions = 0


# Initialize components
@st.cache_resource
def load_components():
    return {
        "transcriber": WhisperTranscriber(),
        "summarizer": IndicBARTSummarizer(),
        "keyword_extractor": KeywordExtractor(),
        "ocr_reader": OCRReader(),
        "storage": StorageManager(),
        "export_utils": ExportUtils(),
    }


def main():
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

        # App info
        st.subheader("About")
        st.info("""
        **WhispNote** is an offline-first, privacy-focused voice note app that:
        - Records and transcribes speech in Indian languages
        - Summarizes content using AI
        - Extracts keywords and topics
        - Supports OCR for image text
        - Optionally contributes to language corpus
        """)

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
                                    key="device_transcription_edit",
                                )

                                # Save note option
                                if st.button(
                                    "📝 Save Note", key="save_device_recording"
                                ):
                                    note_data = {
                                        "id": str(uuid.uuid4()),
                                        "timestamp": datetime.now().isoformat(),
                                        "language": selected_language,
                                        "language_code": language_code,
                                        "transcription": transcription_text,
                                        "audio_file": device_audio.name,
                                        "summary": None,
                                        "keywords": [],
                                        "tags": ["device-recording"],
                                    }

                                    components["storage"].save_note(note_data)

                                    if privacy_consent:
                                        components["storage"].contribute_to_corpus(
                                            temp_audio_path,
                                            transcription_text,
                                            language_code,
                                        )
                                        st.session_state.corpus_contributions += 1

                                    st.success("📝 Note saved successfully!")
                                    st.rerun()

                        except Exception as e:
                            st.error(f"Error during transcription: {str(e)}")

                        finally:
                            # Clean up temp file
                            if os.path.exists(temp_audio_path):
                                os.remove(temp_audio_path)

            # Add browser-based recording option
            st.markdown("---")
            st.subheader("Browser Recording (Experimental)")

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

            st.components.v1.html(browser_recording_html, height=200)

            st.warning("""
            **Note**: Browser recording is experimental and recordings cannot be directly processed yet.
            For best results, please use your device's voice recorder app and upload the file.
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
                                    note_data = {
                                        "id": str(uuid.uuid4()),
                                        "timestamp": datetime.now().isoformat(),
                                        "language": selected_language,
                                        "language_code": language_code,
                                        "transcription": transcription_text,
                                        "audio_file": uploaded_audio.name,
                                        "summary": None,
                                        "keywords": [],
                                        "tags": [],
                                    }

                                    # Save note
                                    components["storage"].save_note(note_data)

                                    # Handle corpus contribution
                                    if privacy_consent:
                                        components["storage"].contribute_to_corpus(
                                            temp_audio_path,
                                            transcription_text,
                                            language_code,
                                        )
                                        st.session_state.corpus_contributions += 1

                                    st.success("📝 Note saved successfully!")
                                    st.rerun()

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

            # Display notes
            for note in reversed(filtered_notes):  # Show newest first
                with st.expander(
                    f"📝 {note.get('language', 'Unknown')} - {note.get('timestamp', '')[:16]}"
                ):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("**Transcription:**")
                        st.write(note.get("transcription", ""))

                        if note.get("summary"):
                            st.write("**Summary:**")
                            st.info(note.get("summary"))

                        if note.get("keywords"):
                            st.write("**Keywords:**")
                            st.write(", ".join(note.get("keywords", [])))

                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{note['id']}"):
                            components["storage"].delete_note(note["id"])
                            st.rerun()

                        if st.button("📤 Export", key=f"export_{note['id']}"):
                            # Export functionality
                            export_data = components["export_utils"].export_note(
                                note, format="markdown"
                            )
                            st.download_button(
                                "⬇️ Download MD",
                                export_data,
                                file_name=f"note_{note['id'][:8]}.md",
                                mime="text/markdown",
                                key=f"download_{note['id']}",
                            )

    with tab3:
        st.header("Summarize & Extract Keywords")

        # Load notes for summarization
        notes = components["storage"].load_notes()
        if notes:
            note_options = {
                f"{note.get('timestamp', '')[:16]} - {note.get('language', '')}": note
                for note in notes
            }

            selected_note_key = st.selectbox(
                "Select a note to summarize:", list(note_options.keys())
            )

            if selected_note_key:
                selected_note = note_options[selected_note_key]

                st.write("**Original Transcription:**")
                st.write(selected_note.get("transcription", ""))

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("📝 Generate Summary"):
                        with st.spinner("Generating summary..."):
                            try:
                                summary = components["summarizer"].summarize(
                                    selected_note.get("transcription", ""),
                                    selected_note.get("language_code", "en"),
                                )

                                # Update note with summary
                                selected_note["summary"] = summary
                                components["storage"].update_note(selected_note)

                                st.success("Summary generated!")
                                st.write("**Summary:**")
                                st.info(summary)

                            except Exception as e:
                                st.error(f"Error generating summary: {str(e)}")

                with col2:
                    if st.button("🔍 Extract Keywords"):
                        with st.spinner("Extracting keywords..."):
                            try:
                                keywords = components[
                                    "keyword_extractor"
                                ].extract_keywords(
                                    selected_note.get("transcription", ""),
                                    num_keywords=10,
                                )

                                # Update note with keywords
                                selected_note["keywords"] = keywords
                                components["storage"].update_note(selected_note)

                                st.success("Keywords extracted!")
                                st.write("**Keywords:**")
                                st.write(", ".join(keywords))

                            except Exception as e:
                                st.error(f"Error extracting keywords: {str(e)}")
        else:
            st.info(
                "No notes available for summarization. Create some voice notes first!"
            )

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
                                note_data = {
                                    "id": str(uuid.uuid4()),
                                    "timestamp": datetime.now().isoformat(),
                                    "language": "OCR Text",
                                    "language_code": "en",
                                    "transcription": final_text,
                                    "audio_file": None,
                                    "summary": None,
                                    "keywords": [],
                                    "tags": ["OCR"],
                                    "source": "OCR",
                                }

                                components["storage"].save_note(note_data)
                                st.success("📝 OCR text saved as note!")
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
        st.header("Corpus Statistics")

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
        st.subheader("🌟 Swecha Telugu Corpus Integration")
        swecha_status = components["storage"].get_swecha_status()

        if swecha_status["available"]:
            api_status = swecha_status["api_status"]
            st.success("✅ Swecha API Integration Active")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Swecha Contributions", swecha_status["contributions_count"])
            with col2:
                last_contrib = swecha_status["last_contribution"]
                if last_contrib != "Never":
                    try:
                        # Format the datetime nicely
                        from datetime import datetime as dt

                        dt_obj = dt.fromisoformat(last_contrib.replace("Z", "+00:00"))
                        formatted_date = dt_obj.strftime("%Y-%m-%d %H:%M")
                        st.metric("Last Contribution", formatted_date)
                    except Exception:
                        st.metric("Last Contribution", "Recently")
                else:
                    st.metric("Last Contribution", "Never")

            # Bearer token status
            has_token = (
                "🔑 Authenticated"
                if api_status.get("capabilities", {}).get(
                    "authentication_required", False
                )
                else "🔓 No Auth Required"
            )
            st.info(f"**Authentication Status:** {has_token}")

            # API details
            with st.expander("🔧 API Details"):
                st.write(f"**API URL:** {api_status.get('base_url', 'N/A')}")
                st.write(
                    f"**API Available:** {'✅ Yes' if api_status.get('api_available', False) else '❌ No'}"
                )
                if api_status.get("api_info"):
                    st.write(
                        f"**API Version:** {api_status['api_info'].get('version', 'Unknown')}"
                    )
                    st.write(
                        f"**Message:** {api_status['api_info'].get('message', 'N/A')}"
                    )

                # Show available endpoints
                endpoints = api_status.get("capabilities", {}).get(
                    "available_endpoints", []
                )
                if endpoints:
                    st.write("**Available Endpoints:**")
                    for endpoint in endpoints:
                        st.write(f"  • `{endpoint}`")

                # Contribution status
                contrib_supported = api_status.get("capabilities", {}).get(
                    "contribution_supported", False
                )
                st.write(
                    f"**Contribution Endpoints:** {'✅ Available' if contrib_supported else '⏳ Coming Soon'}"
                )

                if not contrib_supported:
                    st.warning(
                        "📝 **Note:** Contribution endpoints are not yet available. Telugu transcriptions will be stored locally for future upload when the API is ready."
                    )
        else:
            st.warning(
                f"⚠️ Swecha Integration Unavailable: {swecha_status.get('reason', 'Unknown')}"
            )
            st.info("""
            **About Swecha Telugu Corpus:**
            The Swecha API allows WhispNote to contribute Telugu transcriptions to a community corpus for language research and development.
            Your Telugu voice notes can help improve Telugu language technology!

            **Current Status:** The API is accessible but contribution endpoints are still being developed.
            """)

        # Privacy notice
        st.markdown(
            """
        <div class='privacy-notice'>
        <h4>🔒 Privacy Information</h4>
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


if __name__ == "__main__":
    main()
