#!/usr/bin/env python3
"""
Interactive setup script for secrets management (hybrid approach).

Stores secrets in OS keychain (macOS Keychain / Windows Credential Manager).
Falls back to Azure Key Vault if keyring secrets not found.

Usage:
    python scripts/setup_secrets.py
    
Then enter your API keys when prompted. Secrets will be stored encrypted in:
  - macOS: Keychain.app
  - Windows: Credential Manager
"""

import platform
import sys
import getpass
import json
from pathlib import Path


def get_os_name() -> str:
    """Return friendly OS name."""
    system = platform.system()
    if system == "Darwin":
        return "macOS (Keychain)"
    elif system == "Windows":
        return "Windows (Credential Manager)"
    elif system == "Linux":
        return "Linux (SecretService)"
    else:
        return f"Unknown OS: {system}"


def setup_keyring_secrets():
    """Interactive setup: collect API keys and store in OS keychain."""
    try:
        import keyring
    except ImportError:
        print("❌ ERROR: 'keyring' package not installed")
        print("\n📦 Install it with:")
        print("   pip install keyring")
        sys.exit(1)

    print("\n" + "=" * 70)
    print(f"🔐 SECRETS SETUP - {get_os_name()}")
    print("=" * 70)
    print("\nThis script stores your API keys securely in your OS credential store:")
    print("  • macOS:   Keychain.app")
    print("  • Windows: Credential Manager")
    print("\nSecrets are encrypted and managed by your operating system.")
    print("=" * 70)

    # Service name (used as a category/namespace in credential storage)
    SERVICE_NAME = "content-studio"

    # Collect API keys (with helpful descriptions and optional entries)
    secrets_to_add = {
        "azure-ai-key": {
            "prompt": "Azure AI Foundry API Key",
            "description": "Get from https://ai.azure.com/ → Project Settings → API Keys",
            "optional": False,
        },
        "bing-search-key": {
            "prompt": "Bing Search API Key",
            "description": "Get from Azure Portal → Bing Search Resource → Keys and Endpoint",
            "optional": False,
        },
        "anthropic-api-key": {
            "prompt": "Anthropic API Key (Claude)",
            "description": "Get from https://console.anthropic.com/ → API Keys",
            "optional": True,
        },
        "github-copilot-token": {
            "prompt": "GitHub Copilot Token (for agent mode)",
            "description": "Get from https://github.com/settings/tokens (requires GitHub Enterprise)",
            "optional": True,
        },
        "content-moderator-key": {
            "prompt": "Azure Content Moderator Key (optional)",
            "description": "Get from Azure Portal → Content Moderator Resource → Keys",
            "optional": True,
        },
    }

    secrets_to_store = {}
    skipped = []

    for secret_id, config in secrets_to_add.items():
        print(f"\n📝 {config['prompt']}")
        print(f"   {config['description']}")

        while True:
            value = getpass.getpass(f"   Enter value (or press Enter to skip): ")

            if not value:
                if config["optional"]:
                    print(f"   ⊘ Skipped (optional)")
                    skipped.append(secret_id)
                    break
                else:
                    print(f"   ❌ This key is required. Please enter a value.")
                    continue
            else:
                # Confirm non-empty value
                print(f"   ✓ Stored")
                secrets_to_store[secret_id] = value
                break

    # Store secrets in OS keychain
    print("\n" + "=" * 70)
    print("💾 Storing secrets in OS credential storage...")
    print("=" * 70)

    stored_count = 0
    for secret_id, value in secrets_to_store.items():
        try:
            keyring.set_password(SERVICE_NAME, secret_id, value)
            print(f"✅ Stored: {secret_id}")
            stored_count += 1
        except Exception as e:
            print(f"❌ Failed to store {secret_id}: {e}")
            return False

    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETE")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   • Service: {SERVICE_NAME}")
    print(f"   • Secrets stored: {stored_count}")
    if skipped:
        print(f"   • Skipped (optional): {len(skipped)}")
    print(f"\n🔐 Secrets are encrypted and managed by {get_os_name()}")
    print("\n💡 Your app will automatically load these secrets at startup.")
    print("\n📝 To update a secret later, run this script again.")

    # Optional: Show how to view/manage secrets
    if platform.system() == "Darwin":
        print("\n🔍 To view/manage secrets on macOS:")
        print("   Open: Applications → Utilities → Keychain Access")
        print(f"   Search for: {SERVICE_NAME}")
    elif platform.system() == "Windows":
        print("\n🔍 To view/manage secrets on Windows:")
        print("   Windows key → 'Credential Manager' → Manage generic credentials")
        print(f"   Look for: {SERVICE_NAME}/*")

    return True


def setup_azure_keyvault_fallback():
    """Optional: Setup Azure Key Vault as fallback."""
    print("\n" + "=" * 70)
    print("🔗 OPTIONAL: Setup Azure Key Vault as Fallback (for multi-device sync)")
    print("=" * 70)

    use_keyvault = input(
        "\nDo you want to also setup Azure Key Vault as a fallback? (y/n): "
    ).strip().lower()

    if use_keyvault != "y":
        print("⊘ Skipped Azure Key Vault setup")
        return

    print("\n📝 Azure Key Vault Setup:")
    print("   1. Ensure Azure CLI is installed: https://learn.microsoft.com/cli/azure/")
    print("   2. Login to Azure: az login")
    print("   3. Follow the steps in plan-LOCAL.md sections 1-4 to create Key Vault")
    print("   4. Store your Key Vault name and subscription ID")
    print("\n✓ Once set up, the app will automatically fall back to Key Vault")
    print("  if secrets aren't found in local keyring.")


def main():
    """Main entry point."""
    try:
        # Step 1: Setup keyring (primary)
        success = setup_keyring_secrets()
        if not success:
            print("\n❌ Setup failed. Please try again.")
            sys.exit(1)

        # Step 2: Optional Azure Key Vault fallback
        setup_azure_keyvault_fallback()

        print("\n" + "=" * 70)
        print("🎉 READY TO DEVELOP!")
        print("=" * 70)
        print("\nYou can now run your app:")
        print("  Backend:  uvicorn backend.main:app --reload --port 8000")
        print("  Frontend: streamlit run frontend/app.py")
        print("\nSecrets will be automatically loaded from OS keychain.")

    except KeyboardInterrupt:
        print("\n\n⊘ Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
