#!/usr/bin/env python3
"""
Swecha Authentication and Upload Manager
Handles user authentication and file uploads to Swecha API
"""

import math
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st


class SwechaAuthManager:
    """Manages authentication with Swecha API"""

    def __init__(self, base_url: str = "https://api.corpus.swecha.org/api/v1"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def login_user(self, phone: str, password: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Authenticate user with Swecha API

        Args:
            phone: User's phone number
            password: User's password

        Returns:
            Tuple of (token, user_data) or (None, None) if login fails
        """
        try:
            # Step 1: Login to get access token
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"phone": phone, "password": password}
            )
            response.raise_for_status()

            data = response.json()
            token = data.get('access_token')

            if not token:
                st.error("No access token received from login")
                return None, None

            # Step 2: Get user profile with token
            headers = {"Authorization": f"Bearer {token}"}
            user_response = self.session.get(f"{self.base_url}/auth/me", headers=headers)
            user_response.raise_for_status()

            user_data = user_response.json()
            return token, user_data

        except requests.exceptions.RequestException as e:
            st.error(f"Login failed: {str(e)}")
            return None, None
        except Exception as e:
            st.error(f"Login failed: {str(e)}")
            return None, None

    def register_user(self, name: str, phone: str, email: str, password: str, place: str = "") -> Tuple[bool, str]:
        """
        Register a new user with Swecha API

        Args:
            name: User's full name
            phone: User's phone number
            email: User's email address
            password: User's password
            place: User's location (optional)

        Returns:
            Tuple of (success, message)
        """
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "password": password,
                    "place": place
                }
            )

            if response.status_code == 201:
                return True, "Registration successful! You can now login with your credentials."
            elif response.status_code == 400:
                error_data = response.json()
                return False, f"Registration failed: {error_data.get('detail', 'Invalid data provided')}"
            elif response.status_code == 409:
                return False, "Registration failed: User with this phone number or email already exists."
            else:
                response.raise_for_status()
                return False, f"Registration failed: Server returned status {response.status_code}"

        except requests.exceptions.RequestException as e:
            return False, f"Registration failed: {str(e)}"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"

    def get_categories(self, token: str) -> List[Dict[str, Any]]:
        """
        Get available categories from Swecha API

        Args:
            token: Bearer token for authentication

        Returns:
            List of category dictionaries
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{self.base_url}/categories/", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Could not load categories: {str(e)}")
            return []

    def validate_token(self, token: str) -> bool:
        """
        Validate if token is still valid

        Args:
            token: Bearer token to validate

        Returns:
            True if token is valid, False otherwise
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.get(f"{self.base_url}/auth/me", headers=headers)
            return response.status_code == 200
        except Exception:
            return False


class SwechaUploadManager:
    """Manages file uploads to Swecha API with chunking support"""

    def __init__(self, base_url: str = "https://api.corpus.swecha.org/api/v1"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.chunk_size = 5 * 1024 * 1024  # 5MB chunks

    def upload_file_in_chunks(self, token: str, upload_uuid: str, file_content: bytes,
                            filename: str, file_type: str) -> bool:
        """
        Upload file in chunks to Swecha API

        Args:
            token: Bearer token for authentication
            upload_uuid: Unique identifier for the upload
            file_content: File content as bytes
            filename: Name of the file
            file_type: MIME type of the file

        Returns:
            True if upload successful, False otherwise
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            file_size = len(file_content)
            total_chunks = math.ceil(file_size / self.chunk_size)

            st.info(f"Uploading '{filename}' ({file_size / (1024*1024):.2f} MB) in {total_chunks} chunk(s)...")
            progress_bar = st.progress(0)

            for i in range(total_chunks):
                # Get chunk data
                start = i * self.chunk_size
                end = start + self.chunk_size
                chunk_data = file_content[start:end]

                # Prepare chunk upload
                files = {'chunk': (filename, chunk_data, file_type)}
                data = {
                    "upload_uuid": upload_uuid,
                    "chunk_index": i,
                    "total_chunks": total_chunks,
                    "filename": filename,
                }

                response = self.session.post(
                    f"{self.base_url}/records/upload/chunk",
                    headers=headers,
                    data=data,
                    files=files
                )
                response.raise_for_status()

                # Update progress
                progress_bar.progress((i + 1) / total_chunks)

            st.success(f"All {total_chunks} chunks for '{filename}' uploaded successfully.")
            return True

        except Exception as e:
            st.error(f"File upload failed for {filename}: {str(e)}")
            return False

    def finalize_record(self, token: str, record_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Finalize record after successful file upload

        Args:
            token: Bearer token for authentication
            record_data: Record metadata

        Returns:
            Response data if successful, None otherwise
        """
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.session.post(
                f"{self.base_url}/records/",
                headers=headers,
                json=record_data
            )
            response.raise_for_status()

            st.info(f"Finalizing record for: {record_data['filename']}")
            return response.json()

        except Exception as e:
            st.error(f"Finalization failed for {record_data['filename']}: {str(e)}")
            return None


class SwechaIntegrationManager:
    """Main manager that combines authentication and upload functionality"""

    def __init__(self):
        self.auth_manager = SwechaAuthManager()
        self.upload_manager = SwechaUploadManager()
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize Streamlit session state for Swecha integration"""
        if 'swecha_logged_in' not in st.session_state:
            st.session_state.swecha_logged_in = False
        if 'swecha_token' not in st.session_state:
            st.session_state.swecha_token = None
        if 'swecha_user' not in st.session_state:
            st.session_state.swecha_user = None
        if 'swecha_categories' not in st.session_state:
            st.session_state.swecha_categories = []

    def show_login_form(self) -> bool:
        """
        Display Swecha login form

        Returns:
            True if login successful, False otherwise
        """
        st.subheader("🔐 Swecha API Authentication")
        st.write("Login to contribute your voice notes to the Swecha Telugu Corpus")

        with st.form("swecha_login_form"):
            phone = st.text_input("Phone Number", placeholder="+91XXXXXXXXXX")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login to Swecha")

            if submitted:
                if phone and password:
                    with st.spinner("Authenticating with Swecha API..."):
                        token, user = self.auth_manager.login_user(phone, password)

                        if token and user:
                            st.session_state.swecha_logged_in = True
                            st.session_state.swecha_token = token
                            st.session_state.swecha_user = user

                            # Load categories
                            categories = self.auth_manager.get_categories(token)
                            st.session_state.swecha_categories = categories

                            st.success(f"✅ Successfully logged in as {user.get('name', 'User')}")
                            st.rerun()
                            return True
                        else:
                            st.error("❌ Login failed. Please check your credentials.")
                            return False
                else:
                    st.warning("Please enter both phone number and password")
                    return False

        return False

    def show_signup_form(self) -> bool:
        """
        Display Swecha signup form

        Returns:
            True if signup successful, False otherwise
        """
        st.subheader("📝 Create Swecha Account")
        st.write("Join the Swecha Telugu Corpus community and contribute your voice notes")

        with st.form("swecha_signup_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Full Name *", placeholder="Enter your full name")
                phone = st.text_input("Phone Number *", placeholder="+91XXXXXXXXXX")

            with col2:
                email = st.text_input("Email Address *", placeholder="your.email@example.com")
                place = st.text_input("Location (Optional)", placeholder="City, State")

            password = st.text_input("Password *", type="password", placeholder="Choose a strong password")
            confirm_password = st.text_input("Confirm Password *", type="password", placeholder="Re-enter your password")

            # Terms and conditions
            terms_accepted = st.checkbox("I agree to the Swecha Terms of Service and Privacy Policy")

            submitted = st.form_submit_button("🚀 Create Account")

            if submitted:
                # Validation
                if not all([name, phone, email, password, confirm_password]):
                    st.error("❌ Please fill in all required fields (marked with *)")
                    return False

                if password != confirm_password:
                    st.error("❌ Passwords do not match")
                    return False

                if len(password) < 6:
                    st.error("❌ Password must be at least 6 characters long")
                    return False

                if not terms_accepted:
                    st.error("❌ Please accept the Terms of Service to create an account")
                    return False

                # Email validation
                if "@" not in email or "." not in email:
                    st.error("❌ Please enter a valid email address")
                    return False

                with st.spinner("Creating your Swecha account..."):
                    success, message = self.auth_manager.register_user(name, phone, email, password, place)

                    if success:
                        st.success(f"✅ {message}")
                        st.info("🔐 You can now login with your credentials using the Login button")
                        st.balloons()
                        return True
                    else:
                        st.error(f"❌ {message}")
                        return False

        return False

    def show_user_info(self):
        """Display logged-in user information"""
        if st.session_state.swecha_logged_in and st.session_state.swecha_user:
            user = st.session_state.swecha_user

            st.success(f"✅ Logged in as: **{user.get('name', 'User')}**")

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"📧 Email: {user.get('email', 'N/A')}")
                st.write(f"📱 Phone: {user.get('phone', 'N/A')}")
            with col2:
                st.write(f"📍 Location: {user.get('place', 'N/A')}")
                if st.button("🚪 Logout from Swecha"):
                    self.logout()
                    st.rerun()

    def logout(self):
        """Logout from Swecha and clear session state"""
        st.session_state.swecha_logged_in = False
        st.session_state.swecha_token = None
        st.session_state.swecha_user = None
        st.session_state.swecha_categories = []

    def is_logged_in(self) -> bool:
        """Check if user is logged in to Swecha"""
        if not st.session_state.swecha_logged_in:
            return False

        # Validate token if we have one
        if st.session_state.swecha_token and not self.auth_manager.validate_token(st.session_state.swecha_token):
            self.logout()
            return False

        return True

    def upload_voice_note(self, note_data: Dict[str, Any], audio_file_path: Optional[str] = None) -> bool:
        """
        Upload a voice note to Swecha corpus

        Args:
            note_data: Note metadata including transcription, language, etc.
            audio_file_path: Optional path to audio file

        Returns:
            True if upload successful, False otherwise
        """
        if not self.is_logged_in():
            st.error("Please login to Swecha first")
            return False

        token = st.session_state.swecha_token
        user = st.session_state.swecha_user
        categories = st.session_state.swecha_categories

        if not categories:
            st.error("No categories available. Please contact administrator.")
            return False

        # UI for contribution details
        st.subheader("📤 Contribute to Swecha Corpus")

        with st.form("swecha_contribution_form"):
            # Basic info
            title = st.text_input("Title", value=f"Voice Note - {note_data.get('timestamp', '')}")
            short_desc = st.text_area("Short Description",
                                    value=f"Voice note transcription in {note_data.get('language', 'Unknown')}")

            # Category selection
            category_options = {cat['name']: cat['id'] for cat in categories}
            if category_options:
                category_name = st.selectbox("Category", options=list(category_options.keys()))
            else:
                st.error("No categories available")
                return False

            # Language and rights
            language_map = {
                "English": "english",
                "Telugu": "telugu",
                "Hindi": "hindi",
                "Tamil": "tamil"
            }

            release_rights_map = {
                "This work is created by me": "creator",
                "I have permission to share this": "family_or_friend",
                "I downloaded this from public domain": "downloaded"
            }

            language_ui = st.selectbox("Language", options=list(language_map.keys()))
            release_rights_ui = st.radio("Release Rights", options=list(release_rights_map.keys()))

            submitted = st.form_submit_button("🚀 Contribute to Swecha")

            if submitted:
                if title and short_desc and category_name:
                    try:
                        upload_uuid = str(uuid.uuid4())

                        # Prepare record data
                        combined_description = f"Short Description: {short_desc}\nTranscription: {note_data.get('transcription', '')}"

                        record_data = {
                            "title": title,
                            "description": combined_description,
                            "content": note_data.get('transcription', ''),
                            "category_id": category_options[category_name],
                            "user_id": user['id'],
                            "upload_uuid": upload_uuid,
                            "filename": f"voice_note_{upload_uuid}.txt",
                            "media_type": "text",
                            "total_chunks": 1,
                            "language": language_map.get(language_ui),
                            "release_rights": release_rights_map.get(release_rights_ui),
                        }

                        # If we have audio file, upload it
                        if audio_file_path and os.path.exists(audio_file_path):
                            with open(audio_file_path, 'rb') as f:
                                audio_content = f.read()

                            audio_uuid = str(uuid.uuid4())
                            audio_filename = f"voice_note_{audio_uuid}.wav"

                            upload_success = self.upload_manager.upload_file_in_chunks(
                                token, audio_uuid, audio_content, audio_filename, "audio/wav"
                            )

                            if upload_success:
                                # Update record for audio
                                audio_record_data = record_data.copy()
                                audio_record_data.update({
                                    "upload_uuid": audio_uuid,
                                    "filename": audio_filename,
                                    "media_type": "audio",
                                    "total_chunks": math.ceil(len(audio_content) / self.upload_manager.chunk_size)
                                })

                                final_response = self.upload_manager.finalize_record(token, audio_record_data)
                                if final_response:
                                    st.success("🎉 Audio file contributed successfully!")
                                    return True
                        else:
                            # Upload transcription as text
                            text_content = note_data.get('transcription', '').encode('utf-8')

                            upload_success = self.upload_manager.upload_file_in_chunks(
                                token, upload_uuid, text_content, record_data['filename'], "text/plain"
                            )

                            if upload_success:
                                final_response = self.upload_manager.finalize_record(token, record_data)
                                if final_response:
                                    st.success("🎉 Voice note transcription contributed successfully!")
                                    return True

                        st.error("❌ Upload failed")
                        return False

                    except Exception as e:
                        st.error(f"❌ Error during upload: {str(e)}")
                        return False
                else:
                    st.warning("Please fill in all required fields")
                    return False

        return False
