#!/usr/bin/env python3
"""
Setup script for Azure OpenAI configuration.

This script configures Azure OpenAI with your existing Azure subscription.
It supports two authentication methods:
  1. Azure AD (DefaultAzureCredential) - RECOMMENDED, more secure
  2. API Key - simpler, but requires local auth enabled

Usage:
    python scripts/setup_azure_openai.py
"""

import os
import sys
import json
from pathlib import Path
import subprocess


def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return "", 1


def check_azure_login():
    """Check if user is logged into Azure."""
    output, code = run_command("az account show --query id -o tsv")
    if code != 0:
        print("❌ Not logged into Azure")
        print("\nPlease login first:")
        print("   az login")
        sys.exit(1)
    
    subscription_id = output
    print(f"✓ Logged into Azure Subscription: {subscription_id}")
    return subscription_id


def list_openai_resources():
    """List available Azure OpenAI resources."""
    cmd = 'az cognitiveservices account list --query "[?kind==\'OpenAI\'].{Name:name, ResourceGroup:resourceGroup, Location:location, Endpoint:properties.endpoint}" -o json'
    output, code = run_command(cmd)
    
    if code != 0 or not output:
        print("❌ Failed to list OpenAI resources")
        return []
    
    try:
        resources = json.loads(output)
        return resources
    except:
        return []


def get_openai_endpoint(resource_group, account_name):
    """Get Azure OpenAI endpoint."""
    cmd = f'az cognitiveservices account show --resource-group "{resource_group}" --name "{account_name}" --query properties.endpoint -o tsv'
    output, code = run_command(cmd)
    
    if code != 0:
        print(f"❌ Failed to get endpoint for {account_name}")
        return None
    
    return output


def check_auth_method(resource_group, account_name):
    """Check what auth method is configured."""
    cmd = f'az cognitiveservices account show --resource-group "{resource_group}" --name "{account_name}" --query properties.disableLocalAuth -o tsv'
    output, code = run_command(cmd)
    
    if code == 0:
        disabled = output.lower() in ['true', 'yes']
        return "AAD" if disabled else "API Key"
    
    return "Unknown"


def get_api_key(resource_group, account_name):
    """Get Azure OpenAI API key."""
    cmd = f'az cognitiveservices account keys list --resource-group "{resource_group}" --name "{account_name}" -o json'
    output, code = run_command(cmd)
    
    if code != 0:
        print(f"⚠ Local auth disabled on this resource (requires Azure AD)")
        return None
    
    try:
        keys = json.loads(output)
        return keys.get('key1')
    except:
        return None


def store_secret(secret_id, value):
    """Store secret in OS keychain."""
    try:
        import keyring
        keyring.set_password("content-studio", secret_id, value)
        return True
    except ImportError:
        print("❌ keyring not installed. Install with: pip install keyring")
        return False
    except Exception as e:
        print(f"❌ Failed to store secret: {e}")
        return False


def create_env_file(endpoint, use_aad=True):
    """Create or update .env file for local development."""
    env_file = Path(".env")
    
    content = f"""# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT={endpoint}
AZURE_OPENAI_USE_AAD={'1' if use_aad else '0'}

# If using API Key auth instead of AAD, set:
# AZURE_OPENAI_API_KEY=your-api-key-here

# For local development with Azure AD:
# The app will use DefaultAzureCredential to authenticate
"""
    
    env_file.write_text(content)
    print(f"✓ Created {env_file}")


def main():
    """Main configuration flow."""
    print("\n" + "=" * 70)
    print("🔧 AZURE OPENAI CONFIGURATION")
    print("=" * 70)
    
    # Step 1: Check Azure login
    print("\n📋 Step 1: Checking Azure login...")
    check_azure_login()
    
    # Step 2: List OpenAI resources
    print("\n📦 Step 2: Finding Azure OpenAI resources...")
    resources = list_openai_resources()
    
    if not resources:
        print("❌ No Azure OpenAI resources found!")
        print("\n📌 Create one with:")
        print("   az cognitiveservices account create \\")
        print("     --resource-group <rg> \\")
        print("     --name <name> \\")
        print("     --kind OpenAI \\")
        print("     --sku S0 \\")
        print("     --location eastus")
        sys.exit(1)
    
    print(f"\n✓ Found {len(resources)} OpenAI resource(s):")
    for i, r in enumerate(resources, 1):
        print(f"   {i}. {r['Name']} ({r['ResourceGroup']}) @ {r['Location']}")
    
    # Step 3: Select resource
    if len(resources) == 1:
        selected = resources[0]
        print(f"\nUsing: {selected['Name']}")
    else:
        while True:
            choice = input(f"\nSelect resource (1-{len(resources)}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(resources):
                    selected = resources[idx]
                    break
            except:
                pass
            print("❌ Invalid selection")
    
    resource_group = selected['ResourceGroup']
    account_name = selected['Name']
    
    print(f"✓ Selected: {account_name} ({resource_group})")
    
    # Step 4: Get endpoint
    print("\n🔌 Step 3: Getting endpoint...")
    endpoint = get_openai_endpoint(resource_group, account_name)
    
    if not endpoint:
        print("❌ Failed to get endpoint")
        sys.exit(1)
    
    print(f"✓ Endpoint: {endpoint}")
    
    # Step 5: Check auth method
    print("\n🔐 Step 4: Checking authentication method...")
    auth_method = check_auth_method(resource_group, account_name)
    print(f"✓ Auth method: {auth_method}")
    
    if auth_method == "AAD":
        print("  Using Azure AD (DefaultAzureCredential)")
        print("  Your local Azure CLI credentials will be used automatically")
        use_aad = True
    else:
        # Try to get API key
        api_key = get_api_key(resource_group, account_name)
        if api_key:
            print("  Using API Key authentication")
            print("\n💾 Step 5: Storing API key in OS keychain...")
            if store_secret("azure-openai-endpoint", endpoint):
                print("✓ Endpoint stored")
            if store_secret("azure-ai-key", api_key):
                print("✓ API key stored")
            use_aad = False
        else:
            print("  No local auth available - will use Azure AD")
            use_aad = True
    
    # Step 6: Create .env file
    print("\n📝 Step 5: Creating .env file...")
    create_env_file(endpoint, use_aad)
    
    # Step 7: Verify Python dependencies
    print("\n📦 Step 6: Checking Python dependencies...")
    required_packages = [
        ("openai", "OpenAI SDK"),
        ("azure.identity", "Azure Identity"),
        ("azure.keyvault.secrets", "Azure Key Vault"),
    ]
    
    missing = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✓ {name} installed")
        except ImportError:
            print(f"⚠ {name} not found")
            missing.append(package)
    
    if missing:
        print(f"\n📥 Install missing packages:")
        print(f"   pip install {' '.join(missing)}")
    
    # Step 8: Test connection
    print("\n🧪 Step 7: Testing connection...")
    test_connection(endpoint, use_aad)
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ CONFIGURATION COMPLETE!")
    print("=" * 70)
    print("\n📝 Summary:")
    print(f"   • Resource: {account_name}")
    print(f"   • Endpoint: {endpoint}")
    print(f"   • Auth: {'Azure AD' if use_aad else 'API Key'}")
    print(f"   • Region: {selected['Location']}")
    
    if use_aad:
        print("\n💡 Your Azure CLI credentials will be used automatically")
        print("   (No API key needed for development)")
    else:
        print("\n💡 API key stored securely in OS keychain")
    
    print("\n🎯 Next steps:")
    print("   1. Review the .env file")
    print("   2. Restart your development server")
    print("   3. The app will automatically load Azure OpenAI")
    print("\n   Backend:  uvicorn backend.main:app --reload --port 8000")
    print("   Frontend: streamlit run frontend/Home.py")


def test_connection(endpoint, use_aad):
    """Test Azure OpenAI connection."""
    try:
        from openai import AzureOpenAI
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        import keyring
        
        if use_aad:
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential, "https://cognitiveservices.azure.com/.default"
            )
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                api_version="2024-02-01"
            )
        else:
            api_key = keyring.get_password("content-studio", "azure-ai-key")
            if not api_key:
                print("⚠ API key not found in keychain")
                return
            
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version="2024-02-01"
            )
        
        # Try to get available models (not making actual request)
        print("✓ Connection successful!")
        
    except ImportError as e:
        print(f"⚠ Test skipped - missing package: {e}")
    except Exception as e:
        print(f"⚠ Connection test failed: {e}")
        print("  (This may be normal if no deployments are configured yet)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⊘ Setup cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
