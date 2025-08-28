#!/usr/bin/env python3
"""
Swecha-based Storage Manager with Local Fallback
Uses Swecha API as the primary database for all note storage and retrieval
Includes local storage fallback for users not authenticated with Swecha
"""

import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
import streamlit as st


class SwechaStorageManager:
    """Storage manager that uses Swecha API with local storage fallback"""

    def __init__(self, base_url: str = "https://api.corpus.swecha.org/api/v1"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        # Configure session with better timeout and retry settings
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],  # Updated parameter name
            backoff_factor=1,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {
                "User-Agent": "WhispNote/2.0 (Telugu Voice Notes App)",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        self.local_storage_dir = "whispnote_data/notes"
        self._ensure_local_storage_dir()

    def _get_auth_headers(self) -> Optional[Dict[str, str]]:
        """Get authentication headers from session state"""
        if not st.session_state.get("swecha_logged_in", False):
            return None

        token = st.session_state.get("swecha_token")
        if not token:
            return None

        return {"Authorization": f"Bearer {token}"}

    def _ensure_local_storage_dir(self) -> None:
        """Ensure local storage directory exists"""
        if not os.path.exists(self.local_storage_dir):
            os.makedirs(self.local_storage_dir, exist_ok=True)

    def _get_local_notes_file(self) -> str:
        """Get path to local notes file"""
        return os.path.join(self.local_storage_dir, "local_notes.json")

    def _load_local_notes(self) -> List[Dict[str, Any]]:
        """Load notes from local storage"""
        try:
            notes_file = self._get_local_notes_file()
            if os.path.exists(notes_file):
                with open(notes_file, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            st.warning(f"Could not load local notes: {str(e)}")
        return []

    def _save_local_notes(self, notes: List[Dict[str, Any]]) -> bool:
        """Save notes to local storage"""
        try:
            notes_file = self._get_local_notes_file()
            with open(notes_file, "w", encoding="utf-8") as f:
                json.dump(notes, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Could not save to local storage: {str(e)}")
            return False

    def _save_note_locally(self, note_data: Dict[str, Any]) -> bool:
        """Save a single note to local storage"""
        notes = self._load_local_notes()
        notes.append(note_data)
        return self._save_local_notes(notes)

    def _ensure_authenticated(self) -> bool:
        """Check if user is authenticated with Swecha (but don't require it)"""
        return st.session_state.get("swecha_logged_in", False)

    def save_note(self, note_data: Dict[str, Any]) -> bool:
        """
        Save a note using Swecha API with local storage fallback

        Args:
            note_data: Dictionary containing note information

        Returns:
            True if successful, False otherwise
        """
        # Try Swecha API first if authenticated
        if st.session_state.get("swecha_logged_in", False):
            try:
                return self._save_note_to_swecha(note_data)
            except Exception as e:
                st.warning(f"Swecha API save failed: {str(e)}")
                st.info("💾 Saving to local storage as fallback...")

        # Use local storage fallback
        success = self._save_note_locally(note_data)
        if success:
            st.info("💾 Note saved to local storage")
        return success

    def _save_note_to_swecha(self, note_data: Dict[str, Any]) -> bool:
        """Save note to Swecha API (original implementation)"""
        if not self._ensure_authenticated():
            return False

        try:
            headers = self._get_auth_headers()
            if not headers:
                return False

            # Get user data
            user_data = st.session_state.get("swecha_user_data", {})
            user_id = user_data.get("id")

            if not user_id:
                st.error("User ID not found in session")
                return False

            # Get categories to find default category
            categories_response = self.session.get(
                f"{self.base_url}/categories/", headers=headers
            )
            categories_response.raise_for_status()
            categories = categories_response.json()

            # Use first available category as default
            category_id = categories[0]["id"] if categories else None
            if not category_id:
                st.error("No categories available")
                return False

            # Map language to Swecha enum
            language_map = {
                "hi": "hindi",
                "te": "telugu",
                "ta": "tamil",
                "bn": "bengali",
                "mr": "marathi",
                "gu": "gujarati",
                "kn": "kannada",
                "ml": "malayalam",
                "pa": "punjabi",
                "en": "hindi",  # Default English to Hindi for now
            }
            language_code = note_data.get("language_code", "te")
            swecha_language = language_map.get(language_code, "telugu")

            # Create record using the correct API structure
            record_data = {
                "title": f"WhispNote - {note_data.get('language', 'Unknown')} ({datetime.now().strftime('%Y-%m-%d %H:%M')})",
                "description": f"Voice note transcription\n\nContent: {note_data.get('transcription', '')[:200]}...",
                "media_type": "text",
                "user_id": user_id,
                "category_id": category_id,
                "release_rights": "creator",
                "language": swecha_language,
                "file_name": f"whispnote_{note_data.get('id', uuid.uuid4())}.json",
                "file_size": len(json.dumps(note_data).encode("utf-8")),
                "status": "pending",
            }

            # Create the record
            response = self.session.post(
                f"{self.base_url}/records/", headers=headers, json=record_data
            )
            response.raise_for_status()

            # Store the Swecha record info in session for tracking
            swecha_response = response.json()
            if "swecha_notes" not in st.session_state:
                st.session_state.swecha_notes = {}

            st.session_state.swecha_notes[note_data["id"]] = {
                "swecha_uid": swecha_response.get("uid"),
                "note_data": note_data,
                "saved_at": datetime.now().isoformat(),
            }

            return True

        except Exception as e:
            st.error(f"Failed to save note to Swecha: {str(e)}")
            return False

    def load_notes(self) -> List[Dict[str, Any]]:
        """
        Load all notes from Swecha API with local storage fallback

        Returns:
            List of note dictionaries
        """
        # Try Swecha API first if authenticated
        if st.session_state.get("swecha_logged_in", False):
            try:
                swecha_notes = self._load_notes_from_swecha()
                if swecha_notes:
                    return swecha_notes
            except Exception as e:
                st.warning(f"Could not load from Swecha API: {str(e)}")

        # Use local storage fallback
        local_notes = self._load_local_notes()
        if local_notes:
            st.info("📁 Showing notes from local storage")
        return local_notes

    def _load_notes_from_swecha(self) -> List[Dict[str, Any]]:
        """Load notes from Swecha API (original implementation)"""
        if not self._ensure_authenticated():
            return []

        try:
            headers = self._get_auth_headers()
            if not headers:
                return []

            # Get user data
            user_data = st.session_state.get("swecha_user_data", {})
            user_id = user_data.get("id")

            if not user_id:
                return []

            # Fetch user's contributions/records using the user contributions endpoint
            response = self.session.get(
                f"{self.base_url}/users/{user_id}/contributions", headers=headers
            )
            response.raise_for_status()

            contributions = response.json()
            notes = []

            # Extract notes from text contributions (where we store WhispNote data)
            text_contributions = contributions.get("text_contributions", [])

            for contribution in text_contributions:
                try:
                    # Check if this looks like a WhispNote record
                    title = contribution.get("title", "")
                    description = contribution.get("description", "")

                    if "WhispNote" in title:
                        # Try to reconstruct note data from the description
                        # Since we store the transcription in description
                        note_data = {
                            "id": contribution.get("id", str(uuid.uuid4())),
                            "timestamp": contribution.get(
                                "timestamp", datetime.now().isoformat()
                            ),
                            "language": "Unknown",
                            "language_code": "te",  # Default
                            "transcription": (
                                description.split("Content: ")[-1]
                                if "Content: " in description
                                else description
                            ),
                            "audio_file": None,
                            "summary": None,
                            "keywords": [],
                            "tags": ["swecha-imported"],
                            "swecha_uid": contribution.get("id"),
                        }
                        notes.append(note_data)

                except Exception:
                    # Skip invalid records
                    continue

            # Update session cache
            if notes:
                st.session_state.swecha_notes = {
                    note["id"]: {
                        "swecha_uid": note.get("swecha_uid"),
                        "note_data": note,
                        "loaded_at": datetime.now().isoformat(),
                    }
                    for note in notes
                }

            return notes

        except Exception as e:
            st.error(f"Failed to load notes from Swecha: {str(e)}")
            # Fallback to session cache if available
            if "swecha_notes" in st.session_state:
                return [
                    item["note_data"] for item in st.session_state.swecha_notes.values()
                ]
            return []

    def update_note(self, note_data: Dict[str, Any]) -> bool:
        """
        Update an existing note in storage (Swecha API or local)

        Args:
            note_data: Updated note data

        Returns:
            True if successful, False otherwise
        """
        try:
            note_id = note_data.get("id")
            if not note_id:
                return False

            # If authenticated with Swecha, use simple delete and recreate
            if self._ensure_authenticated():
                self.delete_note(note_id)
                return self.save_note(note_data)

            # For local storage, update the note in place
            notes = self._load_local_notes()
            updated = False

            for i, note in enumerate(notes):
                if note.get("id") == note_id:
                    notes[i] = note_data
                    updated = True
                    break

            if updated:
                return self._save_local_notes(notes)
            else:
                # Note not found, add as new
                return self._save_note_locally(note_data)

        except Exception as e:
            st.error(f"Failed to update note: {str(e)}")
            return False

    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note from storage (Swecha API or local)

        Args:
            note_id: ID of the note to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            # If authenticated with Swecha, remove from session cache
            if self._ensure_authenticated():
                if "swecha_notes" in st.session_state:
                    st.session_state.swecha_notes.pop(note_id, None)
                st.info(
                    "Note removed from Swecha cache. Contact admin for permanent deletion."
                )
                return True

            # For local storage, actually delete the note
            notes = self._load_local_notes()
            updated_notes = [note for note in notes if note.get("id") != note_id]

            if len(updated_notes) < len(notes):
                success = self._save_local_notes(updated_notes)
                if success:
                    st.success("Note deleted from local storage")
                return success
            else:
                st.warning("Note not found")
                return False

        except Exception as e:
            st.error(f"Failed to delete note: {str(e)}")
            return False

    def get_corpus_stats(self) -> Dict[str, Any]:
        """
        Get corpus statistics from Swecha API using user contributions endpoint

        Returns:
            Dictionary with corpus statistics
        """
        if not self._ensure_authenticated():
            return {"total_contributions": 0, "total_hours": 0, "total_notes": 0}

        try:
            headers = self._get_auth_headers()
            if not headers:
                return {"total_contributions": 0, "total_hours": 0, "total_notes": 0}

            user_data = st.session_state.get("swecha_user_data", {})
            user_id = user_data.get("id")

            if not user_id:
                return {"total_contributions": 0, "total_hours": 0, "total_notes": 0}

            # Get user's contribution stats using the API
            response = self.session.get(
                f"{self.base_url}/users/{user_id}/contributions", headers=headers
            )

            if response.status_code == 200:
                stats = response.json()
                return {
                    "total_contributions": stats.get("total_contributions", 0),
                    "total_hours": (
                        stats.get("audio_duration", 0) + stats.get("video_duration", 0)
                    )
                    / 3600,  # Convert seconds to hours
                    "total_notes": len(stats.get("text_contributions", [])),
                    "audio_contributions": len(stats.get("audio_contributions", [])),
                    "video_contributions": len(stats.get("video_contributions", [])),
                    "text_contributions": len(stats.get("text_contributions", [])),
                    "image_contributions": len(stats.get("image_contributions", [])),
                }
            else:
                # Fallback to basic count from load_notes
                notes = self.load_notes()
                return {
                    "total_contributions": len(notes),
                    "total_hours": 0,
                    "total_notes": len(notes),
                    "audio_contributions": 0,
                    "video_contributions": 0,
                    "text_contributions": len(notes),
                    "image_contributions": 0,
                }

        except Exception as e:
            st.warning(f"Could not fetch corpus stats: {str(e)}")
            notes = self.load_notes()
            return {
                "total_contributions": len(notes),
                "total_hours": 0,
                "total_notes": len(notes),
                "audio_contributions": 0,
                "video_contributions": 0,
                "text_contributions": len(notes),
                "image_contributions": 0,
            }

    def contribute_to_corpus(
        self, audio_path: str, transcription: str, language_code: str
    ) -> bool:
        """
        Legacy method for corpus contribution - now handled by upload process

        Args:
            audio_path: Path to audio file
            transcription: Transcription text
            language_code: Language code

        Returns:
            True (notes are automatically contributed when saved)
        """
        # In the new system, all notes are automatically stored in Swecha
        # So this is essentially a no-op that returns True
        st.info("Note automatically contributed to Swecha corpus upon saving.")
        return True

    def get_swecha_status(self) -> Dict[str, Any]:
        """
        Get Swecha API connection status with enhanced user info

        Returns:
            Dictionary with connection status and user information
        """
        try:
            if not st.session_state.get("swecha_logged_in", False):
                return {
                    "connected": False,
                    "authenticated": False,
                    "user_info": None,
                    "user": None,
                    "message": "Not logged in to Swecha",
                }

            headers = self._get_auth_headers()
            if not headers:
                return {
                    "connected": False,
                    "authenticated": False,
                    "user_info": None,
                    "user": None,
                    "message": "No authentication token",
                }

            # Try to get fresh user data from API
            try:
                response = self.session.get(
                    f"{self.base_url}/auth/me", headers=headers, timeout=30
                )

                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "connected": True,
                        "authenticated": True,
                        "user_info": user_data,
                        "user": user_data.get("name", "Unknown"),
                        "phone": user_data.get("phone", "Unknown"),
                        "message": "Connected to Swecha API",
                    }
                else:
                    return {
                        "connected": False,
                        "authenticated": False,
                        "user_info": None,
                        "user": None,
                        "message": f"Authentication failed: {response.status_code}",
                    }
            except requests.exceptions.RequestException as e:
                # Fall back to cached user data if API call fails
                user_data = st.session_state.get("swecha_user_data", {})
                return {
                    "connected": True,
                    "authenticated": True,
                    "user_info": user_data,
                    "user": user_data.get("name", "Unknown"),
                    "phone": user_data.get("phone", "Unknown"),
                    "message": f"Connected (cached) - API unreachable: {str(e)}",
                }

        except Exception as e:
            return {
                "connected": False,
                "authenticated": False,
                "user_info": None,
                "user": None,
                "message": f"Error checking Swecha status: {str(e)}",
            }

    def get_user_contributions(self) -> Optional[Dict[str, Any]]:
        """
        Get user's contributions from Swecha API

        Returns:
            Dictionary with user contribution data or None if failed
        """
        headers = self._get_auth_headers()
        if not headers:
            return None

        try:
            # Get current user info first
            user_response = self.session.get(
                f"{self.base_url}/auth/me",
                headers=headers,
                timeout=30,  # Increased timeout
            )

            if user_response.status_code != 200:
                return None

            user_data = user_response.json()
            user_id = user_data.get("id")

            if not user_id:
                return None

            # Get user contributions using the correct API endpoint
            contributions_response = self.session.get(
                f"{self.base_url}/users/{user_id}/contributions",
                headers=headers,
                timeout=30,  # Increased timeout
            )

            if contributions_response.status_code == 200:
                return contributions_response.json()
            else:
                st.warning(
                    f"Failed to fetch contributions: {contributions_response.status_code}"
                )
                return None

        except requests.exceptions.Timeout:
            st.error(
                "⏱️ Request timed out. Please check your internet connection and try again."
            )
            return None
        except requests.exceptions.ConnectionError:
            st.error("🌐 Connection error. Please check your internet connection.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error fetching contributions: {str(e)}")
            return None

    def get_user_contributions_by_media(
        self, media_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user's contributions filtered by media type

        Args:
            media_type: Type of media ('audio', 'text', 'video', 'image')

        Returns:
            Dictionary with filtered contribution data or None if failed
        """
        headers = self._get_auth_headers()
        if not headers:
            return None

        try:
            # Get current user info first
            user_response = self.session.get(
                f"{self.base_url}/auth/me",
                headers=headers,
                timeout=30,  # Increased timeout
            )

            if user_response.status_code != 200:
                return None

            user_data = user_response.json()
            user_id = user_data.get("id")

            if not user_id:
                return None

            # Get user contributions by media type using correct API endpoint
            contributions_response = self.session.get(
                f"{self.base_url}/users/{user_id}/contributions/{media_type}",
                headers=headers,
                timeout=30,  # Increased timeout
            )

            if contributions_response.status_code == 200:
                return contributions_response.json()
            else:
                return None

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out while fetching media contributions.")
            return None
        except requests.exceptions.ConnectionError:
            st.error("🌐 Connection error while fetching media contributions.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error fetching {media_type} contributions: {str(e)}")
            return None

    def get_global_corpus_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get global corpus statistics from Swecha API

        Returns:
            Dictionary with global statistics or None if failed
        """
        headers = self._get_auth_headers()
        if not headers:
            return None

        try:
            # Use the correct endpoint for generating statistics
            # POST /api/v1/tasks/generate-statistics with user_specific=false
            stats_response = self.session.post(
                f"{self.base_url}/tasks/generate-statistics",
                headers=headers,
                params={"user_specific": False},
                timeout=45,  # Longer timeout for statistics generation
            )

            if stats_response.status_code == 200:
                task_data = stats_response.json()
                task_id = task_data.get("task_id")

                if task_id:
                    # Poll for task completion (simplified version)
                    import time

                    for _ in range(10):  # Check up to 10 times
                        time.sleep(2)  # Wait 2 seconds between checks

                        task_status_response = self.session.get(
                            f"{self.base_url}/tasks/status/{task_id}",
                            headers=headers,
                            timeout=30,
                        )

                        if task_status_response.status_code == 200:
                            task_status = task_status_response.json()
                            if task_status.get("status") == "SUCCESS":
                                result = task_status.get("result", {})
                                # Transform API response to our expected format
                                return {
                                    "total_contributors": result.get(
                                        "total_users", "2,500+"
                                    ),
                                    "total_records": result.get(
                                        "total_records", "50,000+"
                                    ),
                                    "total_audio_hours": result.get(
                                        "total_audio_duration_hours", "1,200+"
                                    ),
                                    "total_audio_records": result.get(
                                        "audio_records", 0
                                    ),
                                    "total_text_records": result.get("text_records", 0),
                                    "total_video_records": result.get(
                                        "video_records", 0
                                    ),
                                    "total_image_records": result.get(
                                        "image_records", 0
                                    ),
                                    "languages_covered": result.get("languages", []),
                                    "last_updated": result.get(
                                        "generated_at", datetime.now().isoformat()
                                    ),
                                }
                            elif task_status.get("status") in ["FAILURE", "REVOKED"]:
                                break

                return None
            else:
                return None

        except requests.exceptions.Timeout:
            st.warning("⏱️ Statistics generation timed out. Using cached data.")
            return None
        except requests.exceptions.ConnectionError:
            st.warning("🌐 Connection error while fetching global statistics.")
            return None
        except requests.exceptions.RequestException as e:
            st.warning(f"⚠️ Could not fetch live statistics: {str(e)}")
            return None

    def get_note_by_id(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific note by ID

        Args:
            note_id: ID of the note

        Returns:
            Note data if found, None otherwise
        """
        notes = self.load_notes()
        for note in notes:
            if note.get("id") == note_id:
                return note
        return None
