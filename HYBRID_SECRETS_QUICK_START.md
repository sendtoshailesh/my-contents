# Hybrid Secrets Management - Quick Reference

**Setup Time**: 10-15 minutes | **Complexity**: Very Low | **Cost**: $0 + LLM APIs

---

## What Is Hybrid Approach?

**Primary (Local, Fast)**: OS keychain via Python `keyring` library
- Secrets stored encrypted in** **macOS Keychain or Windows Credential Manager
- Instant access (no network calls)
- Works offline
- $0 cost

**Fallback (Cloud, Optional)**: Azure Key Vault
- For multi-device sync (same secrets on Mac and Windows)
- For cloud deployment preparation
- Optional; only used if secret not found locally
- $0.50/month

---

## Setup Flow (5 Steps, 10 minutes)

### 1️⃣ Clone & Install (2 min)

```bash
git clone https://github.com/yourusername/content-studio.git
cd content-studio
python3.11 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
```

### 2️⃣ Interactive Secrets Setup (3 min)

```bash
python scripts/setup_secrets.py

# You'll be prompted for:
# ✓ Azure AI Foundry API Key (required)
# ✓ Bing Search API Key (required)
# ○ Anthropic API Key (optional)
# ○ GitHub Copilot Token (optional)
# ○ Content Moderator Key (optional)

# Secrets automatically stored in OS keychain
```

### 3️⃣ Verify Secrets (optional, 2 min)

```bash
python services/secrets_service.py

# Output:
# ✓ Keyring available: True
# ✓ azure-ai-key found
# ✓ bing-search-key found
# ○ anthropic-api-key: optional, not found
```

### 4️⃣ Initialize Database (2 min)

```bash
python scripts/setup_db.py

# Creates: ~/.content-studio/sessions.db
```

### 5️⃣ Run Application (1 min)

Terminal 1:
```bash
uvicorn backend.main:app --reload --port 8000
```

Terminal 2:
```bash
streamlit run frontend/app.py
```

Open browser: **http://localhost:8501**

---

## File Structure Created

```
scripts/
├── setup_secrets.py          ← Interactive keyring setup
└── setup_db.py

services/
└── secrets_service.py        ← Hybrid retrieval (keyring + Key Vault)

.env.example                  ← Config template (no secrets)
.gitignore                    ← Excludes .env, *.db, venv
requirements.txt             ← Includes keyring
```

---

## How It Works in Code

```python
# In your app (backend, services, etc.)
from services.secrets_service import get_secrets_service

# Get secrets service once at startup
secrets_service = get_secrets_service()

# Retrieve secrets (tries keyring first, Key Vault second)
azure_ai_key = secrets_service.get("azure-ai-key")
bing_key = secrets_service.get("bing-search-key")
anthropic_key = secrets_service.get("anthropic-api-key", required=False)

# That's it! No env vars, no files, no git risks
```

---

## Where Are My Secrets Stored?

### macOS
- **Location**: Keychain.app (built-in)
- **View**: Open Keychain Access → Search for "content-studio"
- **Edit**: Double-click to view/modify

### Windows
- **Location**: Credential Manager (built-in)
- **View**: Settings → Accounts → Manage credentials → Generic credentials
- **Edit**: Click → Edit → Update password

---

## When to Use Keyring vs. Key Vault?

| Use Case | Recommendation |
|----------|---|
| Solo development on one laptop | ✅ Keyring only |
| Developing on both Mac and Windows | ⚠️ Keyring + Key Vault fallback |
| Team sharing secrets | ⚠️ Switch to encrypted files (future) |
| Cloud deployment planned | ⚠️ Keep Key Vault fallback ready |
| Compliance/audit logs needed | ⚠️ (Keyring has no audit; use KV) |

---

## Optional: Add Azure Key Vault Fallback

**Why?** So same secrets work on Mac and Windows, and for future cloud deployment.

**Setup** (5 minutes, one-time on one machine):

```bash
# 1. Create Key Vault
az account set --subscription "your-sub-id"
az group create --name rg-content-studio --location eastus
az keyvault create --resource-group rg-content-studio --name kv-content-studio-xxxxx

# 2. Populate it (copy secrets from keyring)
export AZURE_KEYVAULT_NAME="kv-content-studio-xxxxx"
python scripts/setup_secrets.py  # Choose to sync to Key Vault

# 3. Enable fallback
export AZURE_KEYVAULT_NAME="kv-content-studio-xxxxx"  # Add to ~/.zprofile or Windows env
```

Now:
- **Mac**: Tries keychain first (fast) → falls back to Key Vault if needed
- **Windows**: Tries Credential Manager first → falls back to Key Vault if needed
- **Both machines**: Same secrets accessible via Key Vault

---

## Troubleshooting

**Q: "Secret not found" error**  
A: Run `python scripts/setup_secrets.py` again

**Q: "Module keyring not found"**  
A: `pip install keyring` (should be in requirements.txt)

**Q: "Want to update a secret"**  
A: Run setup script again, on which machine to update

**Q: "Using both Mac and Windows, secrets different"**  
A: Either:
  - Run setup_secrets.py on each machine (keyring is local), or
  - Add Key Vault fallback (same secrets on both)

**Q: "Need to deploy to cloud"**  
A: secrets_service.py already supports both keyring and Key Vault, so:
  - Keyring in local development
  - Key Vault in cloud (via Managed Identity)
  - Same code works both places

---

## Security Checklist

✅ Secrets NOT in .env  
✅ Secrets NOT in git  
✅ Secrets encrypted by OS  
✅ No API keys in code  
✅ setup_secrets.py never creates files  
✅ .gitignore excludes .env, *.db, venv  
✅ requirements.txt public (no secrets)  
✅ .env.example public (template only)  

---

## Cost Impact

| Component | Cost | Notes |
|-----------|------|-------|
| Keyring | $0 | Built-in to OS |
| Key Vault (optional) | $0.50/mo | Only if using fallback |
| Azure AI Foundry | $20-50/mo | LLM inference |
| Bing Search | $5-15/mo | Web search |
| **Total (MVP)** | **$25-65/mo** | Mostly LLM/search |

---

## Next Steps

1. ✅ Run setup steps 1-2 above (5 minutes)
2. ✅ Verify with step 3 (secrets_service.py)
3. ✅ Run server with steps 4-5
4. ⏳ Create first content session to test
5. 🔲 Run `/speckit.tasks` for implementation plan

---

## Documentation References

- **Full Plan**: [plan-LOCAL-HYBRID.md](specs/001-content-spec-constitution/plan-LOCAL-HYBRID.md)
- **Secrets Deep Dive**: [SECRETS_MANAGEMENT_EXPLORATION.md](specs/001-content-spec-constitution/SECRETS_MANAGEMENT_EXPLORATION.md)
- **Setup Script**: [scripts/setup_secrets.py](scripts/setup_secrets.py)
- **Secrets Service**: [services/secrets_service.py](services/secrets_service.py)
- **Requirements**: [requirements.txt](requirements.txt)

---

## Summary

**Hybrid approach = best of both worlds:**
- ✅ Fast local development (keyring, instant)
- ✅ Multi-device capability (Key Vault optional)
- ✅ Cloud-ready (same code for cloud deployment)
- ✅ Minimal setup (run one script)
- ✅ Zero cost initially ($0 + APIs)
- ✅ Enterprise-ready (audit logs if using Key Vault)

**Ready? Run `python scripts/setup_secrets.py` now!**
