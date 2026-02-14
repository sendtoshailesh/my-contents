# Secrets Management Options for Local Laptop Development

**Feature**: Personal AI Content Studio MVP  
**Context**: Local laptop development (macOS and Windows)  
**Goal**: Compare secrets management approaches for securing API keys, LLM credentials, and search API tokens

---

## Executive Summary

For local laptop development, you have **5 primary options**:

| Option | Complexity | Security | Cross-Platform | Cost | Best For |
|--------|-----------|----------|-----------------|------|----------|
| **Azure Key Vault** (current) | Medium | ⭐⭐⭐⭐⭐ | ✅ Full | $0.50/mo | Enterprise-ready, future cloud deployment |
| **Python `keyring`** (OS keychains) | Low | ⭐⭐⭐⭐ | ✅ Full | $0 | Simplest local-first approach |
| **macOS Keychain / Windows Credential Manager** | Low | ⭐⭐⭐⭐ | ⚠️ Separate impl | $0 | Native OS security, OS-idiomatic |
| **Encrypted local files** (fernet-based) | Medium | ⭐⭐⭐ | ✅ Full | $0 | Portable, git-safe, no external deps |
| **HashiCorp Vault** (local) | High | ⭐⭐⭐⭐⭐ | ✅ Full | $0 | Future-proof, enterprise-ready, complex |

---

## Option 1: Azure Key Vault (Current Approach)

### Overview

Store all secrets in Azure Key Vault; fetch at runtime using Azure SDK with local Azure CLI authentication (`az login`).

### Pros

✅ **Enterprise-grade security**: Encryption at rest, access logging, audit trail  
✅ **Future-proof**: Easy to transition to Managed Identity when deploying to cloud  
✅ **Multi-device access**: Same Key Vault accessible from Mac and Windows  
✅ **Role-based access control**: Can share with team members later  
✅ **Compliance-ready**: HIPAA, PCI-DSS, GDPR compliant  
✅ **Zero local file storage**: Secrets never written to disk  
✅ **Audit logging**: Track who accessed which secret and when  

### Cons

❌ **Requires Azure subscription**: Minimal cost ($0.50/month), but still a dependency  
❌ **Network dependency**: Must be online to fetch secrets (no offline mode)  
❌ **Azure CLI dependency**: Must run `az login` before app starts  
❌ **Local credential caching**: Azure SDK caches tokens locally (low security risk)  
❌ **Slightly slower**: API latency for each secret fetch  

### Implementation

**One-time setup**:
```bash
# Create Key Vault (done in plan-LOCAL.md)
az keyvault create --resource-group rg-content-studio --name kv-content-studio-xxxxx

# Store secrets
az keyvault secret set --vault-name kv-content-studio-xxxxx --name azure-ai-key --value "..."
az keyvault secret set --vault-name kv-content-studio-xxxxx --name bing-search-key --value "..."
```

**App startup** (Python):
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()  # Uses local az login session
client = SecretClient(vault_url="https://kv-content-studio-xxxxx.vault.azure.net/", 
                      credential=credential)

# Fetch secrets at runtime
azure_ai_key = client.get_secret("azure-ai-key").value
bing_key = client.get_secret("bing-search-key").value
```

**User experience**: 
1. Run `az login` once per session
2. App automatically fetches secrets from Key Vault
3. No local `.env` files

### Security Assessment

**Threat Model Coverage**:
- ✅ Secrets not in git
- ✅ Secrets not in env vars
- ✅ Secrets encrypted in transit (HTTPS)
- ✅ Secrets encrypted at rest
- ✅ Access audit logged
- ⚠️ Local token cache (low risk; scoped to Azure CLI)
- ⚠️ Network dependency (offline inaccessible)

### Cost

- Azure Key Vault: **$0.50/month** (10,000 operations)
- Azure SDK: Free (open source)
- Total: **< $1/month**

### Recommendation

**✅ Best for**: Personal MVP with cloud deployment planned  
**✅ Best for**: Multi-device Mac/Windows sync  
**✅ Best for**: Future team collaboration  
**❌ Not ideal for**: Offline-only development

---

## Option 2: Python `keyring` Library (OS Keychains)

### Overview

Use the **`keyring`** Python library to abstract over native OS keychains:
- **macOS**: Keychain (system-native)
- **Windows**: Windows Credential Manager (system-native)
- **Linux**: SecretService/pass (if needed)

Secrets stored encrypted in OS credential storage; app reads via Python API.

### Pros

✅ **Zero setup required**: Uses existing OS security  
✅ **Fastest local access**: No network calls; instant credential retrieval  
✅ **Offline support**: Works without internet connection  
✅ **Standard library**: Mature, widely-used Python package  
✅ **Cross-platform**: Same code works Mac/Windows/Linux  
✅ **OS-idiomatic**: Every app on your Mac/Windows can use credentials  
✅ **Intuitive for users**: Add secrets via OS Keychain app (macOS) or Credential Manager (Windows)  
✅ **Zero network dependency**: No Azure subscription required  
✅ **Very low cost**: $0

### Cons

❌ **Less secure than cloud vaults**: Vulnerable to local machine compromise  
❌ **No encryption in transit**: Secrets stored locally (but encrypted at rest)  
❌ **No audit trail**: Can't track who accessed secrets outside the OS  
❌ **No multi-device sync**: Separate credentials for each laptop  
❌ **No role-based access control**: Can't share with team members  
❌ **Local OS dependency**: If OS corrupted, secrets at risk  
❌ **No compliance certifications**: Not HIPAA/PCI-DSS ready (not relevant for personal MVP)  

### Implementation

**Installation**:
```bash
pip install keyring
```

**Store secrets** (one-time, via Python):
```python
import keyring

# Store API keys in OS credential storage
keyring.set_password("content-studio", "azure-ai-key", "sk-xxx...")
keyring.set_password("content-studio", "bing-search-key", "xxx...")
keyring.set_password("content-studio", "anthropic-api-key", "xxx...")
```

**Alternative**: Manual entry via OS UI:
- **macOS**: Open Keychain Access → + button → "Application password"
- **Windows**: Windows Credential Manager → Add generic credential

**Retrieve secrets** (app startup):
```python
import keyring

azure_ai_key = keyring.get_password("content-studio", "azure-ai-key")
bing_key = keyring.get_password("content-studio", "bing-search-key")
anthropic_key = keyring.get_password("content-studio", "anthropic-api-key")

if not azure_ai_key:
    raise ValueError("Secret 'azure-ai-key' not found in system keychain")
```

**User experience**:
1. Run setup script: `python scripts/setup_secrets.py`
2. Enter API keys when prompted
3. Secrets stored in OS keychain automatically
4. App reads from keychain on startup (no manual auth needed)

### Security Assessment

**Threat Model Coverage**:
- ✅ Secrets not in git
- ✅ Secrets not in env vars
- ✅ Secrets encrypted at rest (OS handles)
- ✅ Local OS security (Keychain/Credential Manager)
- ⚠️ No encryption in transit (local machine only)
- ⚠️ No audit trail
- ⚠️ Vulnerable to local machine compromise

**Scenario: What if your laptop is stolen?**
- Azure Key Vault: Attacker can't access secrets (requires Azure login)
- Keyring: Attacker could potentially extract credentials (depends on OS encryption)

### Cost

- $0 (completely free)

### Recommendation

**✅ Best for**: Local-only development (no cloud sync needed)  
**✅ Best for**: Fastest credential access (no network)  
**✅ Best for**: Simplest setup (no Azure subscription)  
**❌ Not ideal for**: Sharing secrets with team members  
**❌ Not ideal for**: Cloud deployment planning  
**❌ Not ideal for**: Compliance/audit requirements  

---

## Option 3: macOS Keychain + Windows Credential Manager (Native)

### Overview

Use **native OS credential storage directly** without abstraction:
- **macOS**: `security` command-line tool + Keychain API
- **Windows**: PowerShell's `Get-StoredCredential` + Credential Manager API

### Pros

✅ **Maximum OS integration**: Deepest integration with OS security  
✅ **Zero third-party deps**: Don't need `keyring` library  
✅ **Very fast local access**: Native binary calls  
✅ **Offline support**: Works without internet  
✅ **Granular OS security**: Can set keychain item permissions  

### Cons

❌ **More complex implementation**: Different code paths for Mac vs. Windows  
❌ **Requires shell/PS commands**: Less Pythonic, more subprocess calls  
❌ **Harder to test**: Mocking OS credential storage is non-trivial  
❌ **Less portable**: Each OS needs specific implementation  
❌ **Steeper learning curve**: Requires understanding Keychain API and Credential Manager API  

### Implementation

**macOS** (using `security` CLI):
```python
import subprocess
import json

def get_secret_macos(service: str, key: str) -> str:
    """Retrieve secret from macOS Keychain."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-a", key, "-w"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        raise ValueError(f"Secret '{key}' not found in Keychain")

# Usage
azure_ai_key = get_secret_macos("content-studio", "azure-ai-key")
```

**Windows** (using PowerShell):
```python
import subprocess

def get_secret_windows(service: str, key: str) -> str:
    """Retrieve secret from Windows Credential Manager."""
    ps_command = f"""
    $cred = Get-StoredCredential -Target {service}
    if ($cred -eq $null) {{ exit 1 }}
    $cred.Password
    """
    result = subprocess.run(
        ["powershell", "-Command", ps_command],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise ValueError(f"Secret '{key}' not found in Credential Manager")
    return result.stdout.strip()

# Usage
azure_ai_key = get_secret_windows("content-studio", "azure-ai-key")
```

**Cross-platform wrapper**:
```python
import platform

def get_secret(service: str, key: str) -> str:
    """Get secret from OS credential storage (Mac or Windows)."""
    if platform.system() == "Darwin":
        return get_secret_macos(service, key)
    elif platform.system() == "Windows":
        return get_secret_windows(service, key)
    else:
        raise RuntimeError(f"Unsupported OS: {platform.system()}")

# Usage (same for both platforms)
azure_ai_key = get_secret("content-studio", "azure-ai-key")
```

### Security Assessment

**Same as Option 2** (Keyring), but with lower-level OS access.

### Cost

- $0 (completely free)

### Recommendation

**⚠️ Not recommended unless**: You want to avoid external dependencies and don't mind platform-specific code  
**⚠️ Use `keyring` (Option 2) instead**: It's simpler, better tested, and more maintainable

---

## Option 4: Encrypted Local Files (Fernet-Based)

### Overview

Store secrets in a **local encrypted YAML/JSON file** using Python's `cryptography` library (Fernet symmetric encryption).

Approach:
1. User provides a **master password** once
2. Master password is hashed to encryption key
3. All secrets encrypted using Fernet and stored in local `.secrets.enc` file
4. App decrypts at runtime using master password (kept in memory)

### Pros

✅ **No OS dependencies**: Works on any OS (Mac, Windows, Linux)  
✅ **No Azure subscription needed**: Completely local and free  
✅ **Portable**: Single `.secrets.enc` file can move between machines  
✅ **Version control safe**: Encrypted file can be committed to git (security via encryption, not absence)  
✅ **Offline support**: Works without internet  
✅ **Flexible**: Can use any encryption algorithm (Fernet is battle-tested)  
✅ **Good for team sharing**: Encrypt with team master password, commit to git  

### Cons

❌ **Master password required at startup**: User must enter password when app starts  
❌ **Master password in memory**: If app compromised, master password exposed  
❌ **File-based vulnerability**: `.secrets.enc` on disk (encrypted but deletable/recoverable)  
❌ **No audit trail**: No logging of secret access  
❌ **No compliance ready**: Not HIPAA/PCI-DSS certified  
❌ **Requires discipline**: Users must secure master password  
❌ **Manual rotation**: Changing master password requires re-encrypting all secrets  

### Implementation

**Installation**:
```bash
pip install cryptography pyyaml
```

**Setup** (one-time; create `scripts/setup_secrets.py`):
```python
from cryptography.fernet import Fernet
import getpass
import uuid
import yaml
import os

def setup_secrets():
    """Interactive setup: user enters API keys and master password."""
    secrets = {}
    
    # Collect API keys
    print("📝 Enter your API keys (stored encrypted locally)")
    secrets['azure_ai_key'] = getpass.getpass("Azure AI Foundry key: ")
    secrets['bing_search_key'] = getpass.getpass("Bing Search API key: ")
    secrets['anthropic_api_key'] = getpass.getpass("Anthropic API key: ")
    secrets['github_copilot_token'] = getpass.getpass("GitHub Copilot token (optional): ")
    
    # Get master password
    master_password = getpass.getpass("\n🔐 Create MASTER PASSWORD (to decrypt secrets): ")
    
    # Derive encryption key from master password (using PBKDF2)
    import hashlib
    import base64
    salt = os.urandom(16)
    key = base64.urlsafe_b64encode(
        hashlib.pbkdf2_hmac('sha256', master_password.encode(), salt, 100000)
    )
    
    # Encrypt secrets
    cipher = Fernet(key)
    encrypted_secrets = {
        k: cipher.encrypt(v.encode()).decode()
        for k, v in secrets.items()
    }
    
    # Store encrypted secrets + salt
    config = {
        'salt': base64.b64encode(salt).decode(),
        'secrets': encrypted_secrets
    }
    
    os.makedirs(os.path.expanduser("~/.content-studio"), exist_ok=True)
    with open(os.path.expanduser("~/.content-studio/.secrets.enc"), 'w') as f:
        yaml.dump(config, f)
    
    print("✅ Secrets stored in ~/.content-studio/.secrets.enc")

if __name__ == "__main__":
    setup_secrets()
```

**Retrieve secrets** (app startup):
```python
import getpass
import yaml
from cryptography.fernet import Fernet
import hashlib
import base64
import os

def load_secrets():
    """Load and decrypt secrets from encrypted file."""
    secrets_file = os.path.expanduser("~/.content-studio/.secrets.enc")
    
    if not os.path.exists(secrets_file):
        raise FileNotFoundError(f"Secrets file not found: {secrets_file}")
    
    # Prompt for master password
    master_password = getpass.getpass("🔐 Enter MASTER PASSWORD to decrypt secrets: ")
    
    # Load encrypted secrets
    with open(secrets_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Derive key from master password + stored salt
    salt = base64.b64decode(config['salt'])
    key = base64.urlsafe_b64encode(
        hashlib.pbkdf2_hmac('sha256', master_password.encode(), salt, 100000)
    )
    
    # Decrypt secrets
    cipher = Fernet(key)
    secrets = {}
    for k, encrypted_v in config['secrets'].items():
        try:
            secrets[k] = cipher.decrypt(encrypted_v.encode()).decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt secret '{k}': {e}")
    
    return secrets

# Usage (at app startup)
secrets = load_secrets()
azure_ai_key = secrets.get('azure_ai_key')
bing_key = secrets.get('bing_search_key')
```

**Git-friendly approach**:
```bash
# Add to .gitignore (master password file)
echo "~/.content-studio/.secrets.enc" >> .gitignore

# But encrypted file can be committed to git (encrypted):
git add ~/.content-studio/.secrets.enc
git commit -m "Add encrypted secrets"
# Anyone cloning needs master password to decrypt
```

### Security Assessment

**Threat Model Coverage**:
- ✅ Secrets not in git (if using `.gitignore`) OR encrypted if in git
- ✅ Secrets encrypted at rest (Fernet 128-bit AES)
- ⚠️ Master password in memory (only during app execution)
- ⚠️ Master password entered at startup (could be shoulder-surfed)
- ⚠️ No audit trail
- ⚠️ Vulnerable to local machine keyloggers (master password)

**Stronger variant** (using environment variable for master password):
```bash
# At startup (shell):
export SECRETS_MASTER_PASSWORD="my-master-password"
python frontend/app.py

# In code:
import os
master_password = os.environ.get('SECRETS_MASTER_PASSWORD')
if not master_password:
    master_password = getpass.getpass("🔐 Enter master password: ")
```

### Cost

- $0 (completely free)
- `cryptography` library: Free (open source)

### Recommendation

**✅ Best for**: Team collaboration (encrypt with team master password, commit to git)  
**✅ Best for**: Portability (copy `.secrets.enc` between machines)  
**✅ Best for**: No external dependencies  
**⚠️ Trade-off**: Requires master password at startup  
**❌ Not ideal for**: Automated deployments (need unattended secret access)  

---

## Option 5: HashiCorp Vault (Local)

### Overview

**HashiCorp Vault** is an enterprise-grade secrets management system. Run a local Vault server; app authenticates and retrieves secrets.

Vault features:
- Dynamic secrets generation (rotate secrets automatically)
- Encrypted secrets storage
- Detailed audit logging
- Role-based access control
- API-based secret management
- Can run locally or in cloud

### Pros

✅ **Enterprise-ready**: Used by large organizations (banks, tech companies)  
✅ **Dynamic secrets**: Auto-rotate credentials (e.g., database passwords)  
✅ **Detailed audit logs**: Track every secret access  
✅ **Role-based access**: Define who can access which secrets  
✅ **Flexible authentication**: Multiple auth methods (password, GitHub, Kubernetes, etc.)  
✅ **API-driven**: Excellent for automation  
✅ **Open source**: Free to use and self-hosted  
✅ **Future-proof**: If scaling beyond personal use, Vault is already there  

### Cons

❌ **Complex setup**: Requires running a Vault server locally (Docker or binary)  
❌ **Steeper learning curve**: Vault concepts (auth methods, policies, engines) are complex  
❌ **Overkill for MVP**: More infrastructure than needed for personal laptop  
❌ **Local server overhead**: Consumes resources (memory, port)  
❌ **Configuration heavy**: Startup scripts, initialization, unsealing  
❌ **Not truly "local"**: While Vault runs locally, it's a service to manage  

### Implementation

**Installation** (macOS):
```bash
# Via Homebrew
brew install hashicorp/tap/vault

# Or download binary
curl https://releases.hashicorp.com/vault/1.16.0/vault_1.16.0_darwin_amd64.zip \
  -o vault.zip && unzip vault.zip
```

**Start Vault server**:
```bash
# Development mode (unsealed, in-memory storage - not for production)
vault server -dev

# Output will show root token and API endpoint
# Example: Root Token: hvs.xxxxx
#          API URL: http://127.0.0.1:8200
```

**Store secrets**:
```bash
export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="hvs.xxxxx"  # From server output

# Store secrets via CLI
vault kv put secret/content-studio \
  azure_ai_key="sk-xxx..." \
  bing_search_key="xxx..." \
  anthropic_api_key="xxx..."
```

**Retrieve secrets** (Python app):
```python
import hvac

def get_vault_client() -> hvac.Client:
    """Connect to local Vault server."""
    client = hvac.Client(url='http://127.0.0.1:8200')
    # For dev mode, use root token (not secure; for dev only)
    client.token = os.environ.get('VAULT_TOKEN')
    return client

def load_secrets():
    """Fetch secrets from Vault."""
    client = get_vault_client()
    secrets = client.secrets.kv.v2.read_secret_version(path='content-studio')
    return secrets['data']['data']

# Usage
azure_ai_key = load_secrets()['azure_ai_key']
```

**Production setup** (with authentication):
```bash
# Initialize Vault
vault operator init

# Unseal Vault
vault operator unseal

# Create JWT or GitHub auth
vault auth enable github
vault write auth/github/config organization=my-org
```

### Security Assessment

**Threat Model Coverage**:
- ✅ Secrets encrypted at rest
- ✅ Detailed audit logs
- ✅ Role-based access control
- ✅ API authentication
- ⚠️ Local server running (consumes resources)
- ⚠️ Unsealing required (manual or automated)

### Cost

- $0 (open source, self-hosted)
- Infrastructure: Minimal (just a local process)

### Recommendation

**❌ Not recommended for MVP**: Too complex for personal laptop use  
**✅ Consider for**: Future team collaboration or self-hosted infrastructure  
**✅ Consider for**: Learning secrets management best practices  
**🎯 Better choice**: Start with `keyring` (Option 2) or Azure Key Vault, migrate to Vault later if needed

---

## Comparison Matrix

| Feature | Azure KV | `keyring` | Native OS | Encrypted Files | Vault |
|---------|----------|----------|-----------|-----------------|-------|
| **Setup complexity** | Medium | Very Low | Low | Medium | High |
| **Local access speed** | Slow (network) | Fast | Fast | Fast | Medium |
| **Offline support** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Yes (if unsealed) |
| **Multi-device sync** | ✅ Yes | ❌ No | ❌ No | ⚠️ Manual | ⚠️ If cloud hosted |
| **Audit logs** | ✅ Yes | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Compliance ready** | ✅ Yes | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Cost** | $0.50/mo | $0 | $0 | $0 | $0 |
| **Team sharing** | ✅ Easy | ❌ Hard | ❌ Hard | ✅ Easy (encrypt) | ✅ Easy |
| **Cloud deployment** | ✅ Seamless | ⚠️ Refactor | ⚠️ Refactor | ⚠️ Refactor | ✅ Easy |

---

## Recommendation Summary

### For Personal MVP (Local Laptop Only)

**🥇 Best Option: Python `keyring` (Option 2)**

**Why?**
- ✅ Simplest setup (one `pip install`)
- ✅ Zero configuration
- ✅ Fastest local access
- ✅ Uses native OS security
- ✅ Works offline
- ✅ Completely free
- ✅ Cross-platform (Mac/Windows)

**When to use**: Personal MVP, single user, local development only

**Setup time**: 5 minutes (install `keyring`, run setup script)

```bash
pip install keyring
python scripts/setup_secrets.py
# Enter API keys, done!

# App automatically reads from OS keychain
```

---

### For Planning Ahead (Future Team Collaboration)

**🥈 Current Choice: Azure Key Vault (Option 1)**

**Why?**
- ✅ Already set up in your MVP plan
- ✅ Multi-device access (Mac and Windows same secrets)
- ✅ Future-proof (Managed Identity for cloud deployment)
- ✅ Team collaboration ready (RBAC)
- ✅ Compliance certifications
- ✅ Enterprise-grade

**When to use**: Personal MVP with plans to deploy to cloud or share with team

**Setup time**: 10 minutes (Azure CLI config + Key Vault creation)

---

### For Maximum Portability (Git-Safe Secrets)

**🥉 Encrypted Files (Option 4)**

**Why?**
- ✅ Encrypt with team master password, commit to git
- ✅ Portable between machines
- ✅ Zero external dependencies
- ✅ Good for open-source projects

**When to use**: When sharing encrypted secrets with team via git

**Setup time**: 15 minutes (create encryption setup script)

---

## Hybrid Recommendation

**Best approach for your MVP**:

1. **Primary (Local Dev)**: Use `keyring` (Option 2)
   - Simplest, fastest, zero friction
   - Stored in native OS security
   - Perfect for daily development

2. **Fallback (Cloud Services)**: Keep Azure Key Vault
   - For storing secrets that need cloud access authorization
   - For future Managed Identity deployment
   - For multi-device sync if developing on multiple machines

**Example architecture**:
```python
import keyring
from azure.keyvault.secrets import SecretClient

# Try to load from OS keyring first (local development)
azure_ai_key = keyring.get_password("content-studio", "azure-ai-key")

# If not found, try Azure Key Vault (cloud/team setup)
if not azure_ai_key:
    try:
        client = SecretClient(...)
        azure_ai_key = client.get_secret("azure-ai-key").value
    except Exception:
        raise ValueError("Secrets not found in keyring or Key Vault")
```

This provides:
- ✅ Fast local development (keyring)
- ✅ Cloud deployment option (Key Vault)
- ✅ Flexibility (choose at runtime)

---

## Implementation Roadmap

### Phase 1: MVP (Personal Laptop)
- [ ] Use Python `keyring` (Option 2)
- [ ] Setup script: `scripts/setup_secrets.py`
- [ ] Retrieval code: `services/secrets_service.py`
- [ ] Documentation: How to add/update secrets locally

### Phase 2: Multi-Device / Team Prep
- [ ] Add Azure Key Vault as fallback
- [ ] Implement hybrid approach (try keyring first, fall back to Key Vault)
- [ ] Document both flows

### Phase 3: Team Collaboration (Future)
- [ ] Migrate to encrypted files (Option 4) for git-safe sharing
- [ ] Or: Upgrade to Azure Key Vault for full team RBAC
- [ ] Or: Deploy HashiCorp Vault for enterprise features

---

## Next Steps

**If you want to proceed with `keyring`**:
1. I can create `scripts/setup_secrets.py` (interactive setup)
2. I can create `services/secrets_service.py` (retrieval wrapper)
3. You'll have local secrets in OS keychain, zero friction

**If you want to stick with Azure Key Vault**:
1. Follow plan-LOCAL.md setup steps (already provided)
2. Same app code, just cloud-hosted secrets

**If you want hybrid approach**:
1. I can create code that tries `keyring` first, falls back to Azure KV
2. Best of both worlds: fast local dev + cloud backup

---

## References

- **Python keyring**: https://github.com/jaraco/keyring
- **Cryptography (Fernet)**: https://cryptography.io/en/latest/fernet/
- **HashiCorp Vault**: https://www.vaultproject.io/
- **Azure Key Vault**: https://learn.microsoft.com/en-us/azure/key-vault/
