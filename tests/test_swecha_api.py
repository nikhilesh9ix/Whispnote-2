#!/usr/bin/env python3
"""
Test script for Swecha API endpoint discovery
"""

from src.api.swecha_api import WhispNoteSwechaIntegration

def main():
    print("🔍 Swecha API Endpoint Discovery Test")
    print("=" * 50)

    # Initialize integration
    integration = WhispNoteSwechaIntegration()

    # Get full status
    status = integration.get_integration_status()

    print(f"📡 API Available: {status['api_available']}")
    print(f"🔗 Base URL: {status['base_url']}")
    print(f"📝 API Info: {status['api_info']}")
    print(f"🔐 Authentication Required: {status.get('authentication_required', 'Unknown')}")
    print(f"📤 Contribution Supported: {status.get('contribution_supported', 'Unknown')}")
    print(f"🔄 Integration Active: {status['integration_active']}")

    print("\n📋 Available Endpoints:")
    endpoints = status.get('available_endpoints', [])
    if endpoints:
        for endpoint in endpoints:
            print(f"  ✅ {endpoint}")
    else:
        print("  ❌ No additional endpoints discovered")

    print("\n🧪 Testing Text Contribution (will likely fail - endpoints not ready):")
    test_success = integration.contribute_whispnote_data(
        transcription="ఇది ఒక టెస్ట్ వాక్యం",  # Telugu test sentence
        language_code="te",
        user_consent=True
    )
    print(f"  📤 Test Contribution Result: {'✅ Success' if test_success else '❌ Failed (Expected)'}")

    print("\n" + "=" * 50)
    print("📋 Summary:")
    print(f"  • API is {'accessible' if status['api_available'] else 'not accessible'}")
    print(f"  • Version: {status['api_info'].get('version', 'Unknown')}")
    print(f"  • Ready for contributions: {'Yes' if status.get('contribution_supported') else 'Not yet'}")
    if status.get('authentication_required'):
        print("  • 🔑 Bearer token required (set SWECHA_API_TOKEN environment variable)")

if __name__ == "__main__":
    main()
