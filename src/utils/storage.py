# storage.py
import datetime
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

# Import Swecha API integration
try:
    from src.api.swecha_api import WhispNoteSwechaIntegration

    SWECHA_AVAILABLE = True
except ImportError:
    SWECHA_AVAILABLE = False
    # Note: Warning is handled in the UI when needed


class StorageManager:
    def __init__(self, base_dir: str = "whispnote_data"):
        """
        Initialize storage manager

        Args:
            base_dir: Base directory for storing data
        """
        self.base_dir = Path(base_dir)
        self.notes_dir = self.base_dir / "notes"
        self.corpus_dir = self.base_dir / "corpus"
        self.audio_dir = self.base_dir / "audio"
        self.config_file = self.base_dir / "config.json"

        # Initialize Swecha API integration
        self.swecha_integration = None
        if SWECHA_AVAILABLE:
            try:
                self.swecha_integration = WhispNoteSwechaIntegration()
            except Exception as e:
                st.warning(f"Could not initialize Swecha integration: {e}")

        # Create directories if they don't exist
        self._initialize_directories()

    def _initialize_directories(self):
        """Create necessary directories"""
        try:
            self.base_dir.mkdir(exist_ok=True)
            self.notes_dir.mkdir(exist_ok=True)
            self.corpus_dir.mkdir(exist_ok=True)
            self.audio_dir.mkdir(exist_ok=True)

            # Initialize config file
            if not self.config_file.exists():
                default_config = {
                    "version": "1.0",
                    "created": datetime.datetime.now().isoformat(),
                    "total_notes": 0,
                    "total_contributions": 0,
                }
                self._save_json(self.config_file, default_config)

        except Exception as e:
            st.error(f"Failed to initialize storage directories: {str(e)}")

    def save_note(self, note_data: Dict) -> bool:
        """
        Save a note to storage

        Args:
            note_data: Dictionary containing note information

        Returns:
            True if successful, False otherwise
        """
        try:
            note_id = note_data.get("id")
            if not note_id:
                st.error("Note ID is required")
                return False

            # Save note data
            note_file = self.notes_dir / f"{note_id}.json"
            self._save_json(note_file, note_data)

            # Update config
            self._update_config({"total_notes": len(self.load_notes())})

            return True

        except Exception as e:
            st.error(f"Failed to save note: {str(e)}")
            return False

    def load_notes(self) -> List[Dict]:
        """
        Load all notes from storage

        Returns:
            List of note dictionaries
        """
        try:
            notes = []

            if not self.notes_dir.exists():
                return notes

            for note_file in self.notes_dir.glob("*.json"):
                try:
                    note_data = self._load_json(note_file)
                    if note_data:
                        notes.append(note_data)
                except Exception as e:
                    st.warning(f"Failed to load note {note_file.name}: {str(e)}")

            # Sort by timestamp (newest first)
            notes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return notes

        except Exception as e:
            st.error(f"Failed to load notes: {str(e)}")
            return []

    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note from storage

        Args:
            note_id: ID of note to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            note_file = self.notes_dir / f"{note_id}.json"

            if note_file.exists():
                note_file.unlink()

                # Update config
                self._update_config({"total_notes": len(self.load_notes())})
                return True
            else:
                st.warning(f"Note {note_id} not found")
                return False

        except Exception as e:
            st.error(f"Failed to delete note: {str(e)}")
            return False

    def update_note(self, note_data: Dict) -> bool:
        """
        Update an existing note

        Args:
            note_data: Updated note data

        Returns:
            True if successful, False otherwise
        """
        try:
            note_id = note_data.get("id")
            if not note_id:
                st.error("Note ID is required for update")
                return False

            # Update timestamp
            note_data["updated"] = datetime.datetime.now().isoformat()

            return self.save_note(note_data)

        except Exception as e:
            st.error(f"Failed to update note: {str(e)}")
            return False

    def contribute_to_corpus(
        self, audio_path: str, transcription: str, language_code: str
    ) -> bool:
        """
        Contribute audio and transcription to corpus (with user consent)

        Args:
            audio_path: Path to audio file
            transcription: Transcribed text
            language_code: Language code

        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            contribution_id = f"{language_code}_{timestamp}"

            # Local corpus storage (existing functionality)
            # Copy audio file to corpus
            corpus_audio_path = self.corpus_dir / f"{contribution_id}.wav"
            if os.path.exists(audio_path):
                shutil.copy2(audio_path, corpus_audio_path)

            # Save transcription and metadata
            corpus_data = {
                "id": contribution_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "language_code": language_code,
                "transcription": transcription,
                "audio_file": f"{contribution_id}.wav",
                "duration": self._get_audio_duration(corpus_audio_path)
                if corpus_audio_path.exists()
                else 0,
                "anonymized": True,
            }

            corpus_meta_file = self.corpus_dir / f"{contribution_id}.json"
            self._save_json(corpus_meta_file, corpus_data)

            # Update corpus statistics
            self._update_corpus_stats()

            # Contribute to Swecha API (if available and Telugu content)
            swecha_success = False
            if self.swecha_integration and SWECHA_AVAILABLE:
                try:
                    swecha_success = self.swecha_integration.contribute_whispnote_data(
                        transcription=transcription,
                        audio_path=audio_path,
                        language_code=language_code,
                        user_consent=True,  # User already gave consent in the main app
                    )

                    if swecha_success:
                        # Update config to track Swecha contributions
                        config = self._load_config()
                        config["swecha_contributions"] = (
                            config.get("swecha_contributions", 0) + 1
                        )
                        config["last_swecha_contribution"] = (
                            datetime.datetime.now().isoformat()
                        )
                        self._save_json(self.config_file, config)

                        st.success("🌟 Data contributed to Swecha Telugu Corpus!")

                except Exception as e:
                    st.warning(f"Could not contribute to Swecha corpus: {e}")

            return True

        except Exception as e:
            st.error(f"Failed to contribute to corpus: {str(e)}")
            return False

    def get_corpus_stats(self) -> Dict:
        """
        Get corpus contribution statistics

        Returns:
            Dictionary with corpus statistics
        """
        try:
            stats = {
                "total_contributions": 0,
                "languages_used": {},
                "total_duration": 0.0,
                "total_transcription_length": 0,
            }

            if not self.corpus_dir.exists():
                return stats

            for meta_file in self.corpus_dir.glob("*.json"):
                try:
                    corpus_data = self._load_json(meta_file)
                    if corpus_data:
                        stats["total_contributions"] += 1

                        lang = corpus_data.get("language_code", "unknown")
                        stats["languages_used"][lang] = (
                            stats["languages_used"].get(lang, 0) + 1
                        )

                        stats["total_duration"] += corpus_data.get("duration", 0)
                        stats["total_transcription_length"] += len(
                            corpus_data.get("transcription", "")
                        )

                except Exception as e:
                    st.warning(
                        f"Failed to process corpus file {meta_file.name}: {str(e)}"
                    )

            # Convert duration to minutes
            stats["total_duration"] = stats["total_duration"] / 60.0

            return stats

        except Exception as e:
            st.error(f"Failed to get corpus stats: {str(e)}")
            return {}

    def export_corpus_data(self, output_path: str, format: str = "json") -> bool:
        """
        Export corpus data for research purposes

        Args:
            output_path: Path to save exported data
            format: Export format ('json', 'csv')

        Returns:
            True if successful, False otherwise
        """
        try:
            corpus_data = []

            for meta_file in self.corpus_dir.glob("*.json"):
                try:
                    data = self._load_json(meta_file)
                    if data:
                        # Remove sensitive information
                        export_data = {
                            "id": data.get("id"),
                            "language_code": data.get("language_code"),
                            "transcription": data.get("transcription"),
                            "duration": data.get("duration"),
                            "timestamp": data.get("timestamp"),
                        }
                        corpus_data.append(export_data)
                except Exception:
                    continue

            if format == "json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(corpus_data, f, ensure_ascii=False, indent=2)
            elif format == "csv":
                import pandas as pd

                df = pd.DataFrame(corpus_data)
                df.to_csv(output_path, index=False, encoding="utf-8")

            return True

        except Exception as e:
            st.error(f"Failed to export corpus data: {str(e)}")
            return False

    def _save_json(self, file_path: Path, data: Dict):
        """Save data as JSON file"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_json(self, file_path: Path) -> Optional[Dict]:
        """Load data from JSON file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _load_config(self) -> Dict:
        """Load configuration data"""
        return self._load_json(self.config_file) or {}

    def _update_config(self, updates: Dict):
        """Update configuration file"""
        try:
            config = self._load_json(self.config_file) or {}
            config.update(updates)
            config["last_updated"] = datetime.datetime.now().isoformat()
            self._save_json(self.config_file, config)
        except Exception as e:
            st.warning(f"Failed to update config: {str(e)}")

    def _update_corpus_stats(self):
        """Update corpus statistics in config"""
        try:
            stats = self.get_corpus_stats()
            self._update_config(
                {
                    "total_contributions": stats.get("total_contributions", 0),
                    "corpus_languages": list(stats.get("languages_used", {}).keys()),
                    "corpus_total_duration": stats.get("total_duration", 0),
                }
            )
        except Exception as e:
            st.warning(f"Failed to update corpus stats: {str(e)}")

    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds"""
        try:
            # This is a placeholder - you might want to use librosa or pydub
            # for actual audio duration calculation
            if audio_path.exists():
                file_size = audio_path.stat().st_size
                # Rough estimate: assume 16kHz, 16-bit audio
                estimated_duration = file_size / (16000 * 2)  # seconds
                return min(estimated_duration, 600)  # Cap at 10 minutes
            return 0
        except Exception:
            return 0

    def get_swecha_status(self) -> Dict:
        """
        Get Swecha API integration status

        Returns:
            Dictionary containing Swecha integration information
        """
        if not SWECHA_AVAILABLE or not self.swecha_integration:
            return {"available": False, "reason": "Swecha integration not available"}

        try:
            status = self.swecha_integration.get_integration_status()
            config = self._load_config()

            return {
                "available": True,
                "api_status": status,
                "contributions_count": config.get("swecha_contributions", 0),
                "last_contribution": config.get("last_swecha_contribution", "Never"),
            }
        except Exception as e:
            return {"available": False, "reason": f"Error getting status: {e}"}

    def cleanup_old_files(self, days_old: int = 30):
        """Clean up old temporary files"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)

            for temp_file in self.base_dir.glob("temp_*"):
                try:
                    if temp_file.stat().st_mtime < cutoff_date.timestamp():
                        temp_file.unlink()
                except Exception:
                    pass

        except Exception as e:
            st.warning(f"Cleanup failed: {str(e)}")

    def get_storage_info(self) -> Dict:
        """Get storage information"""
        try:
            total_size = 0
            file_counts = {}

            for path in self.base_dir.rglob("*"):
                if path.is_file():
                    total_size += path.stat().st_size
                    suffix = path.suffix or "no_extension"
                    file_counts[suffix] = file_counts.get(suffix, 0) + 1

            return {
                "total_size_mb": total_size / (1024 * 1024),
                "file_counts": file_counts,
                "directories": {
                    "notes": len(list(self.notes_dir.glob("*.json"))),
                    "corpus": len(list(self.corpus_dir.glob("*.json"))),
                    "audio": len(list(self.audio_dir.glob("*"))),
                },
            }

        except Exception as e:
            st.error(f"Failed to get storage info: {str(e)}")
            return {}
