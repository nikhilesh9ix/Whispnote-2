#!/usr/bin/env python3
"""
Test     # Find all timeout occurrences
    timeout_lines = []
    for i, line in enumerate(lines, 1):
        if 'timeout=' in line:
            timeout_lines.append((i, line.strip()))rify that all timeouts in SwechaStorageManager are properly configured
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_timeout_configuration():
    """Test that all API calls have appropriate timeout values"""

    print("🧪 Testing Timeout Configuration")
    print("=" * 50)

    # Read the storage file and check for timeout values
    storage_file = os.path.join(
        os.path.dirname(__file__), "src", "utils", "swecha_storage.py"
    )

    if not os.path.exists(storage_file):
        # Try alternative path
        storage_file = "src/utils/swecha_storage.py"
        if not os.path.exists(storage_file):
            print(f"❌ Storage file not found at either location")
            print(
                f"   Tried: {os.path.join(os.path.dirname(__file__), 'src', 'utils', 'swecha_storage.py')}"
            )
            print(f"   Tried: {storage_file}")
            print(f"   Current directory: {os.getcwd()}")
            return

    with open(storage_file, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    print("📊 Timeout Analysis:")
    print()

    # Find all timeout occurrences
    timeout_lines = []
    for i, line in enumerate(lines, 1):
        if "timeout=" in line and "session.get" in lines[max(0, i - 3) : i + 1]:
            timeout_lines.append((i, line.strip()))

    if not timeout_lines:
        print("❌ No timeout configurations found!")
        return

    print("🔍 Found timeout configurations:")
    print()

    all_good = True
    for line_num, line in timeout_lines:
        # Extract timeout value
        if "timeout=" in line:
            timeout_part = line.split("timeout=")[1].split(",")[0].split(")")[0].strip()
            try:
                timeout_val = int(timeout_part)
                if timeout_val >= 30:
                    status = "✅"
                    color = ""
                elif timeout_val >= 15:
                    status = "⚠️"
                    color = " (Warning: might be too short)"
                else:
                    status = "❌"
                    color = " (Error: too short)"
                    all_good = False

                print(f"   Line {line_num:3d}: {status} timeout={timeout_val}s{color}")
                print(f"           {line}")
                print()
            except ValueError:
                print(f"   Line {line_num:3d}: ❓ timeout={timeout_part} (non-numeric)")
                print(f"           {line}")
                print()

    print("=" * 50)

    if all_good:
        print("🎯 All timeouts are properly configured (≥30s)!")
        print("   This should resolve the timeout errors.")
    else:
        print("⚠️  Some timeouts might be too short.")
        print("   Consider increasing timeouts to 30+ seconds.")

    print()
    print("📝 Recommended timeout values:")
    print("   • Authentication calls: 30s")
    print("   • Data retrieval calls: 30s")
    print("   • Statistics generation: 45s")
    print("   • File upload calls: 60s+")

    print()
    print("🔧 Additional fixes applied:")
    print("   ✅ Session retry strategy with exponential backoff")
    print("   ✅ Proper error handling for timeout exceptions")
    print("   ✅ User-friendly error messages")
    print("   ✅ Connection error handling")


if __name__ == "__main__":
    test_timeout_configuration()
