# Implementation Plan: Personal AI Content Studio MVP (LOCAL LAPTOP EDITION)

**Branch**: `001-content-spec-constitution` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-content-spec-constitution/spec.md`

## Summary

Build a **local laptop** single-user agentic content creation system that validates factual accuracy via web search, generates compelling outlines with user approval, applies storytelling frameworks and visuals, and produces platform-specific outputs. The system emphasizes human-in-the-loop approvals at every critical gate and iterates until the user says "ok and good".

**Deployment Model**: Personal use on **Mac and Windows laptop** with minimal cloud dependencies.

## Technical Context

**Platform**: Mac/Windows laptop (Python 3.11+)  
**Execution Model**: Local development; all processing on laptop  
**Primary Dependencies**: 
- LangGraph (agentic orchestration, local execution)
- FastAPI (backend REST API, local server)
- Streamlit (frontend UI, local server)
- Azure SDK for Python (Key Vault client, LLM clients)
- SQLite (local file-based database)

**Cloud Services** (called from laptop):
- Azure Key Vault (secrets management; accessed via Azure CLI authentication)
- Azure AI Foundry (multi-model LLM inference; REST API calls)
- Bing Search API (web search and fact validation)
- Azure Content Moderator (optional content safety filtering)
- Anthropic API (direct Claude 3.5 Sonnet access)
- GitHub Copilot (optional code generation and agent support)

**Local Storage**:
- **SQLite Database**: `~/.content-studio/sessions.db`
- **Session Limit**: Max 10 sessions; auto-delete older entries
- **Manual Backup**: User backs up `.content-studio/` folder via OneDrive/iCloud/Dropbox

**Authentication & Secrets**: 
- Azure Key Vault stores all API keys (LLM, search, moderation)
- Local authentication via `az login` (Azure CLI)
- No `.env` files; secrets fetched at runtime

**Testing**: 
- `pytest` with mocked Azure services (avoid API costs)
- Manual test execution (no CI/CD for MVP)

**Target Platform**: 
- Backend: `http://localhost:8000` (FastAPI)
- Frontend: `http://localhost:8501` (Streamlit)

**Project Type**: Local Python application with cloud API integrations

**Performance Goals**: 
- Outline generation: 2-3 minutes
- Full end-to-end cycle: < 20 minutes (mostly LLM latency)
- SQLite query time: < 100ms
- Session load time: < 2 seconds

**Constraints**: 
- 70% minimum validation confidence (web search)
- No cleartext secrets in code or git
- Azure Key Vault for all API keys
- Data stored locally; no cloud database
- Single-user only (no multi-tenant)
- macOS and Windows compatibility required

**Scale/Scope**: 
- Single active user (you)
- 6 supported platforms (LinkedIn, Twitter, Reddit, Medium, Substack, Instagram)
- 6 storytelling frameworks + custom option
- Web search via Bing API
- Multi-model LLM routing via Azure AI Foundry + GitHub Copilot + Anthropic

---

## Local Development Setup

**Prerequisites**:
1. **Python 3.11+** installed on Mac or Windows
2. **Git** for version control
3. **GitHub account** (optional; for Copilot and agent support)
4. **Azure subscription** (optional; for cloud services and Key Vault fallback)
5. **Azure CLI** (optional; only if using Key Vault fallback)

**Setup Steps**:

### Step 1: Create Azure Key Vault (One-Time Setup)

```bash
# Define variables
SUBSCRIPTION_ID="your-subscription-id-here"
RESOURCE_GROUP="rg-content-studio"
LOCATION="eastus"
KEY_VAULT_NAME="kv-content-studio-$(date +%s | tail -c 8)"

# Set active subscription
az account set --subscription "$SUBSCRIPTION_ID"

# Create resource group
az group create \
   --name "$RESOURCE_GROUP" \
   --location "$LOCATION" \
   --tags "Environment=personal" "Project=content-studio"

# Create Key Vault
az keyvault create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$KEY_VAULT_NAME" \
   --location "$LOCATION" \
   --enable-rbac-authorization false

# Grant yourself access (using Azure CLI user identity)
az keyvault set-policy \
   --name "$KEY_VAULT_NAME" \
   --upn "$(az account show --query user.name -o tsv)" \
   --secret-permissions get list set delete
```

### Step 2: Provision Azure AI Foundry Endpoint (One-Time Setup)

```bash
# Create Azure AI Services (multi-model hub)
AI_SERVICES_NAME="ai-content-studio"

az cognitiveservices account create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$AI_SERVICES_NAME" \
   --location "eastus" \
   --kind AIServices \
   --sku S0

# Get endpoint and key
AI_ENDPOINT=$(az cognitiveservices account show \
   --resource-group "$RESOURCE_GROUP" \
   --name "$AI_SERVICES_NAME" \
   --query properties.endpoint -o tsv)

AI_KEY=$(az cognitiveservices account keys list \
   --resource-group "$RESOURCE_GROUP" \
   --name "$AI_SERVICES_NAME" \
   --query key1 -o tsv)
```

### Step 3: Create Bing Search API Resource (One-Time Setup)

```bash
BING_SEARCH_NAME="bing-content-studio"

az cognitiveservices account create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$BING_SEARCH_NAME" \
   --location "global" \
   --kind BingSearch \
   --sku S1

# Get Bing Search key
BING_KEY=$(az cognitiveservices account keys list \
   --resource-group "$RESOURCE_GROUP" \
   --name "$BING_SEARCH_NAME" \
   --query key1 -o tsv)
```

### Step 4: Store Secrets in Key Vault

```bash
# Store Azure AI Foundry credentials
az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "azure-ai-endpoint" --value "$AI_ENDPOINT"

az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "azure-ai-key" --value "$AI_KEY"

# Store Bing Search key
az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "bing-search-key" --value "$BING_KEY"

# Store Anthropic API key (get from https://console.anthropic.com/)
az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "anthropic-api-key" --value "your-anthropic-key-here"

# Optional: GitHub Copilot token (if using Copilot agent mode)
az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "github-copilot-token" --value "your-github-token-here"

# Optional: Content Moderator key
az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "content-moderator-key" --value "your-moderator-key-here"
```

### Step 5: Clone Repository and Setup Python Environment

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

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Create Local Configuration File

Create `config.yaml` in project root (NOT committed to git):

```yaml
key_vault:
  name: "kv-content-studio-12345678"  # Your Key Vault name

database:
  path: "~/.content-studio/sessions.db"
  max_sessions: 10

llm:
  default_model: "gpt-4-turbo"
  fallback_model: "claude-3.5-sonnet"
  temperature_creative: 0.7
  temperature_factual: 0.3

search:
  provider: "bing"
  confidence_threshold: 0.7

platforms:
  - linkedin
  - twitter
  - reddit
  - medium
  - substack
  - instagram
```

Add `config.yaml` to `.gitignore`.

### Step 7: Initialize Local Database

```bash
# Run database setup script
python scripts/setup_db.py

# This creates:
# - ~/.content-studio/ directory
# - sessions.db with schema (sessions, outlines, validations, content, platforms, feedback)
# - Reference data tables (frameworks, platforms, focus_areas, visual_types)
```

### Step 8: Verify Setup

```bash
# Test Azure Key Vault access
python scripts/test_keyvault.py

# Expected output:
# ✅ Connected to Key Vault: kv-content-studio-12345678
# ✅ Retrieved secret: azure-ai-endpoint
# ✅ Retrieved secret: bing-search-key

# Test LLM connectivity
python scripts/test_llm.py

# Expected output:
# ✅ Azure AI Foundry: GPT-4 Turbo responding
# ✅ Anthropic API: Claude 3.5 Sonnet responding

# Test SQLite database
python scripts/test_db.py

# Expected output:
# ✅ Database exists: ~/.content-studio/sessions.db
# ✅ All tables created: sessions, outlines, validations, content, platforms, feedback
# ✅ Reference data loaded: 6 frameworks, 6 platforms, 8 visual types
```

### Step 9: Run Local Servers

Open two terminal windows:

**Terminal 1 - Backend (FastAPI)**:
```bash
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
uvicorn backend.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Application startup complete.
# INFO:     Connected to Azure Key Vault
# INFO:     Loaded 6 storytelling frameworks
# INFO:     Loaded 6 platform templates
```

**Terminal 2 - Frontend (Streamlit)**:
```bash
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
streamlit run frontend/app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
# Network URL: http://192.168.1.x:8501
```

### Step 10: Access Application

Open browser: **http://localhost:8501**

You should see the Content Studio home page with options to:
- Start new content session
- View session history
- Configure settings

---

## Cost Estimate (Monthly)

**Azure Cloud Services** (pay-as-you-go):
- **Azure Key Vault**: $0.03/10,000 operations (~$0.50/month for personal use)
- **Azure AI Foundry** (multi-model LLM):
  - GPT-4 Turbo: $10/1M input tokens, $30/1M output tokens (~$20-50/month for 20-50 sessions)
  - Claude 3.5: Via Anthropic API, ~$3/1M input, $15/1M output (~$10-30/month)
  - Llama 3.1: ~$0.50/1M tokens (minimal cost for classification tasks)
  - Mistral Large: ~$2/1M tokens
- **Bing Search API**: $7/1,000 queries (~$5-15/month for ~1,000 searches)
- **Azure Content Moderator** (optional): $1/1,000 transactions (~$1-2/month)

**Local Costs**: $0 (all compute, storage on your laptop)

**Total Estimated Cost**: **$35-100/month** (highly variable based on usage)

For **10-20 content sessions/month**:
- ~50,000 LLM input tokens/session
- ~20,000 LLM output tokens/session
- ~10 web searches/session
- Estimated: **$40-60/month**

---

## Constitution Check

**Gate: Core Principles Compliance**

✅ **Human-in-the-loop is mandatory** — Plan includes three explicit approval gates (outline approval, framework/visual selection, platform versions ready before iteration). No content flows without user sign-off.  
✅ **Factual accuracy is verified** — Web search integration with 70% confidence scoring before content generation. Multiple independent sources required.  
✅ **Visuals prioritized** — FR-009 mandates at least one visual per final output (unless opted out). Mermaid/PlantUML/SVG support specified.  
✅ **Storytelling without distortion** — Framework selection is separate from fact-checking. Outline is validated before framework is applied.  
✅ **Iteration until "ok and good"** — FR-012 explicitly requires iterative loop with user's final approval phrase.  

**Gate: Safety & Privacy**

✅ **No secrets in repository** — All secrets in Azure Key Vault; fetched at runtime via Azure CLI. No `.env` files, no API keys in code.  
✅ **No unsolicited data in output** — Sessions stored locally in SQLite; user approves all platform outputs before iteration.  
✅ **Focus area governance** — FR-016 detects out-of-scope topics and allows user override; defined scope list in spec.  
✅ **Local data storage** — All session data stays on laptop; max 10 sessions with auto-cleanup.

**Status**: ✅ **All gates pass. No violations to justify.**

---

## Project Structure

### Documentation (this feature)

```text
specs/001-content-spec-constitution/
├── spec.md                  # Feature specification (DONE)
├── constitution.md          # Product values (DONE)
├── plan.md                  # This file (/speckit.plan output)
├── research.md              # Phase 0 output (Azure cloud edition)
├── research-LOCAL.md        # Phase 0 output (LOCAL LAPTOP EDITION) ✨
├── data-model.md            # Phase 1 output (entities, SQLite schema)
├── contracts/               # Phase 1 output (API schemas, agent interfaces)
│   ├── input-agent.md
│   ├── reasoning-agent.md
│   ├── research-agent.md
│   ├── storytelling-visual-agent.md
│   ├── content-agent.md
│   ├── platform-agent.md
│   └── session-api.md
├── quickstart.md            # Phase 1 output (local laptop setup)
└── checklists/
    └── requirements.md      # Verification checklist (DONE)
```

### Source Code Repository (Local Laptop Edition)

```text
# Local Python Application Structure
backend/
├── src/
│   ├── agents/
│   │   ├── input_agent.py         # Topic intake and extraction
│   │   ├── reasoning_agent.py     # Content angle + outline generation
│   │   ├── research_agent.py      # Fact validation via Bing Search
│   │   ├── storytelling_agent.py  # Framework application
│   │   ├── visual_agent.py        # Visual strategy & Mermaid generation
│   │   ├── content_agent.py       # Final content synthesis
│   │   └── platform_agent.py      # Platform-specific formatting
│   ├── models/
│   │   ├── session.py             # SQLite ORM models
│   │   ├── outline.py             # Outline entity
│   │   ├── validation.py          # Validation report
│   │   └── content.py             # Content draft and platform versions
│   ├── services/
│   │   ├── search_service.py      # Bing Search API integration
│   │   ├── llm_service.py         # Multi-model LLM router
│   │   ├── visual_generator.py    # Mermaid/PlantUML generation
│   │   ├── keyvault_service.py    # Azure Key Vault client
│   │   └── framework_engine.py    # Storytelling framework application
│   ├── api/
│   │   ├── routes.py              # FastAPI REST endpoints
│   │   └── schemas.py             # Pydantic request/response models
│   ├── config.py                  # Configuration loader
│   └── main.py                    # FastAPI app initialization
├── tests/
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_services.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── test_workflow.py       # End-to-end approval flow
│   │   └── test_search_validation.py
│   └── mocks/
│       ├── mock_llm.py            # Mock Azure AI Foundry responses
│       ├── mock_keyvault.py       # Mock Key Vault responses
│       └── mock_search.py         # Mock Bing Search responses
└── requirements.txt

frontend/
├── Home.py                         # Main Streamlit app entry point
├── pages/
│   ├── 1_New_Session.py           # New content session workflow
│   ├── 2_History.py               # Browse past sessions
│   └── 3_Settings.py              # Configure models, platforms, API keys
├── components/
│   ├── topic_input.py             # Topic input form
│   ├── outline_review.py          # Approval gate #1
│   ├── framework_selector.py      # Framework + visual selection
│   ├── content_preview.py         # Draft content display
│   ├── platform_versions.py       # Platform output review
│   └── iteration_loop.py          # Feedback & refinement
└── requirements.txt

scripts/
├── setup_db.py                     # Initialize SQLite database
├── test_keyvault.py               # Verify Key Vault access
├── test_llm.py                    # Test LLM connectivity
└── test_db.py                     # Verify database schema

config.yaml.example                 # Template for local configuration
config.yaml                         # (NOT committed) actual config
.gitignore                          # Include config.yaml, .venv, __pycache__
README.md                           # Local setup instructions
```

**Structure Decision**: Single Python application with FastAPI backend and Streamlit frontend. All orchestration runs locally via LangGraph. SQLite stores all session data. No Docker, no containers, no cloud deployment infrastructure.

---

## Phase 0: Research & Clarification → `research-LOCAL.md`

**Status**: ✅ Complete

All clarifications resolved for **local laptop architecture**. Key decisions:
- **Multi-model LLM** via Azure AI Foundry + GitHub Copilot + Anthropic
- **SQLite** for all storage (max 10 sessions)
- **Local execution** for FastAPI + Streamlit
- **Azure Key Vault** for secrets (accessed via Azure CLI)
- **Bing Search API** for web search
- **Deferred**: Monitoring, DR, IaC, cloud deployment (post-MVP)

---

## Phase 1: Design & Contracts → `data-model.md`, `contracts/`, `quickstart.md`

**Status**: ⏳ In Progress (Updating for Local Laptop)

### Phase 1 Deliverables

1. **Data Model** ([data-model.md](data-model.md)) - **NEEDS UPDATE**
   - Revert from Cosmos DB/PostgreSQL to **SQLite schema**
   - Add session limit logic (max 10 sessions, auto-delete)
   - Update state management for local LangGraph execution
   - Add backup/restore procedures (manual file copy)

2. **Agent Contracts** (`contracts/` directory) - **MOSTLY COMPLETE**
   - `input-agent.md`: Topic intake (no changes needed)
   - `reasoning-agent.md`: Outline generation (no changes needed)
   - `research-agent.md`: Update for Bing Search API specifics
   - `storytelling-visual-agent.md`: Update for multi-model LLM routing
   - `content-agent.md`: Update for model selection logic
   - `platform-agent.md`: No changes needed
   - `session-api.md`: Update for local FastAPI endpoints (`localhost:8000`)

3. **Quickstart Guide** ([quickstart.md](quickstart.md)) - **NEEDS REWRITE**
   - Local development setup (Mac/Windows, Python venv)
   - Azure Key Vault setup (one-time)
   - First content session walkthrough (using local Streamlit UI)
   - Troubleshooting guide (Azure CLI auth, SQLite access, LLM connectivity)

### Phase 1 Quality Gates

- [ ] SQLite schema documented with all tables and indexes
- [ ] Session limit logic (max 10) clearly specified
- [ ] Multi-model LLM routing logic documented
- [ ] Agent I/O contracts updated for local execution
- [ ] Local API endpoints documented (`localhost:8000`)
- [ ] Quickstart includes Mac and Windows setup instructions
- [ ] Manual backup/restore procedures documented
- [ ] Constitution principles verified in design

---

## Phase 2: Task Generation & Implementation Planning

**Status**: Awaiting `/speckit.tasks` command

**Next Step**: Run `/speckit.tasks` to generate implementation task breakdown for **local laptop architecture**.

**Expected Tasks**:
1. Setup Python project structure
2. Implement SQLite models and migrations
3. Create Azure Key Vault service client
4. Implement multi-model LLM router (AI Foundry + Anthropic)
5. Build LangGraph state machine for agent orchestration
6. Implement all 7 agents (input, reasoning, research, storytelling, visual, content, platform)
7. Create FastAPI REST API endpoints
8. Build Streamlit multi-page app
9. Write unit and integration tests (with mocks)
10. Create setup scripts and documentation
