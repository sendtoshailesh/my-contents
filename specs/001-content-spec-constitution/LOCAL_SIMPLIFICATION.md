# Local Laptop Simplification Summary

**Date**: 2026-02-07  
**Feature**: Personal AI Content Studio MVP  
**Change**: Simplified from Azure cloud architecture to local laptop development

---

## Overview

After completing the Azure cloud migration design, we pivoted to **local laptop architecture** for the MVP phase. This decision prioritizes:
- **Faster MVP iteration** (no cloud deployment overhead)
- **Minimal costs** (only pay for Azure API calls; no infrastructure charges)
- **Personal use focus** (single-user on Mac/Windows laptop)
- **Defer complexity** (monitoring, DR, IaC, multi-user to post-MVP)

---

## Architecture Comparison

### Before: Azure Cloud-Native Architecture

| Component | Azure Service | Notes |
|-----------|---------------|-------|
| **Secrets Management** | Azure Key Vault + Managed Identity | Secure, no env vars |
| **LLM** | Azure OpenAI Service (GPT-4 Turbo) | Single-provider lock-in |
| **Storage (Sessions)** | Cosmos DB (NoSQL, geo-distributed) | Global replication, high throughput |
| **Storage (Reference)** | PostgreSQL (managed) | Structured SQL data |
| **Backend** | Azure Container Apps (serverless) | Auto-scale 1-10 instances |
| **Frontend** | Azure Static Web Apps (Next.js) | Global CDN, auto-HTTPS |
| **Search** | Bing Search API + Azure Cognitive Search | Advanced semantic ranking |
| **Monitoring** | Application Insights + Log Analytics | Real-time dashboards, alerts |
| **CI/CD** | GitHub Actions + Azure Bicep | Automated deployments |
| **Disaster Recovery** | Geo-redundant backups, failover | Multi-region replication |
| **Cost** | $250-1000/month | Variable based on usage |

### After: Local Laptop Architecture

| Component | Solution | Notes |
|-----------|----------|-------|
| **Secrets Management** | Azure Key Vault (via Azure CLI) | Still secure; accessed locally via `az login` |
| **LLM** | **Multi-model routing** (Azure AI Foundry + Anthropic + GitHub Copilot) | Flexible model selection per task |
| **Storage (All Data)** | **SQLite (local file)** | `~/.content-studio/sessions.db` |
| **Backend** | **FastAPI (local server)** | `localhost:8000` |
| **Frontend** | **Streamlit (local server)** | `localhost:8501` |
| **Search** | Bing Search API (cloud REST API) | Called from local app |
| **Monitoring** | **Python `logging` module** | Local logs; console output |
| **CI/CD** | **Git version control (manual)** | No automated pipelines |
| **Disaster Recovery** | **Manual backup** (OneDrive/iCloud) | Copy `.db` file to cloud folder |
| **Cost** | **$35-100/month** | Only Azure API calls; no infrastructure |

---

## Key Changes

### 1. Multi-Model LLM Strategy (New Feature)

**Before**: Single Azure OpenAI Service (GPT-4 Turbo only)

**After**: Multi-model routing with:
- **Azure AI Foundry** (unified hub): GPT-4 Turbo, Llama 3.1, Mistral Large
- **Anthropic API** (direct): Claude 3.5 Sonnet
- **GitHub Copilot** (agent mode): GPT-4, Claude, Codex

**Model Selection Logic**:
| Task | Primary Model | Fallback | Rationale |
|------|--------------|----------|-----------|
| Topic extraction | Llama 3.1 (AI Foundry) | GPT-4 | Simple classification |
| Outline generation | GPT-4 Turbo (AI Foundry) | Claude 3.5 | Complex reasoning |
| Fact validation | Claude 3.5 (Anthropic/Copilot) | GPT-4 | Structured output |
| Content synthesis | GPT-4 Turbo (AI Foundry) | Claude 3.5 | Creative writing |
| Platform formatting | Llama 3.1 (AI Foundry) | Mistral | Template-based |
| Code generation | GitHub Copilot (Codex) | GPT-4 | Code-optimized |

**Benefits**:
- Cost optimization (use cheaper models for simple tasks)
- Flexibility (choose best model per task)
- Avoid vendor lock-in (multi-provider strategy)

---

### 2. Storage Simplification: Cosmos DB + PostgreSQL → SQLite

**Before**: 
- Cosmos DB (sessions, content, feedback) - NoSQL, geo-distributed
- PostgreSQL (frameworks, platforms, focus areas) - SQL, managed service

**After**: 
- **SQLite** (all data) - Local file database (`~/.content-studio/sessions.db`)
- **Session limit**: Max 10 sessions; auto-delete older entries
- **Manual backup**: User copies `.db` file to OneDrive/iCloud/Dropbox

**Schema Changes**:
- All JSON fields stored as TEXT in SQLite (e.g., `focus_area_match`, `sections`, `sources`)
- Boolean fields stored as INTEGER (0 = false, 1 = true)
- Foreign key constraints enforced with `ON DELETE CASCADE`
- Indexes added for frequent queries (session lookup, cleanup)

**Session Cleanup Logic**:
```sql
-- Run on app startup
DELETE FROM sessions
WHERE id NOT IN (
    SELECT id FROM sessions
    ORDER BY created_at DESC
    LIMIT 10
);
```

---

### 3. Backend: Azure Container Apps → FastAPI (Local)

**Before**: 
- Azure Container Apps (serverless, auto-scale 1-10 instances)
- Docker container with FastAPI
- Managed Identity for Azure services

**After**: 
- **FastAPI running locally** (`uvicorn backend.main:app --reload --port 8000`)
- No Docker (direct Python execution)
- Azure SDK with local `az login` credentials

**Changes**:
- Remove Dockerfile
- Remove Container Apps deployment config
- Remove Managed Identity auth (use Azure CLI local auth)
- Add local startup scripts (`setup_db.py`, `test_keyvault.py`, etc.)

---

### 4. Frontend: Azure Static Web Apps (Next.js) → Streamlit (Local)

**Before**: 
- Next.js SPA hosted on Azure Static Web Apps
- Global CDN, auto-HTTPS
- TypeScript + React

**After**: 
- **Streamlit multi-page app** (`streamlit run frontend/app.py`)
- `localhost:8501`
- Python-native UI (no TypeScript/React needed)

**Benefits**:
- Faster MVP iteration (no frontend build step)
- Python-only stack (no TypeScript knowledge required)
- Built-in session state and approval gates
- Mermaid diagram rendering via `st.markdown()` or `streamlit-mermaid`

**Streamlit Pages**:
- `Home.py`: New session creation
- `pages/1_New_Session.py`: Content creation workflow
- `pages/2_History.py`: Browse past sessions
- `pages/3_Settings.py`: Configure models, platforms, API keys

---

### 5. Secrets Management: No Change (Still Azure Key Vault)

**Before**: Azure Key Vault + Managed Identity  
**After**: Azure Key Vault + Azure CLI local authentication

**Why keep Azure Key Vault for local dev?**
- Secrets stay centralized (no `.env` files, no git commits)
- Enterprise-grade security (audit logs, access policies)
- Multi-device sync (same Key Vault accessible from Mac and Windows laptop)
- Future-proof (easy to add Managed Identity when deploying to cloud later)

**Local Access**:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Uses local `az login` session
credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://kv-content-studio-12345678.vault.azure.net/", credential=credential)

# Fetch secrets at runtime
azure_ai_key = client.get_secret("azure-ai-key").value
bing_key = client.get_secret("bing-search-key").value
anthropic_key = client.get_secret("anthropic-api-key").value
```

---

### 6. Monitoring: Application Insights → Python `logging`

**Before**: 
- Application Insights + Log Analytics
- Real-time dashboards, alerts, distributed tracing
- Cost: ~$2-10/month

**After**: 
- **Python `logging` module**
- Console output + local log file (`~/.content-studio/app.log`)
- Cost: $0

**Logging Configuration**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler("~/.content-studio/app.log")  # Local log file
    ]
)
```

**Deferred**: Application Insights, distributed tracing, cost dashboards (post-MVP)

---

### 7. CI/CD: GitHub Actions + Bicep → Git (Manual)

**Before**: 
- GitHub Actions workflows for automated testing, building, deploying
- Azure Bicep templates for infrastructure provisioning
- Automated deployments to Azure Container Apps + Static Web Apps

**After**: 
- **Git version control** (local commits, GitHub backup)
- **Manual testing** (`pytest tests/ -v`)
- **No CI/CD pipelines** (no automation for personal use)

**Deferred**: GitHub Actions, automated testing, Bicep IaC (post-MVP)

---

### 8. Disaster Recovery: Geo-Redundant Backups → Manual File Copy

**Before**: 
- Geo-redundant storage (Cosmos DB replication to multiple regions)
- Automated backups with 30-day retention
- Point-in-time restore capabilities
- Cost: Included in Cosmos DB/PostgreSQL pricing

**After**: 
- **Manual backup**: Copy `~/.content-studio/sessions.db` to OneDrive/iCloud/Dropbox
- **User responsibility**: Remember to back up before major changes
- **Restore**: Copy backed-up `.db` file back to `~/.content-studio/`

**Future Enhancement** (optional):
- Automated daily backup via `cron` (Mac) or Task Scheduler (Windows)
- Not included in MVP; manual backup sufficient for personal use

---

## Files Updated

### New Files Created (Local Architecture)

1. **research-LOCAL.md**: Local laptop research (Phase 0, simplified)
   - Multi-model LLM strategy
   - SQLite storage decision
   - Local FastAPI + Streamlit setup
   - Deferred: monitoring, DR, IaC, cloud deployment

2. **plan-LOCAL.md**: Local laptop implementation plan
   - Azure Key Vault setup (one-time)
   - Azure AI Foundry provisioning
   - Local Python environment setup
   - 10-step local development guide
   - Cost estimate: $35-100/month

3. **data-model-LOCAL.md**: SQLite schema and ER diagrams
   - 10 tables (6 core + 4 reference)
   - Session limit logic (max 10 sessions)
   - Manual backup/restore procedures
   - LangGraph state management integration

4. **LOCAL_SIMPLIFICATION.md**: This file (architecture comparison summary)

### Files Retained (Still Relevant)

- **spec.md**: Feature specification (no changes needed)
- **constitution.md**: Product values (no changes needed)
- **contracts/**: Agent I/O schemas (minor updates needed for Bing API specifics)
- **checklists/requirements.md**: Requirements validation checklist

### Files Archived (Azure Cloud Version)

- **research.md**: Azure cloud research (renamed to `research-AZURE.md` for reference)
- **plan.md**: Azure subscription setup guide (renamed to `plan-AZURE.md`)
- **data-model.md**: Cosmos DB + PostgreSQL schema (renamed to `data-model-AZURE.md`)
- **AZURE_MIGRATION.md**: Azure migration summary (kept as reference)

---

## Cost Impact

### Before: Azure Cloud (Monthly)

- Azure Key Vault: $0.60
- Azure OpenAI (GPT-4): $50-200 (usage-based)
- Cosmos DB: $100-500 (RU-based, with free tier)
- PostgreSQL: $50 (B1 tier)
- Container Apps: $50-200 (consumption-based)
- Static Web Apps: $0 (free tier)
- Application Insights: $2-10
- **Total**: **$250-1000/month**

### After: Local Laptop (Monthly)

- Azure Key Vault: $0.50 (minimal operations)
- **Azure AI Foundry** (multi-model):
  - GPT-4 Turbo: $20-50 (~20-50 sessions)
  - Claude 3.5 (Anthropic): $10-30
  - Llama 3.1: ~$0.50 (classification)
  - Mistral Large: ~$2 (multilingual)
- Bing Search API: $5-15 (~1,000 searches)
- Content Moderator (optional): $1-2
- **Total**: **$35-100/month**

**Savings**: **$215-900/month** (85-90% reduction)

---

## Cloud Services Still Used (Called from Laptop)

1. **Azure Key Vault**: Secrets storage (accessed via Azure CLI `az login`)
2. **Azure AI Foundry**: Multi-model LLM inference (REST API calls)
3. **Bing Search API**: Web search and fact validation
4. **Azure Content Moderator** (optional): Content safety filtering
5. **Anthropic API** (direct): Claude 3.5 Sonnet (optional)
6. **GitHub Copilot** (optional): Agent mode with Claude and Codex

**Why keep these cloud services?**
- **Key Vault**: Enterprise-grade secrets management; no local `.env` files
- **LLM APIs**: No local GPU needed; pay-per-use pricing
- **Bing Search**: Official Microsoft search; credibility scoring built-in
- **Content Moderator**: Compliance-ready safety filtering (GDPR, HIPAA)

---

## Deferred to Post-MVP Phase

The following components are **not included in the local laptop MVP** and will be re-evaluated after proving the concept:

1. **Cloud Deployment** (Azure Container Apps, Static Web Apps)
   - Reason: Local laptop execution is sufficient for personal use
   - Future: Deploy to cloud if sharing with team or scaling beyond personal use

2. **Monitoring & Observability** (Application Insights, Log Analytics)
   - Reason: Python `logging` module is sufficient for local debugging
   - Future: Add distributed tracing and dashboards if deploying to cloud

3. **Disaster Recovery** (Geo-redundant backups, automated failover)
   - Reason: Manual file backup to OneDrive/iCloud is sufficient for personal use
   - Future: Implement automated backups if data criticality increases

4. **Infrastructure as Code** (Azure Bicep templates, automated deployments)
   - Reason: Manual Azure CLI commands are sufficient for one-time setup
   - Future: Add IaC if deploying to multiple environments or teams

5. **Multi-User Support** (Authentication, RBAC, shared workspaces)
   - Reason: Single-user MVP on local laptop
   - Future: Add Azure AD B2C, RBAC if expanding to multi-tenant SaaS

6. **Automated CI/CD** (GitHub Actions, automated testing, security scans)
   - Reason: Manual testing and git commits are sufficient for personal development
   - Future: Add CI/CD if collaborating with team or publishing to production

---

## Migration Path (If Needed Later)

**Scenario**: After MVP proves valuable, you want to deploy to Azure cloud for team collaboration or broader use.

**Migration Steps**:

1. **Database Migration**: SQLite → Azure Cosmos DB + PostgreSQL
   - Export SQLite data to JSON
   - Import JSON to Cosmos DB (sessions, content, feedback)
   - Load reference data (frameworks, platforms) to PostgreSQL
   - Update ORM models to use Azure SDKs

2. **Containerization**: FastAPI → Docker + Azure Container Apps
   - Create Dockerfile for FastAPI backend
   - Build and push image to Azure Container Registry
   - Deploy to Azure Container Apps with Managed Identity

3. **Frontend Deployment**: Streamlit → Azure Static Web Apps (or keep Streamlit on Container Apps)
   - Option A: Rewrite frontend in Next.js (better UX for web)
   - Option B: Deploy Streamlit to Container Apps (keep Python-native UI)

4. **Secrets Management**: Azure CLI → Managed Identity
   - Enable Managed Identity on Container Apps
   - Grant Key Vault access to Managed Identity
   - Remove Azure CLI authentication from code

5. **Monitoring**: Add Application Insights SDK to FastAPI + frontend

6. **CI/CD**: Create GitHub Actions workflows for automated deployments

7. **Infrastructure**: Create Azure Bicep templates for all resources

**Estimated effort**: 2-3 weeks (assuming existing Azure cloud design from `research-AZURE.md`, `plan-AZURE.md`, `data-model-AZURE.md`)

---

## Recommendations

### For MVP Phase (Current)

✅ **Use local laptop architecture**:
- Faster iteration (no deployment overhead)
- Lower costs ($35-100/month vs. $250-1000/month)
- Simpler development (no Docker, no cloud debugging)
- Sufficient for personal use (single-user, 10 session limit)

✅ **Multi-model LLM strategy**:
- Flexibility (choose best model per task)
- Cost optimization (use cheaper models for simple tasks)
- Avoid vendor lock-in (multi-provider)

✅ **Keep Azure Key Vault**:
- Enterprise-grade secrets management
- No local `.env` files (git-safe)
- Future-proof (easy to add Managed Identity later)

### For Post-MVP Phase (Future)

⏳ **Consider cloud deployment if**:
- Sharing with team members (multi-user requirements)
- Need for automated backups and disaster recovery
- Compliance requirements (audit logs, geo-redundancy)
- Scale beyond personal use (higher throughput, global access)

⏳ **Add monitoring/observability if**:
- Debugging complex issues (need distributed tracing)
- Cost tracking (need to optimize LLM API spend)
- Performance optimization (need query performance insights)

⏳ **Implement IaC if**:
- Deploying to multiple environments (dev, staging, prod)
- Team collaboration (reproducible infrastructure)
- Disaster recovery (infrastructure rebuild automation)

---

## Next Steps

1. ✅ **Phase 0 Complete** (research-LOCAL.md)
2. ✅ **Phase 1 Design** (plan-LOCAL.md, data-model-LOCAL.md)
3. ⏳ **Update Agent Contracts** (contracts/ directory)
   - Minimal changes needed (mostly architecture-agnostic)
   - Update `research-agent.md` for Bing API specifics
   - Update `storytelling-visual-agent.md` for multi-model LLM routing
4. ⏳ **Create Local Quickstart Guide** (quickstart-LOCAL.md)
   - Mac and Windows setup instructions
   - First content session walkthrough
   - Troubleshooting guide
5. 🔲 **Run `/speckit.tasks`** to generate implementation tasks

**Status**: Ready to proceed with local laptop MVP implementation. All design decisions documented and validated.
