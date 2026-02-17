#!/usr/bin/env python3
"""
Setup demo/test secrets for development and testing.

This script configures demo API keys securely in OS keychain
without requiring you to have real API keys.

For production, you would:
  1. Get real API keys from Azure Portal
  2. Run: python scripts/setup_secrets.py
  3. Enter your actual keys

Usage:
    python scripts/setup_demo_secrets.py

This will set up demo keys in your OS keychain for testing.
"""

import platform
import sys
import logging


def setup_demo_keyring_secrets():
    """Setup demo secrets in OS keychain for testing."""
    try:
        import keyring
    except ImportError:
        print("❌ ERROR: 'keyring' package not installed")
        print("\n📦 Install it with:")
        print("   pip install keyring")
        sys.exit(1)

    SERVICE_NAME = "content-studio"

    # Demo/test secrets (these are fake keys for testing only)
    # In production, you would use real API keys from Azure Portal
    demo_secrets = {
        "azure-ai-key": {
            "value": "demo-azure-openai-key-6290f2e7-test",
            "description": "Demo Azure OpenAI API Key",
            "type": "CRITICAL - Replace with real Azure OpenAI key from Azure Portal",
        },
        "bing-search-key": {
            "value": "demo-bing-search-key-a1b2c3d4e5f6-test",
            "description": "Demo Bing Search API Key",
            "type": "CRITICAL - Replace with real Bing Search key from Azure Portal",
        },
        "anthropic-api-key": {
            "value": "demo-anthropic-key-sk-ant-test-123456",
            "description": "Demo Anthropic (Claude) API Key",
            "type": "OPTIONAL - Get from https://console.anthropic.com",
        },
    }

    print("\n" + "=" * 70)
    print("📝 DEMO SECRETS SETUP")
    print("=" * 70)
    print("\n⚠️  WARNING: Setting up DEMO keys for testing purposes only!")
    print("\nFor production use:")
    print("  1. Get REAL API keys from Azure Portal")
    print("  2. Run: python scripts/setup_secrets.py")
    print("  3. Enter your actual keys")
    print("\n" + "=" * 70)

    print(f"\nService: {SERVICE_NAME}")
    print("Storing in OS credential storage...\n")

    stored_count = 0
    for secret_id, config in demo_secrets.items():
        try:
            keyring.set_password(SERVICE_NAME, secret_id, config["value"])
            print(
                f"✅ {config['description']:<50} Stored in keychain"
            )
            stored_count += 1
        except Exception as e:
            print(f"❌ Failed to store '{secret_id}': {e}")

    print("\n" + "=" * 70)
    print("✅ DEMO SETUP COMPLETE")
    print("=" * 70)

    print(f"\n📊 Summary:")
    print(f"   Service: {SERVICE_NAME}")
    print(f"   Secrets stored: {stored_count}")
    print(f"   Keys configured: {', '.join(demo_secrets.keys())}")

    print("\n⚠️  Important Reminders:")
    print("   1. These are DEMO keys - won't work with real APIs")
    print("   2. System will use MOCK fallback with these keys")
    print("   3. Tests will show: API Type = 'Mock Fallback'")
    print("   4. For REAL functionality:")
    print("      - Get API keys from Azure Portal")
    print("      - Run: python scripts/setup_secrets.py")
    print("      - Enter your REAL keys")

    print("\n🔐 To view/manage secrets on macOS:")
    print("   Open: Applications → Utilities → Keychain Access")
    print(f"   Search for: {SERVICE_NAME}")

    print("\n" + "=" * 70)
    print("🧪 NEXT STEPS FOR TESTING:")
    print("=" * 70)
    print("\n1. Validate configuration:")
    print("   python3 run_tests.py --validate-only")
    print("\n2. Run E2E tests (will show mock fallback with demo keys):")
    print("   python3 run_tests.py --e2e-only")
    print("\n3. Start backend for manual testing:")
    print("   uvicorn backend.main:app --reload --port 8000")
    print("\n" + "=" * 70)
    print("\n✅ Demo secrets setup complete! Ready for testing...")
    print("\nTo use REAL API keys, follow the instructions in:")
    print("   scripts/setup_secrets.py (interactive mode)")
    print("=" * 70)


if __name__ == "__main__":
    setup_demo_keyring_secrets()
