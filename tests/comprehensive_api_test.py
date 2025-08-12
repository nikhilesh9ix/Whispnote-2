#!/usr/bin/env python3
"""
Comprehensive Swecha Corpus API Test Suite
Tests API endpoints, authentication, and functionality
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SwechaAPITester:
    """Comprehensive API testing class for Swecha Corpus API"""

    def __init__(self):
        self.base_url = os.getenv("SWECHA_API_BASE_URL", "https://api.corpus.swecha.org")
        self.token = os.getenv("SWECHA_API_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WhispNote-APITester/2.0.0",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })

        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "has_token": bool(self.token),
            "base_url": self.base_url,
            "endpoints": {},
            "summary": {}
        }

    def test_endpoint(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """Test a specific API endpoint"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=10)
            else:
                return {"error": f"Unsupported method: {method}"}

            result = {
                "url": url,
                "status_code": response.status_code,
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
                "headers": dict(response.headers),
                "success": 200 <= response.status_code < 300
            }

            # Try to parse JSON response
            try:
                result["content"] = response.json()
            except:
                result["content"] = response.text[:500] if response.text else None

            return result

        except requests.exceptions.Timeout:
            return {"error": "Request timeout", "url": url}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error", "url": url}
        except Exception as e:
            return {"error": str(e), "url": url}

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("🔍 Testing Basic API Endpoints")
        print("-" * 50)

        basic_endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/docs", "API Documentation"),
            ("/openapi.json", "OpenAPI specification"),
            ("/redoc", "Alternative docs"),
        ]

        for endpoint, description in basic_endpoints:
            result = self.test_endpoint(endpoint)
            self.test_results["endpoints"][endpoint] = result

            if "error" in result:
                print(f"❌ {endpoint} ({description}): {result['error']}")
            else:
                status_icon = "✅" if result["success"] else "⚠️"
                print(f"{status_icon} {endpoint} ({description}): {result['status_code']} ({result['response_time_ms']}ms)")

                # Show content preview for successful responses
                if result["success"] and result.get("content"):
                    if isinstance(result["content"], dict):
                        if "message" in result["content"]:
                            print(f"   📝 Message: {result['content']['message']}")
                        if "version" in result["content"]:
                            print(f"   🏷️ Version: {result['content']['version']}")

    def test_corpus_endpoints(self):
        """Test corpus-specific endpoints"""
        print("\n🗂️ Testing Corpus Endpoints")
        print("-" * 50)

        corpus_endpoints = [
            ("/stats", "Corpus statistics"),
            ("/contribute", "Contribution endpoint"),
            ("/upload", "File upload endpoint"),
            ("/corpus", "Corpus management"),
            ("/texts", "Text management"),
            ("/audio", "Audio management"),
            ("/api/v1/health", "API v1 health"),
            ("/api/v1/corpus", "API v1 corpus"),
        ]

        for endpoint, description in corpus_endpoints:
            result = self.test_endpoint(endpoint)
            self.test_results["endpoints"][endpoint] = result

            if "error" in result:
                print(f"❌ {endpoint} ({description}): {result['error']}")
            else:
                status_icon = "✅" if result["success"] else "⚠️"
                print(f"{status_icon} {endpoint} ({description}): {result['status_code']} ({result['response_time_ms']}ms)")

    def test_authentication(self):
        """Test authentication requirements"""
        print("\n🔐 Testing Authentication")
        print("-" * 50)

        if not self.token:
            print("⚠️ No API token provided - testing without authentication")
            # Test without token
            no_auth_session = requests.Session()
            no_auth_session.headers.update({
                "User-Agent": "WhispNote-APITester/2.0.0",
                "Accept": "application/json"
            })

            try:
                response = no_auth_session.get(f"{self.base_url}/", timeout=5)
                print(f"📡 Root endpoint without auth: {response.status_code}")
                if response.status_code == 401:
                    print("🔒 Authentication required for API access")
                elif response.status_code == 200:
                    print("🔓 API accessible without authentication")
            except Exception as e:
                print(f"❌ Auth test failed: {e}")
        else:
            print("✅ API token provided - testing with authentication")
            # Decode JWT to show expiration (basic)
            try:
                import base64
                # Simple JWT decode (just for info, not verification)
                parts = self.token.split('.')
                if len(parts) >= 2:
                    payload = base64.b64decode(parts[1] + '==').decode('utf-8')
                    payload_data = json.loads(payload)
                    if 'exp' in payload_data:
                        exp_time = datetime.fromtimestamp(payload_data['exp'])
                        print(f"🕐 Token expires: {exp_time}")
                        if exp_time < datetime.now():
                            print("⚠️ Token appears to be expired!")
            except Exception as e:
                print(f"ℹ️ Could not decode token details: {e}")

    def test_contribution_functionality(self):
        """Test contribution functionality with test data"""
        print("\n📤 Testing Contribution Functionality")
        print("-" * 50)

        test_data = {
            "text": "ఇది ఒక టెస్ట్ వాక్యం తెలుగులో",  # Telugu test sentence
            "language": "te",
            "source": "whispnote_test",
            "user_consent": True,
            "metadata": {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "app_version": "2.0.0"
            }
        }

        # Test different contribution endpoints
        contribution_tests = [
            ("/contribute", "POST", test_data),
            ("/api/v1/contribute", "POST", test_data),
            ("/corpus/contribute", "POST", test_data),
            ("/texts", "POST", test_data),
        ]

        for endpoint, method, data in contribution_tests:
            print(f"\n🧪 Testing {method} {endpoint}")
            result = self.test_endpoint(endpoint, method, data)
            self.test_results["endpoints"][f"{method}_{endpoint}"] = result

            if "error" in result:
                print(f"❌ {endpoint}: {result['error']}")
            else:
                status_icon = "✅" if result["success"] else "⚠️"
                print(f"{status_icon} {endpoint}: {result['status_code']} ({result['response_time_ms']}ms)")

                if result.get("content"):
                    print(f"   📋 Response: {json.dumps(result['content'], indent=2)[:200]}...")

    def test_api_integration(self):
        """Test API integration using WhispNote's integration class"""
        print("\n🔗 Testing WhispNote API Integration")
        print("-" * 50)

        try:
            from src.api.swecha_api import WhispNoteSwechaIntegration

            integration = WhispNoteSwechaIntegration()
            status = integration.get_integration_status()

            print("📡 Integration Status:")
            print(f"   • API Available: {status.get('api_available', 'Unknown')}")
            print(f"   • Base URL: {status.get('base_url', 'Unknown')}")
            print(f"   • Integration Active: {status.get('integration_active', 'Unknown')}")

            if status.get('api_info'):
                info = status['api_info']
                print(f"   • API Version: {info.get('version', 'Unknown')}")
                print(f"   • API Message: {info.get('message', 'Unknown')}")

            # Test actual contribution
            print("\n🧪 Testing Contribution via Integration:")
            contrib_result = integration.contribute_whispnote_data(
                transcription="ఇది విస్ప్‌నోట్ నుండి ఒక టెస్ట్ కంట్రిబ్యూషన్",
                language_code="te",
                user_consent=True
            )
            print(f"   📤 Contribution Result: {'✅ Success' if contrib_result else '❌ Failed'}")

            self.test_results["integration_test"] = {
                "status": status,
                "contribution_success": contrib_result
            }

        except ImportError as e:
            print(f"❌ Could not import WhispNote integration: {e}")
        except Exception as e:
            print(f"❌ Integration test failed: {e}")

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 SWECHA CORPUS API TEST REPORT")
        print("=" * 60)

        # Summary statistics
        total_tests = len(self.test_results["endpoints"])
        successful_tests = sum(1 for result in self.test_results["endpoints"].values()
                             if not result.get("error") and result.get("success", False))

        print("\n📈 Test Summary:")
        print(f"   • Total Endpoints Tested: {total_tests}")
        print(f"   • Successful Responses: {successful_tests}")
        print(f"   • Failed/Error Responses: {total_tests - successful_tests}")
        print(f"   • Success Rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "   • No tests completed")

        # Authentication status
        print("\n🔐 Authentication:")
        print(f"   • Token Provided: {'✅ Yes' if self.test_results['has_token'] else '❌ No'}")

        # Working endpoints
        working_endpoints = [ep for ep, result in self.test_results["endpoints"].items()
                           if not result.get("error") and result.get("success", False)]

        if working_endpoints:
            print(f"\n✅ Working Endpoints ({len(working_endpoints)}):")
            for endpoint in working_endpoints:
                result = self.test_results["endpoints"][endpoint]
                print(f"   • {endpoint} ({result.get('status_code', 'N/A')})")

        # Failed endpoints
        failed_endpoints = [ep for ep, result in self.test_results["endpoints"].items()
                          if result.get("error") or not result.get("success", False)]

        if failed_endpoints:
            print(f"\n❌ Failed Endpoints ({len(failed_endpoints)}):")
            for endpoint in failed_endpoints:
                result = self.test_results["endpoints"][endpoint]
                status = result.get("status_code", result.get("error", "Unknown"))
                print(f"   • {endpoint} ({status})")

        # Recommendations
        print("\n💡 Recommendations:")
        if not self.test_results['has_token']:
            print("   • Set SWECHA_API_TOKEN environment variable for authenticated testing")

        if successful_tests == 0:
            print("   • Check if API server is running and accessible")
            print("   • Verify base URL configuration")
        elif successful_tests < total_tests:
            print("   • Some endpoints may be under development")
            print("   • Check API documentation for endpoint specifications")
        else:
            print("   • API appears to be functioning well!")

        # Save detailed report
        report_file = f"swecha_api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️ Could not save report: {e}")

def main():
    """Main test execution"""
    print("🚀 WhispNote - Swecha Corpus API Test Suite")
    print("=" * 60)
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tester = SwechaAPITester()

    # Run all tests
    tester.test_authentication()
    tester.test_basic_endpoints()
    tester.test_corpus_endpoints()
    tester.test_contribution_functionality()
    tester.test_api_integration()

    # Generate final report
    tester.generate_report()

    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
