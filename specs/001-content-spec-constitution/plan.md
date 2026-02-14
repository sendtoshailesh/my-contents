# Implementation Plan: Personal AI Content Studio MVP

**Branch**: `001-content-spec-constitution` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-content-spec-constitution/spec.md`

## Summary

Build a single-user agentic content creation system that validates factual accuracy via web search, generates compelling outlines with user approval, applies storytelling frameworks and visuals, and produces platform-specific outputs. The system emphasizes human-in-the-loop approvals at every critical gate and iterates until the user says "ok and good".

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/React (frontend)
**Primary Dependencies**: 
- LangGraph (agentic orchestration)
- FastAPI (backend REST API)
- Next.js (frontend SPA)
- Azure OpenAI SDK
- Azure Cosmos DB SDK
- Azure PostgreSQL Driver
- Azure Identity (Managed Identity auth)

**Azure Resources**:
- Subscription ID: [YOUR_SUBSCRIPTION_ID] (configure during setup)
- Resource Group: `rg-content-studio-prod` (create during deployment)
- Region: `eastus` (primary), `westeurope` (secondary for DR)
- Environment: **dev, staging, prod** (Bicep parameterized)

**Storage**:
- **Cosmos DB** (sessions, content, feedback): NoSQL documents with geo-replication
- **PostgreSQL** (frameworks, platforms, focus_areas): Structured reference data
- **Backup**: Azure Backup with 30-day retention; geo-redundant storage

**Container Registry**: Azure Container Registry (ACR) for Docker images

**Authentication & Secrets**: Azure Key Vault + Managed Identity (no environment files; all config via Azure)

**Testing**: pytest with Azure service mocks (avoid costs during testing)

**Target Platform**: Web application (Next.js frontend on Static Web Apps + FastAPI on Container Apps)

**Project Type**: Cloud-native multi-tier (agentic backend + SPA frontend, serverless infrastructure)

**Performance Goals**: 
- Outline generation: 2-3 minutes
- Full end-to-end cycle: < 20 minutes
- API response time: < 5 seconds (p95)
- Container auto-scale: 1-10 instances (cost control)

**Constraints**: 
- 70% minimum validation confidence (web search)
- No cleartext secrets ever stored or logged
- Managed Identity for all authentication (no API keys in code)
- Data residency: US/EU as required by compliance
- GDPR/HIPAA/PCI-DSS compliant

**Scale/Scope**: 
- Single active user (MVP)
- 6 supported platforms (LinkedIn, Twitter, Reddit, Medium, Substack, Instagram)
- 6 storytelling frameworks + custom option
- Web search + semantic ranking via Bing API
- Azure Cognitive Search for advanced indexing
+ Add Azure Subscription Configuration section

---

## Azure Subscription Configuration

**Prerequisites Before Deployment**:
1. Active Azure subscription with sufficient quota
2. GitHub Enterprise account with GitHub Actions access
3. Local Azure CLI installed and authenticated
4. Bicep CLI (included in latest Azure CLI)

**Setup Steps**:

### Step 1: Create Azure Resource Group

```bash
# Define variables
SUBSCRIPTION_ID="your-subscription-id-here"
RESOURCE_GROUP="rg-content-studio-prod"
LOCATION="eastus"

# Set active subscription
az account set --subscription "$SUBSCRIPTION_ID"

# Create resource group
az group create \
   --name "$RESOURCE_GROUP" \
   --location "$LOCATION" \
   --tags "Environment=prod" "Project=content-studio"
```

### Step 2: Create Azure Key Vault

```bash
KEY_VAULT_NAME="kv-content-studio-$(date +%s | tail -c 8)"

# Create Key Vault
az keyvault create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$KEY_VAULT_NAME" \
   --location "$LOCATION" \
   --enable-purge-protection

# Enable managed identity access (will do after creating Container Apps)
```

### Step 3: Deploy Azure OpenAI Service

```bash
OPENAI_RESOURCE="openai-content-studio"
OPENAI_SKU="S0"

# Create OpenAI resource
az cognitiveservices account create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$OPENAI_RESOURCE" \
   --location "eastus" \
   --kind OpenAI \
   --sku "$OPENAI_SKU"

# Deploy GPT-4 Turbo model
az cognitiveservices account deployment create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$OPENAI_RESOURCE" \
   --deployment-name "gpt4-turbo" \
   --model-name "gpt-4-turbo" \
   --model-version "latest"
```

### Step 4: Create Cosmos DB (Sessions)

```bash
COSMOS_ACCOUNT="cosmos-content-studio"
COSMOS_DATABASE="sessions_db"
COSMOS_CONTAINER="sessions"

# Create Cosmos DB account
az cosmosdb create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$COSMOS_ACCOUNT" \
   --kind GlobalDocumentDB \
   --locations "eastus=0" "westeurope=1"

# Create database and container
az cosmosdb database create \
   --resource-group "$RESOURCE_GROUP" \
   --account-name "$COSMOS_ACCOUNT" \
   --name "$COSMOS_DATABASE"

az cosmosdb sql container create \
   --resource-group "$RESOURCE_GROUP" \
   --account-name "$COSMOS_ACCOUNT" \
   --database-name "$COSMOS_DATABASE" \
   --name "$COSMOS_CONTAINER" \
   --partition-key-path "/session_id"
```

### Step 5: Create PostgreSQL (Reference Data)

```bash
POSTGRES_SERVER="postgres-content-studio"
POSTGRES_ADMIN="azureuser"
POSTGRES_PASSWORD="$(openssl rand -base64 32)"  # Generate strong password

# Create PostgreSQL server
az postgres server create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$POSTGRES_SERVER" \
   --location "$LOCATION" \
   --admin-user "$POSTGRES_ADMIN" \
   --admin-password "$POSTGRES_PASSWORD" \
   --sku-name "B_Gen5_1" \
   --storage-size 51200 \
   --enable-storage-autogrow \
   --backup-retention 30 \
   --geo-redundant-backup Enabled

# Store password in Key Vault
az keyvault secret set \
   --vault-name "$KEY_VAULT_NAME" \
   --name "postgres-password" \
   --value "$POSTGRES_PASSWORD"
```

### Step 6: Create Azure Container Registry

```bash
REGISTRY_NAME="crcontentiostudio"

# Create ACR
az acr create \
   --resource-group "$RESOURCE_GROUP" \
   --name "$REGISTRY_NAME" \
   --sku Basic
```

### Step 7: Create Azure Container Apps Environment

```bash
CONTAINER_ENV="env-content-studio"

# Create Container Apps environment
az containerapp env create \
   --name "$CONTAINER_ENV" \
   --resource-group "$RESOURCE_GROUP" \
   --location "$LOCATION"
```

### Step 8: Create Application Insights

```bash
APP_INSIGHTS="insights-content-studio"

# Create Application Insights
az monitor app-insights component create \
   --app "$APP_INSIGHTS" \
   --resource-group "$RESOURCE_GROUP" \
   --location "$LOCATION" \
   --kind web --application-type web
```

### Step 9: Store Secrets in Key Vault

```bash
# Store all Azure resource endpoints and keys
az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "openai-endpoint" \
   --value "$(az cognitiveservices account show --resource-group "$RESOURCE_GROUP" --name "$OPENAI_RESOURCE" --query properties.endpoint -o tsv)"

az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "openai-key" \
   --value "$(az cognitiveservices account keys list --resource-group "$RESOURCE_GROUP" --name "$OPENAI_RESOURCE" --query key1 -o tsv)"

az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "cosmos-connection-string" \
   --value "$(az cosmosdb keys list --resource-group "$RESOURCE_GROUP" --name "$COSMOS_ACCOUNT" --type connection-strings --query connectionStrings[0].connectionString -o tsv)"

az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "bing-search-key" \
   --value "your-bing-search-key"

az keyvault secret set --vault-name "$KEY_VAULT_NAME" \
   --name "github-token" \
   --value "your-github-enterprise-token"
```

### Step 10: Configure GitHub Secrets

In your GitHub Enterprise repository, set these secrets:
```
AZURE_SUBSCRIPTION_ID = <your-subscription-id>
AZURE_RESOURCE_GROUP = rg-content-studio-prod
AZURE_KEY_VAULT_NAME = <your-key-vault-name>
AZURE_ACR_NAME = <your-acr-name>
AZURE_CONTAINER_APP_NAME = content-studio-backend
```

**Cost Estimate**:
- Key Vault: $0.60/month
- Azure OpenAI: ~$50–200/month (usage-based)
- Cosmos DB: ~$100–500/month (RU-based, with free tier)
- PostgreSQL: ~$50/month (B1 tier)
- Container Apps: ~$50–200/month (consumption-based)
- Application Insights: ~$2–10/month
- **Total**: ~$250–1000/month (highly variable based on usage)

---
## Constitution Check

**Gate: Core Principles Compliance**

✅ **Human-in-the-loop is mandatory** — Plan includes three explicit approval gates (outline approval, framework/visual selection, platform versions ready before iteration). No content flows without user sign-off.  
✅ **Factual accuracy is verified** — Web search integration with 70% confidence scoring before content generation. Multiple independent sources required.  
✅ **Visuals prioritized** — FR-009 mandates at least one visual per final output (unless opted out). Mermaid/PlantUML/SVG support specified.  
✅ **Storytelling without distortion** — Framework selection is separate from fact-checking. Outline is validated before framework is applied.  
✅ **Iteration until "ok and good"** — FR-012 explicitly requires iterative loop with user's final approval phrase.  

**Gate: Safety & Privacy**

✅ **No secrets in repository** — Clarified: environment variables with .env.example template; actual .env in .gitignore.  
✅ **No unsolicited data in output** — Sessions are ephemeral; user approves all platform outputs before iteration.  
✅ **Focus area governance** — FR-016 detects out-of-scope topics and allows user override; defined scope list in spec.  

**Status**: ✅ **All gates pass. No violations to justify.**

## Project Structure

### Documentation (this feature)

```text
specs/001-content-spec-constitution/
├── spec.md                  # Feature specification (DONE)
├── constitution.md          # Product values (DONE)
├── plan.md                  # This file (/speckit.plan output)
├── research.md              # Phase 0 output (research & tech decisions)
├── data-model.md            # Phase 1 output (entities, data flow)
├── contracts/               # Phase 1 output (API schemas, agent interfaces)
│   ├── input-agent.yaml
│   ├── reasoning-agent.yaml
│   ├── research-agent.yaml
│   ├── outline-agent.yaml
│   ├── content-agent.yaml
│   ├── visual-agent.yaml
│   ├── platform-agent.yaml
│   └── session-api.yaml
├── quickstart.md            # Phase 1 output (setup, first user journey)
└── checklists/
    └── requirements.md      # Verification checklist (DONE)
```

### Source Code Repository

```text
# Web Backend + Frontend Structure
backend/
├── src/
│   ├── agents/
│   │   ├── input_agent.py         # Topic intake and extraction
│   │   ├── reasoning_agent.py     # Content angle + outline generation
│   │   ├── research_agent.py      # Fact validation via web search
│   │   ├── outline_agent.py       # Outline structuring
│   │   ├── storytelling_agent.py  # Framework application
│   │   ├── visual_agent.py        # Visual strategy & diagram generation
│   │   ├── content_agent.py       # Final content synthesis
│   │   └── platform_agent.py      # Platform-specific formatting
│   ├── models/
│   │   ├── session.py             # Session state and history
│   │   ├── outline.py             # Outline entity
│   │   ├── validation.py          # Validation report
│   │   └── content.py             # Content draft and platform versions
│   ├── services/
│   │   ├── search_service.py      # Web search integration (Tavily/SerpAPI)
│   │   ├── llm_service.py         # LLM integration (Claude/GPT-4)
│   │   ├── visual_generator.py    # Mermaid/SVG/PlantUML generation
│   │   └── framework_engine.py    # Storytelling framework application
│   ├── api/
│   │   ├── routes.py              # REST or GraphQL endpoints
│   │   └── schemas.py             # Request/response validation
│   ├── config.py                  # Configuration, env vars
│   └── main.py                    # FastAPI app initialization
├── tests/
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_services.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── test_workflow.py       # End-to-end approval flow
│   │   └── test_search_validation.py
│   └── contract/
│       └── test_agent_interfaces.py
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   │   ├── TopicInput.tsx
│   │   ├── OutlineReview.tsx      # Approval gate #1
│   │   ├── FrameworkSelector.tsx
│   │   ├── VisualPlanReview.tsx    # Framework & visual selection
│   │   ├── ContentDraft.tsx
│   │   ├── PlatformVersions.tsx    # Platform outputs
│   │   └── IterationLoop.tsx       # Feedback & refinement
│   ├── pages/
│   │   ├── SessionHome.tsx
│   │   ├── ContentStudio.tsx
│   │   └── History.tsx
│   ├── services/
│   │   └── api.ts                 # Client SDK
│   └── App.tsx
├── tests/
│   ├── unit/
│   └── integration/
└── package.json

.env.example                    # Template for environment variables
.env                            # (NOT committed) actual secrets
.gitignore                      # Include .env
README.md
DOCKERFILE
```

**Structure Decision**: Web backend (FastAPI + Python agents) + frontend (React/Streamlit). Backend runs agentic orchestration (LangGraph); frontend provides session UI. This separation allows testing agents independently and scaling frontend separately later.

## Phase 0: Research & Clarification → `research.md`

**Status**: ✅ Complete

All clarifications resolved (12 topics). No blocking ambiguities remain.

---

## Phase 1: Design & Contracts → `data-model.md`, `contracts/`, `quickstart.md`

**Status**: ✅ Complete

### Phase 1 Deliverables

1. **Data Model** ([data-model.md](data-model.md))
   - 6 core entities: Session, Outline, ValidationReport, ContentDraft, PlatformVersion, IterationFeedback
   - Complete ER relationships and data flow diagram
   - SQLite schema and state management (LangGraph)
   - Validation rules for all entities

2. **Agent Contracts** (`contracts/` directory)
   - `input-agent.md`: Topic intake and focus area classification
   - `reasoning-agent.md`: Content angle and outline generation
   - `research-agent.md`: Fact validation via web search (70% confidence)
   - `storytelling-visual-agent.md`: Framework application and visual planning
   - `content-agent.md`: Final narrative synthesis
   - `platform-agent.md`: Platform-specific formatting for 6 platforms
   - `session-api.md`: REST API endpoints for session orchestration

3. **Quickstart Guide** ([quickstart.md](quickstart.md))
   - Local development setup (5 steps, ~15 minutes)
   - First content session walkthrough (10 steps, ~20 minutes)
   - Real-world scenario: LinkedIn post on "LLMs and EI in Leadership"
   - Troubleshooting guide and reference commands

### Phase 1 Quality Gates ✅

- [x] All entities documented with field types and relationships
- [x] Data flow diagram shows complete session lifecycle
- [x] Agent I/O contracts are specific and testable
- [x] API endpoints cover all user workflows
- [x] Quickstart includes realistic, end-to-end walkthrough
- [x] Error handling and edge cases documented per contract
- [x] Constitution principles verified in design (human-in-the-loop gates, validation, visuals, etc.)

---

## Phase 2: Task Generation & Implementation Planning

**Status**: Awaiting `/speckit.tasks` command

**Next Step**: Run `/speckit.tasks` to generate implementation task breakdown and team assignments.
