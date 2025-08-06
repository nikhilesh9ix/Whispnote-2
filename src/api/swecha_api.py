"""
Swecha Corpus API Integration Module
===================================

This module provides integration with the Swecha Telugu Corpus Collections API
for contributing and accessing Telugu language data.

API Base URL: https://api.corpus.swecha.org/
Documentation: https://api.corpus.swecha.org/docs
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

# Try to import the bearer token from config
try:
    from swecha_config import SWECHA_API_TOKEN
    DEFAULT_TOKEN = SWECHA_API_TOKEN
except ImportError:
    DEFAULT_TOKEN = None

class SwechaAPI:
    """
    Client for interacting with the Swecha Telugu Corpus Collections API
    """
    
    def __init__(self, base_url: str = "https://api.corpus.swecha.org", bearer_token: Optional[str] = None):
        """
        Initialize the Swecha API client
        
        Args:
            base_url: Base URL for the Swecha API
            bearer_token: Optional bearer token for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Set up headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'WhispNote/1.0 (Telugu Voice Notes App)'
        }
        
        # Add bearer token if provided
        if bearer_token:
            headers['Authorization'] = f'Bearer {bearer_token}'
            
        self.session.headers.update(headers)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Track API capabilities
        self._api_capabilities = None
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get basic API information
        
        Returns:
            Dictionary containing API version and info
        """
        try:
            response = self.session.get(f"{self.base_url}/")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to get API info: {e}")
            return {}
    
    def health_check(self) -> bool:
        """
        Check if the API is accessible
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/", timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def discover_endpoints(self) -> Dict[str, Any]:
        """
        Discover available API endpoints and capabilities
        
        Returns:
            Dictionary of available endpoints and their status
        """
        if self._api_capabilities is not None:
            return self._api_capabilities
            
        # Known working endpoints from testing
        working_endpoints = ["/", "/docs", "/health"]
        
        # Endpoints to test for future availability
        potential_endpoints = [
            "/api/v1/texts", "/api/v1/audio", "/api/v1/corpus",
            "/v1/texts", "/v1/contribute", "/contribute", 
            "/text", "/audio", "/upload", "/submit"
        ]
        
        capabilities = {
            "available_endpoints": working_endpoints.copy(),
            "authentication_required": False,
            "contribution_supported": False,
            "tested_endpoints": working_endpoints.copy()
        }
        
        # Test potential endpoints
        for endpoint in potential_endpoints:
            try:
                # Test with GET first
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code not in [404]:
                    capabilities["available_endpoints"].append(endpoint)
                    capabilities["tested_endpoints"].append(endpoint)
                    
                    if any(keyword in endpoint for keyword in ["contribute", "upload", "submit", "text", "audio"]):
                        capabilities["contribution_supported"] = True
                    
                    if response.status_code == 401:
                        capabilities["authentication_required"] = True
                        
                # Test with POST for contribution endpoints
                if any(keyword in endpoint for keyword in ["contribute", "upload", "submit", "text", "audio"]):
                    test_payload = {"text": "test", "language": "te"}
                    post_response = self.session.post(f"{self.base_url}{endpoint}", json=test_payload, timeout=5)
                    if post_response.status_code not in [404, 405]:
                        if endpoint not in capabilities["available_endpoints"]:
                            capabilities["available_endpoints"].append(endpoint)
                        capabilities["contribution_supported"] = True
                        
                        if post_response.status_code == 401:
                            capabilities["authentication_required"] = True
                            
            except requests.RequestException:
                pass
        
        self._api_capabilities = capabilities
        return capabilities
    
    def contribute_text_data(self, 
                           text: str, 
                           language: str = "te", 
                           metadata: Optional[Dict] = None) -> bool:
        """
        Contribute text data to the corpus
        
        Args:
            text: The text content to contribute
            language: Language code (default: 'te' for Telugu)
            metadata: Additional metadata about the text
            
        Returns:
            True if contribution was successful, False otherwise
        """
        # Check if contribution endpoints are available
        capabilities = self.discover_endpoints()
        if not capabilities["contribution_supported"]:
            self.logger.warning("Text contribution not supported by current API version")
            return False
            
        try:
            payload = {
                "text": text,
                "language": language,
                "metadata": metadata or {}
            }
            
            # Try different possible endpoints
            endpoints_to_try = ["/contribute/text", "/contribute", "/upload/text"]
            
            for endpoint in endpoints_to_try:
                if endpoint in capabilities["available_endpoints"]:
                    response = self.session.post(f"{self.base_url}{endpoint}", json=payload)
                    
                    if response.status_code in [200, 201]:
                        self.logger.info(f"Text contribution successful via {endpoint}")
                        return True
                    elif response.status_code == 401:
                        self.logger.error("Authentication required for text contribution")
                        return False
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        self.logger.warning(f"Text contribution failed via {endpoint}: {response.status_code}")
            
            self.logger.warning("No working text contribution endpoint found")
            return False
                
        except requests.RequestException as e:
            self.logger.error(f"Failed to contribute text: {e}")
            return False
    
    def contribute_audio_transcription(self, 
                                     audio_path: str, 
                                     transcription: str,
                                     language: str = "te",
                                     metadata: Optional[Dict] = None) -> bool:
        """
        Contribute audio file with its transcription
        
        Args:
            audio_path: Path to the audio file
            transcription: Text transcription of the audio
            language: Language code (default: 'te' for Telugu)
            metadata: Additional metadata
            
        Returns:
            True if contribution was successful, False otherwise
        """
        try:
            # Prepare metadata
            contribution_metadata = {
                "transcription": transcription,
                "language": language,
                "source": "WhispNote",
                **(metadata or {})
            }
            
            # Prepare files for upload
            files = {}
            if Path(audio_path).exists():
                files['audio'] = open(audio_path, 'rb')
            
            data = {
                "metadata": json.dumps(contribution_metadata)
            }
            
            # Note: This endpoint might not exist - placeholder for when API is documented
            response = self.session.post(
                f"{self.base_url}/contribute/audio-transcription", 
                files=files,
                data=data
            )
            
            # Close file handle
            if 'audio' in files:
                files['audio'].close()
            
            if response.status_code in [200, 201]:
                self.logger.info("Audio-transcription contribution successful")
                return True
            else:
                self.logger.warning(f"Audio-transcription contribution failed: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            self.logger.error(f"Failed to contribute audio-transcription: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during contribution: {e}")
            return False
    
    def get_corpus_stats(self) -> Dict[str, Any]:
        """
        Get corpus statistics
        
        Returns:
            Dictionary containing corpus statistics
        """
        try:
            response = self.session.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Failed to get corpus stats: {e}")
            return {}
    
    def search_corpus(self, 
                     query: str, 
                     language: str = "te", 
                     limit: int = 10) -> List[Dict]:
        """
        Search the corpus for specific content
        
        Args:
            query: Search query
            language: Language to search in
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            params = {
                "q": query,
                "lang": language,
                "limit": limit
            }
            
            response = self.session.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            return response.json().get('results', [])
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to search corpus: {e}")
            return []

class WhispNoteSwechaIntegration:
    """
    Integration class for connecting WhispNote with Swecha API
    """
    
    def __init__(self, bearer_token: Optional[str] = None):
        """
        Initialize the integration
        
        Args:
            bearer_token: Optional bearer token for API authentication
                         If not provided, will try to load from:
                         1. Environment variable SWECHA_API_TOKEN
                         2. Default token from swecha_config.py
        """
        # Try to get bearer token from multiple sources
        if not bearer_token:
            bearer_token = os.getenv('SWECHA_API_TOKEN') or DEFAULT_TOKEN
            
        self.api = SwechaAPI(bearer_token=bearer_token)
        self.logger = logging.getLogger(__name__)
        
        # Check API capabilities on initialization
        self._check_api_status()
    
    def _check_api_status(self):
        """Check API status and log capabilities"""
        try:
            if self.api.health_check():
                capabilities = self.api.discover_endpoints()
                if capabilities["authentication_required"]:
                    self.logger.warning("Swecha API requires authentication - bearer token needed")
                if not capabilities["contribution_supported"]:
                    self.logger.info("Swecha API contribution endpoints not yet available")
                else:
                    self.logger.info("Swecha API contribution endpoints available")
            else:
                self.logger.warning("Swecha API is not accessible")
        except Exception as e:
            self.logger.error(f"Error checking Swecha API status: {e}")
    
    def is_telugu_content(self, text: str) -> bool:
        """
        Simple check to determine if content is Telugu
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be Telugu
        """
        # Simple heuristic: check for Telugu Unicode range
        telugu_chars = 0
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return False
        
        for char in text:
            if '\u0C00' <= char <= '\u0C7F':  # Telugu Unicode block
                telugu_chars += 1
        
        # If more than 50% of alphabetic characters are Telugu, consider it Telugu
        return (telugu_chars / total_chars) > 0.5 if total_chars > 0 else False
    
    def contribute_whispnote_data(self, 
                                 transcription: str,
                                 audio_path: Optional[str] = None,
                                 language_code: str = "te",
                                 user_consent: bool = False) -> bool:
        """
        Contribute WhispNote transcription data to Swecha corpus
        
        Args:
            transcription: The transcribed text
            audio_path: Optional path to audio file
            language_code: Language code from WhispNote
            user_consent: Whether user has given consent for contribution
            
        Returns:
            True if contribution was successful
        """
        if not user_consent:
            self.logger.info("User has not given consent for corpus contribution")
            return False
        
        # Only contribute Telugu content
        if language_code != "te" and not self.is_telugu_content(transcription):
            self.logger.info("Content is not Telugu, skipping corpus contribution")
            return False
        
        # Check API availability
        if not self.api.health_check():
            self.logger.warning("Swecha API is not available")
            return False
        
        # Check if contribution endpoints are available
        capabilities = self.api.discover_endpoints()
        if not capabilities["contribution_supported"]:
            self.logger.info("Swecha API contribution endpoints not yet available - storing locally for future upload")
            # Store locally for future batch upload when API becomes available
            self._store_for_future_upload(transcription, audio_path, language_code)
            return False
        
        metadata = {
            "source_app": "WhispNote",
            "transcription_method": "OpenAI Whisper",
            "contribution_timestamp": "2025-08-06T20:46:12.310Z"
        }
        
        success = False
        
        # Contribute text transcription
        if self.api.contribute_text_data(transcription, "te", metadata):
            success = True
            self.logger.info("Successfully contributed text to Swecha corpus")
        
        # Contribute audio + transcription if audio is available
        if audio_path and Path(audio_path).exists():
            if self.api.contribute_audio_transcription(audio_path, transcription, "te", metadata):
                success = True
                self.logger.info("Successfully contributed audio-transcription to Swecha corpus")
        
        return success
    
    def _store_for_future_upload(self, transcription: str, audio_path: Optional[str], language_code: str):
        """Store data locally for future upload when API becomes available"""
        try:
            # Create a pending uploads directory
            pending_dir = Path("whispnote_data/pending_swecha_uploads")
            pending_dir.mkdir(parents=True, exist_ok=True)
            
            # Store the data
            import datetime
            timestamp = datetime.datetime.now().isoformat()
            filename = f"pending_{timestamp.replace(':', '-')}.json"
            
            data = {
                "transcription": transcription,
                "audio_path": audio_path,
                "language_code": language_code,
                "timestamp": timestamp,
                "status": "pending"
            }
            
            with open(pending_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"Stored data for future Swecha upload: {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to store data for future upload: {e}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get status of the Swecha integration
        
        Returns:
            Dictionary with integration status information
        """
        api_info = self.api.get_api_info()
        api_available = self.api.health_check()
        capabilities = self.api.discover_endpoints() if api_available else {}
        
        return {
            "api_available": api_available,
            "api_info": api_info,
            "base_url": self.api.base_url,
            "integration_active": api_available and bool(api_info),
            "capabilities": capabilities,
            "authentication_required": capabilities.get("authentication_required", False),
            "contribution_supported": capabilities.get("contribution_supported", False),
            "available_endpoints": capabilities.get("available_endpoints", [])
        }

# Example usage
if __name__ == "__main__":
    # Test the API connection
    integration = WhispNoteSwechaIntegration()
    status = integration.get_integration_status()
    
    print("Swecha API Integration Status:")
    print(f"API Available: {status['api_available']}")
    print(f"API Info: {status['api_info']}")
    print(f"Integration Active: {status['integration_active']}")
