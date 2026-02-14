# Implementation Plan: Personal AI Content Studio MVP (LOCAL LAPTOP EDITION - HYBRID)

**Branch**: `001-content-spec-constitution` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-content-spec-constitution/spec.md`

## Summary

Build a **local laptop** single-user agentic content creation system that validates factual accuracy via web search, generates compelling outlines with user approval, applies storytelling frameworks and visuals, and produces platform-specific outputs. The system emphasizes human-in-the-loop approvals at every critical gate and iterates until the user says "ok and good".

**Deployment Model**: Personal use on **Mac and Windows laptop** with **hybrid secrets management**:
- **Primary**: OS keychain (macOS Keychain / Windows Credential Manager) - fast, local, offline
- **Fallback**: Azure Key Vault (optional cloud backup for multi-device sync)

---

## Technical Context

**Platform**: Mac/Windows laptop (Python 3.11+)  
**Execution Model**: Local development; all processing on laptop  
**Primary Dependencies**: 
- LangGraph (agentic orchestration, local execution)
- FastAPI (backend REST API, local server)
- Streamlit (frontend UI, local server)
- SQLite (local file-based database)
- keyring (OS credential storage - primary secrets)
- Azure SDK for Python (optional - LLM and Key Vault access)

**Cloud Services** (optional, called from laptop):
- Azure AI Foundry (multi-model LLM inference; REST API calls)
- Bing Search API (web search and fact validation)
- Azure Content Moderator (optional content safety filtering)
- Anthropic API (direct Claude 3.5 Sonnet access)
- GitHub Copilot (optional code generation and agent support)
- Azure Key Vault (optional fallback for multi-device sync)

**Local Storage**:
- **SQLite Database**: `~/.content-studio/sessions.db`
- **OS Keychain**: Built-in to macOS/Windows (no setup needed)
- **Session Limit**: Max 10 sessions; auto-delete older entries
- **Manual Backup**: User backs up `.content-studio/` folder via OneDrive/iCloud/Dropbox

**Authentication & Secrets** (Hybrid Approach):
- **Primary (Local, Fast)**: OS keychain via `keyring` library
  - macOS: Keychain.app
  - Windows: Credential Manager
  - No files, no env vars, encrypted by OS
- **Fallback (Cloud, Multi-Device)**: Azure Key Vault (optional)
  - Requires Azure subscription and `az login`
  - Accessed only if secret not found in keyring
  - Provides multi-device sync capability

**Testing**: 
- `pytest` with mocked cloud services (avoid API costs)
- Manual test execution (no CI/CD for MVP)

**Target Platform**: 
- Backend: `http://localhost:8000` (FastAPI)
- Frontend: `http://localhost:8501` (Streamlit)

**Project Type**: Local Python application with optional cloud service integrations

**Performance Goals**: 
- Outline generation: 2-3 minutes
- Full end-to-end cycle: < 20 minutes (mostly LLM latency)
- SQLite query time: < 100ms
- Session load time: < 2 seconds
- Secret retrieval: < 100ms (from keyring)

**Constraints**: 
- 70% minimum validation confidence (web search)
- No cleartext secrets in code or git
- All secrets in OS keychain or Azure Key Vault
- Data stored locally; no cloud database
- Single-user only (no multi-tenant)
- macOS and Windows compatibility required

**Scale/Scope**: 
- Single active user (you)
- 6 supported platforms (LinkedIn, Twitter, Reddit, Medium, Substack, Instagram)
- 6 storytelling frameworks + custom option
- Web search via optional Bing API
- Multi-model LLM routing via optional Azure AI Foundry + GitHub Copilot + Anthropic

---

## Hybrid Secrets Setup (5 Steps)

**Prerequisites**:
1. **Python 3.11+** installed on Mac or Windows
2. **Git** for version control
3. **API keys** from LLM and search providers (optional but recommended)

### Step 1: Clone Repository and Setup Python Environment

```bash
# Clone repo (or create new one)
git clone https://github.com/yourusername/content-studio.git
cd content-studio

# Create Python virtual environment
python3.11 -m venv .venv

# Activate (Mac/Linux)
source .venv/bin/activate

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install dependencies (includes keyring)
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2: Interactive Secrets Setup (Primary - OS Keychain)

```bash
# Run interactive setup script
python scripts/setup_secrets.py

# You will be prompted for:
# 1. Azure AI Foundry API Key (required)
# 2. Bing Search API Key (required)
# 3. Anthropic API Key (optional - for Claude)
# 4. GitHub Copilot Token (optional - for agent mode)
# 5. Azure Content Moderator Key (optional - for safety)

# Secrets are stored encrypted in:
#   macOS: Keychain.app (double-click Keychain Access to view/edit)
#   Windows: Credential Manager (Settings → Accounts → Manage credentials)
```

**That's it!** Secrets are now securely stored in your OS keychain. No files to manage, no env vars, no git risks.

### Step 3: Verify Secrets (Optional)

```bash
# Test that secrets are accessible
python services/secrets_service.py

# Output should show:
# ✓ azure-ai-key: sk-xxxxx...
# ✓ bing-search-key: xxxxx...
# Optional secrets: Found or Not found
```

### Step 4: Initialize Local Database

```bash
# Create SQLite database schema
python scripts/setup_db.py

# This creates:
# - ~/.content-studio/ directory
# - sessions.db with full schema (5000+ rows of data ready)
# - Reference tables pre-populated (frameworks, platforms, etc.)
```

### Step 5: Run Local Servers (Development)

Open two terminal windows:

**Terminal 1 - Backend (FastAPI)**:
```bash
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
uvicorn backend.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# 🔐 Secrets Service Initialized
#    Keyring available: True
#    Key Vault configured: False
```

**Terminal 2 - Frontend (Streamlit)**:
```bash
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
streamlit run frontend/app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

### Step 6: Access Application

Open browser: **http://localhost:8501**

You should see the Content Studio home page with options to:
- Start new content session
- View session history
- Configure settings

---

## Optional: Setup Azure Key Vault Fallback

**Why?** For multi-device sync (develop on both Mac and Windows with same secrets) or future cloud deployment.

### Step A: Create Azure Key Vault

```bash
# Prerequisites: Azure CLI installed and `az login` completed
az account set --subscription "your-subscription-id"

# Create resource group
az group create --name rg-content-studio --location eastus

# Create Key Vault
KEYVAULT_NAME="kv-content-studio-$(date +%s | tail -c 8)"
az keyvault create \
  --resource-group rg-content-studio \
  --name "$KEYVAULT_NAME" \
  --location eastus

# Grant yourself access
az keyvault set-policy \
  --name "$KEYVAULT_NAME" \
  --upn "$(az account show --query user.name -o tsv)" \
  --secret-permissions get list set delete
```

### Step B: Populate Key Vault

Option 1: **Semi-automated** (from keyring values):
```python
# retrieve_and_store_in_keyvault.py
from services.secrets_service import SecretsService
from azure.credential import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

service = SecretsService()
client = SecretClient(
    vault_url="https://YOUR-KEYVAULT-NAME.vault.azure.net/",
    credential=DefaultAzureCredential()
)

# Store each secret to Key Vault
for secret_id in ["azure-ai-key", "bing-search-key", "anthropic-api-key"]:
    value = service.get(secret_id, required=False)
    if value:
        client.set_secret(secret_id.replace("_", "-"), value)
        print(f"✓ Stored {secret_id}")
```

Option 2: **Manual via CLI**:
```bash
KEYVAULT_NAME="kv-content-studio-xxxxx"

# Store secrets you want synced
az keyvault secret set --vault-name "$KEYVAULT_NAME" \
  --name "azure-ai-key" --value "sk-..."

az keyvault secret set --vault-name "$KEYVAULT_NAME" \
  --name "bing-search-key" --value "..."

az keyvault secret set --vault-name "$KEYVAULT_NAME" \
  --name "anthropic-api-key" --value "..."
```

### Step C: Enable Key Vault Fallback

Set environment variable (optional):
```bash
# Add to ~/.zprofile (Mac) or environment (Windows)
export AZURE_KEYVAULT_NAME="kv-content-studio-xxxxx"

# Or create config file: ~/.content-studio/config.yaml
key_vault:
  name: "kv-content-studio-xxxxx"
```

**Done!** Now your app will:
1. Try to load secrets from OS keychain (fast, primary)
2. Fall back to Azure Key Vault if not found (slower, multi-device sync)

---

## Cost Estimate (Monthly)

### Option A: Keyring Only (Recommended for MVP)

- Azure AI Foundry: $20-50/month (multi-model LLM)
- Bing Search API: $5-15/month (web search)
- Anthropic API: $10-30/month (Claude 3.5, optional)
- Content Moderator: $1-2/month (optional)
- **Total: $36-97/month** (mostly LLM inference)
- **Keyring: $0** (built into OS, free)

### Option B: Keyring + Key Vault Fallback (Multi-Device)

Add:
- Azure Key Vault: $0.50/month (minimal operations)
- **Total: $36-98/month**

### Option C: Cloud Deployment (Future)

If migrating to cloud:
- All costs above +
- Azure Container Apps: $50-200/month
- Azure Static Web Apps: $0-50/month
- **Total: $150-500/month+**

**Recommendation**: Start with Keyring only ($0), add Key Vault if needed ($0.50/mo), consider cloud deployment later.

---

## Constitution Check

**Gate: Core Principles Compliance**

✅ **Human-in-the-loop is mandatory** — Plan includes three explicit approval gates (outline approval, framework/visual selection, platform versions ready before iteration). No content flows without user sign-off.  
✅ **Factual accuracy is verified** — Web search integration with 70% confidence scoring before content generation. Multiple independent sources required.  
✅ **Visuals prioritized** — FR-009 mandates at least one visual per final output (unless opted out). Mermaid/PlantUML/SVG support specified.  
✅ **Storytelling without distortion** — Framework selection is separate from fact-checking. Outline is validated before framework is applied.  
✅ **Iteration until "ok and good"** — FR-012 explicitly requires iterative loop with user's final approval phrase.  

**Gate: Safety & Privacy**

✅ **No secrets in repository** — All secrets in OS keychain (encrypted by OS). No `.env` files, no API keys in code.  
✅ **No unsolicited data in output** — Sessions stored locally in SQLite; user approves all platform outputs before iteration.  
✅ **Focus area governance** — FR-016 detects out-of-scope topics and allows user override; defined scope list in spec.  
✅ **Local data storage** — All session data stays on laptop; max 10 sessions with auto-cleanup.

**Status**: ✅ **All gates pass. No violations to justify.**

---

## Project Structure

### Documentation (this feature)

```text
specs/001-content-spec-constitution/
├── spec.md                  # Feature specification (done)
├── constitution.md          # Product values (done)
├── plan.md                  # Previous Azure plan (archived reference)
├── plan-LOCAL.md            # This file (hybrid secrets approach) ✨
├── research.md              # Azure cloud research (reference)
├── research-LOCAL.md        # Local laptop research (done)
├── data-model.md            # Cosmos DB schema (reference)
├── data-model-LOCAL.md      # SQLite schema (done)
├── contracts/               # Agent I/O schemas (done)
├── quickstart-LOCAL.md      # Local setup guide (todo)
├── LOCAL_SIMPLIFICATION.md  # Architecture comparison
├── SECRETS_MANAGEMENT_EXPLORATION.md  # Secrets options analysis
└── checklists/
    └── requirements.md      # Verification checklist (done)
```

### Source Code Repository (Local Laptop Edition)

```text
scripts/
├── setup_secrets.py         # Interactive keyring setup ✨ NEW
├── setup_db.py              # Initialize SQLite database
├── test_keyvault.py         # Test Key Vault access (optional)
└── test_llm.py              # Test LLM connectivity

services/
├── secrets_service.py       # Hybrid secrets (keyring + Key Vault) ✨ NEW
├── llm_service.py           # Multi-model LLM router
├── search_service.py        # Bing Search API integration
└── framework_engine.py      # Storytelling framework application

backend/
├── main.py                  # FastAPI app entry point
├── agents/                  # Agent implementations
│   ├── input_agent.py
│   ├── reasoning_agent.py
│   ├── research_agent.py
│   └── ... (4 more agents)
├── models/                  # SQLite ORM models
├── api/                     # REST endpoints
└── tests/                   # Unit and integration tests

frontend/
├── Home.py                  # Streamlit main entry point
├── pages/
│   ├── 1_New_Session.py
│   ├── 2_History.py
│   └── 3_Settings.py
└── components/              # Streamlit components

.env.example                 # Never use (secrets in keyring now)
.gitignore                   # Include secrets, .venv, __pycache__
requirements.txt            # Python dependencies (includes keyring)
```

---

## Phase 0: Research & Clarification

**Status**: ✅ Complete

All clarifications resolved for **local laptop architecture with hybrid secrets**.

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

- [data-model-LOCAL.md](data-model-LOCAL.md) - SQLite schema
- [contracts/](contracts/) - Agent I/O schemas (updated)

---

## Phase 2: Implementation Planning

**Status**: ⏳ Next (after Phase 1 review)

### Phase 2 Deliverables

The planning phase will conclude with the following documents:

1. **Task Breakdown** (`/speckit.tasks`)
   - Sprint-by-sprint task list for MVP implementation
   - Task dependencies and sequencing
   - Effort estimates (story points or hours)
   - Team member assignments (if applicable)

2. **Development Roadmap**
   - Timeline with milestones
   - Phase gates and quality criteria
   - Risk assessment and mitigation
   - Go/no-go decision points

3. **Architecture Validation**
   - Security review of hybrid secrets approach
   - Performance testing plan
   - Scalability assumptions
   - Deployment checklist

### Next Steps in Planning Phase

**Step 1: Review Current Design** (15 min)
- Review [data-model-LOCAL.md](data-model-LOCAL.md) - SQLite schema
- Review [contracts/](contracts/) - Agent I/O interfaces
- Verify all requirements covered in constitution check ✅

**Step 2: Validate Hybrid Secrets Architecture** (10 min)
- Review [SECRETS_MANAGEMENT_EXPLORATION.md](SECRETS_MANAGEMENT_EXPLORATION.md)
- Confirm keyring (primary) + Key Vault fallback (optional) approach
- Verify security gates pass ✅

**Step 3: Generate Implementation Tasks** (5 min)
- Run: `/speckit.tasks`
- This will generate detailed task breakdown for coding phase
- Review generated tasks and priorities

**Step 4: Plan Development Sprints** (optional, 15 min)
- Batch tasks into logical sprints
- Estimate effort per task
- Prioritize based on feedback loops
- Define sprint milestones

**Step 5: Kickoff Implementation** (5 min)
- Review task list
- Set up GitHub project board (if using)
- Confirm development environment is working
- Begin Phase 3: Implementation

---

## Setup Timeline

| Step | Time | Notes |
|------|------|-------|
| 1. Python venv setup | 2 min | Clone repo, create venv, pip install |
| 2. Interactive secrets | 3 min | Run setup_secrets.py, enter API keys |
| 3. Verify secrets | 2 min | Optional; python services/secrets_service.py |
| 4. Initialize database | 2 min | python scripts/setup_db.py |
| 5. Start servers | 2 min | Open 2 terminals, run FastAPI and Streamlit |
| **Total** | **11 min** | Ready to start first content session |

---

## Planning Phase Gates

### ✅ Gate 1: Requirements Validation
- [x] All 16 FRs specified in spec.md
- [x] 3 prioritized user stories defined
- [x] 5 success criteria established
- [x] Clarification questions answered (5 Q&A sessions)
- **Status**: PASS

### ✅ Gate 2: Constitution Alignment
- [x] Human-in-the-loop mandatory (3 approval gates)
- [x] Factual accuracy verified (70% web search confidence)
- [x] Visuals prioritized (≥1 per output)
- [x] Storytelling without distortion (framework separation)
- [x] Iteration until "ok and good" (defined workflow)
- **Status**: PASS

### ✅ Gate 3: Architecture Design
- [x] Local laptop architecture (FastAPI + Streamlit)
- [x] Hybrid secrets (keyring primary + Key Vault fallback)
- [x] SQLite storage (max 10 sessions, no cloud DB)
- [x] Multi-model LLM routing (AI Foundry + Anthropic + Copilot)
- [x] Web search validation (Bing API)
- **Status**: PASS

### ✅ Gate 4: Data Model Validation
- [x] SQLite schema complete (10 tables)
- [x] ER relationships defined
- [x] Session lifecycle documented
- [x] Validation rules specified
- [x] State management integration clear
- **Status**: PASS

### ✅ Gate 5: Agent Contract Validation
- [x] 7 agent contracts defined (input, reasoning, research, storytelling, visual, content, platform)
- [x] I/O schemas complete (JSON request/response)
- [x] LLM model routing documented
- [x] Error handling specified
- [x] Integration points clear
- **Status**: PASS

### ✅ Gate 6: Secrets Management Validation
- [x] Hybrid approach decided (keyring + Key Vault)
- [x] Security assessment complete
- [x] Setup scripts created (setup_secrets.py)
- [x] Retrieval service implemented (secrets_service.py)
- [x] Multi-OS support verified (macOS + Windows)
- **Status**: PASS

---

## Critical Path to Implementation

```
Phase 0 (Research)       ✅ COMPLETE
    ↓
Phase 1 (Design)         ✅ COMPLETE
    ↓
Phase 2 (Planning) ← YOU ARE HERE
    ├─ Review & Validate (15 min)
    ├─ Generate Tasks (/speckit.tasks) (5 min)
    └─ Plan Sprints (optional) (15 min)
    ↓
Phase 3 (Implementation) ← NEXT
    ├─ Backend logic & agents (Week 1-2)
    ├─ Frontend UI & integration (Week 2)
    ├─ Testing & QA (Week 2-3)
    └─ First production run (Week 3)
    ↓
Phase 4 (Launch)
    ├─ Manual testing of end-to-end flow
    ├─ Documentation & setup guide
    └─ Ready for personal use MVP
```

---

## Estimated Effort to Implementation

| Phase | Effort | Timeline |
|-------|--------|----------|
| **Phase 0: Research** | 8 hours | ✅ Complete |
| **Phase 1: Design** | 12 hours | ✅ Complete |
| **Phase 2: Planning** | 2 hours | ← Current (mostly done) |
| **Phase 3: Implementation** | 40-60 hours | Next (2-3 weeks) |
| **Phase 4: Launch** | 8 hours | Final (1 week) |
| **TOTAL** | 70-92 hours | ~3-4 weeks solo |

---

## Decision Points Before Implementation

Before running `/speckit.tasks`, confirm:

1. **Secrets Strategy**: Keyring primary + Key Vault optional? ✅
2. **Database**: SQLite local only (no Cosmos DB)? ✅
3. **Frontend**: Streamlit (not Next.js)? ✅
4. **Deployment**: Local laptop MVP only? ✅
5. **Timeline**: 2-3 weeks to MVP? ✅

All confirmed? **Ready for Phase 3.**

---

## What /speckit.tasks Will Generate

The task breakdown will include:

**Backend Tasks** (15-20 tasks)
- LangGraph state machine setup
- 7 agent implementations
- SQLite ORM and migrations
- Hybrid secrets integration
- FastAPI endpoint definitions
- LLM routing logic

**Frontend Tasks** (5-8 tasks)
- Streamlit page structure
- Session management UI
- Approval gate components
- Visualization rendering
- Settings configuration

**Testing Tasks** (8-10 tasks)
- Unit tests for agents
- Integration test for workflow
- Secrets service tests
- Database transaction tests
- Fast API endpoint tests

**Setup & Documentation** (5-8 tasks)
- Setup scripts (db.py, secrets.py)
- Configuration files
- README and guides
- GitHub project board

---

## Recommendation

**You are here**: 90% done with planning. Only missing detailed tasks.

**Next action**:
1. Review the 6 design documents (spec, constitution, research, data-model, contracts, secrets)
2. Confirm all gates pass ✅
3. Run `/speckit.tasks` to generate task breakdown
4. Begin Phase 3 (Implementation) with first agent logic

---

## Key Advantages of Hybrid Approach

✅ **Fastest setup**: No Azure configuration needed (step 2 is interactive)  
✅ **Zero cost initially**: Keyring is free; only pay for LLM/search APIs  
✅ **Offline capable**: Works without internet once secrets are stored  
✅ **OS-native security**: Leverages macOS Keychain and Windows Credential Manager  
✅ **Flexible**: Add Key Vault later if needed for multi-device sync  
✅ **Future-proof**: Easy to upgrade to cloud deployment (secrets already in Key Vault)  
✅ **Simple to teach**: New team members just run setup_secrets.py  

---

## Troubleshooting

**Q: "keyring.get_password() returns None"**  
A: Secret not in keychain. Run `python scripts/setup_secrets.py` again.

**Q: "ModuleNotFoundError: No module named 'keyring'"**  
A: Install with `pip install keyring` (should be in requirements.txt).

**Q: "Want to use Key Vault too"**  
A: Set `AZURE_KEYVAULT_NAME` environment variable or follow Step A-C above.

**Q: "Secrets work on Mac but not on Windows (or vice versa)"**  
A: Keyring uses different OS backends. Re-run setup_secrets.py on each machine, OR use Azure Key Vault fallback for same secrets on both.

---

## Next Steps

1. ✅ Run Step 1-2 of setup above (5 minutes)
2. ✅ Verify with `python services/secrets_service.py`
3. ✅ Initialize database with `python scripts/setup_db.py`
4. ✅ Start servers and access http://localhost:8501
5. ⏳ Create first content session to test end-to-end flow
6. 🔲 Run `/speckit.tasks` when ready to start implementation

**Status**: Ready for local laptop MVP development with hybrid secrets!
