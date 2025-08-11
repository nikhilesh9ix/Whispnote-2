# Swecha API Configuration Template
# This file provides a secure template for API configuration

import os
from typing import Optional

class SwechaConfig:
    """Secure configuration management for Swecha API"""
    
    @staticmethod
    def get_api_token() -> Optional[str]:
        """Get API token from environment variables"""
        return os.getenv("SWECHA_API_TOKEN")
    
    @staticmethod
    def get_base_url() -> str:
        """Get base URL for Swecha API"""
        return os.getenv("SWECHA_API_BASE_URL", "https://api.corpus.swecha.org")
    
    @staticmethod
    def is_configured() -> bool:
        """Check if API is properly configured"""
        return SwechaConfig.get_api_token() is not None
    
    @staticmethod
    def get_headers() -> dict:
        """Get headers for API requests"""
        token = SwechaConfig.get_api_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

# Backward compatibility
SWECHA_API_TOKEN = SwechaConfig.get_api_token()
SWECHA_API_BASE_URL = SwechaConfig.get_base_url()
TOKEN_TYPE = "bearer"
