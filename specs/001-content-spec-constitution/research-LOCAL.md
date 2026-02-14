# Phase 0: Research & Clarifications (LOCAL LAPTOP EDITION)

**Feature**: Personal AI Content Studio MVP  
**Date**: 2026-02-07  
**Status**: Complete (Simplified for Local Development)  
**Target Platform**: Mac/Windows Laptop (Personal Use)

---

## Executive Summary

All key architectural, technology, and workflow decisions have been researched and clarified for **local laptop development**. The system is designed for **personal single-user use** with minimal infrastructure complexity. Cloud services (Azure) are used **only** for:
- Secrets management (Azure Key Vault)
- Web search (Bing Search API + Azure Cognitive Search)
- LLM inference (Azure AI Foundry multi-model support)
- Content safety (Azure Content Moderator)

All compute, storage, and orchestration run **locally** on your Mac/Windows laptop.

---

## 1. Agentic Orchestration Framework

### Decision: LangGraph (Local Execution)

**Rationale**:
- LangGraph is purpose-built for multi-step agentic workflows with state management and human-in-the-loop approvals.
- Native support for branching, loops, and conditional routing (essential for approval gates).
- **Runs entirely in-process** on laptop; no cloud orchestration needed.
- Strong integration with LangChain ecosystem for LLM calls and tool use.
- Better debugging and tracing than CrewAI for local development.

**Alternatives Considered**:
- **CrewAI**: Simpler syntax, but less flexible for approval gates.
- **AutoGen**: Heavier; designed for multi-agent systems we don't need.
- **Custom async orchestration**: Risky; reinventing the wheel.

**Implementation Notes**:
- Use Lang Graph's `StateGraph` to manage session state (topic, outline, framework, visuals, content).
- Define separate `Node` functions for each agent (input, reasoning, research, outline, storytelling, visual, content, platform).
- Use `add_conditional_edges` for approval gates (outline review, framework selection, platform output review).
- Store session state in **SQLite** (local database) after each agent completes.
- All execution happens locally; no cloud dependencies for orchestration.

---

## 2. Secrets Management: Azure Key Vault

### Decision: Azure Key Vault + Local Azure CLI Authentication

**Rationale**:
- **Azure Key Vault**: Enterprise-grade secret storage; keeps API keys out of git and local files.
- **Local authentication**: Use Azure CLI (`az login`) for local development; no Managed Identity needed.
- **Centralized**: All API keys (LLM, search, moderation) stored securely in Key Vault.
- **Audit trails**: All secret access logged in Azure Monitor.
- **No `.env` files**: Secrets fetched at runtime; nothing stored locally beyond cache.

**Implementation Notes**:
- Create Azure Key Vault resource in your Azure subscription.
- Store all API keys: Azure AI Foundry endpoint, Anthropic API key, Bing Search key, GitHub Copilot token, Content Moderator key.
- At app startup, use `DefaultAzureCredential` (Azure SDK) to fetch secrets via local Azure CLI session.
- No secrets in git, environment files, or code.
- Manual `az login` required before running app locally.

---

## 3. Web Search & Fact Validation: Bing Search API + Azure Cognitive Search

### Decision: Azure Cognitive Search + Bing Search API

**Rationale**:
- **Bing Search API** (via Azure Marketplace): Official Microsoft search with built-in credibility scoring.
- **Azure Cognitive Search**: Semantic ranking, AI-enriched results, custom indexing (if needed).
- Seamless integration with Azure AI Services for NLP and entity extraction.
- **Cloud-based but called from laptop**: Local app makes REST API calls to Azure services.
- Compliance-ready (HIPAA, PCI-DSS) for future expansion.

**Implementation Notes**:
- Provision Bing Search API via Azure Marketplace.
- **Research Agent** (running locally) calls Bing Search API for each key claim.
- Use Azure AI Language Service to extract entities and claims (optional; can use local LLM).
- Calculate confidence score = (credible sources found / searches performed) with 70% threshold.
- Store search results in local **SQLite database** for audit trail.
- Use Bing's `freshness=Week` filter for recent, high-quality sources.

---

## 4. LLM Provider: Multi-Model Support via Azure AI Foundry + GitHub Copilot

### Decision: Multi-model routing with Azure AI Foundry + GitHub Copilot + Anthropic

**Rationale**:
- **Azure AI Foundry** (formerly Azure AI Studio): Unified multi-model hub supporting Azure OpenAI, Meta Llama, Mistral, Cohere, and more.
- **GitHub Copilot** (with agent support): Now supports Claude (Anthropic) and GPT-4 via Codex for agentic workflows.
- **Anthropic API directly**: Option to call Claude 3.5 Sonnet directly for tasks requiring structured output.
- **Model Selection Strategy**: Choose the best model for each task:
  - **GPT-4 Turbo** (via Azure AI Foundry or Copilot): Complex reasoning, outline generation, content synthesis
  - **Claude 3.5 Sonnet** (via Copilot or Anthropic API): Structured output, JSON parsing, fact-checking, ethical review
  - **Llama 3.1** (via AI Foundry): Cost-effective for simple classification, summarization
  - **Mistral Large** (via AI Foundry): Multilingual support, European data residency
  - **GitHub Copilot (Codex)**: Code generation and explanation
- **Flexibility**: Each agent specifies its preferred model; fallback to GPT-4 if primary unavailable.
- **Cost Optimization**: Use cheaper models (Llama, Mistral) for validation/classification; reserve GPT-4/Claude for creative tasks.

**Model Routing Logic**:

| Task | Primary Model | Fallback | Rationale |
|------|--------------|----------|-----------|
| Topic extraction | Llama 3.1 (AI Foundry) | GPT-4 | Simple classification task |
| Outline generation | GPT-4 Turbo (AI Foundry) | Claude 3.5 | Complex reasoning required |
| Fact validation | Claude 3.5 (Anthropic/Copilot) | GPT-4 | Structured output for source parsing |
| Content synthesis | GPT-4 Turbo (AI Foundry) | Claude 3.5 | Creative writing, storytelling |
| Platform formatting | Llama 3.1 (AI Foundry) | Mistral | Template-based transformation |
| Code generation | GitHub Copilot (Codex) | GPT-4 | Optimized for code snippets |

**Implementation Notes**:
- **Azure AI Foundry**: Deploy via Azure portal; access via unified endpoint with `model` parameter.
- **GitHub Copilot**: Use in VS Code with `@workspace` agent mode; configure to use Claude or GPT-4.
- **Anthropic API**: Direct REST API calls for Claude 3.5 Sonnet when preferred over Azure OpenAI.
- **API Keys**: Store all keys in Azure Key Vault (AI Foundry endpoint, Anthropic key, GitHub token).
- **Model Router Service**: Create `ModelRouter` class that selects best model per task and handles failover logic.
- **Temperature Settings**: 0.7 for creative tasks; 0.3 for structured/factual tasks.
- **Cost Tracking**: Log model usage per session; estimate costs locally.
- **Local execution**: All LLM calls made from local FastAPI backend; responses stream to Streamlit frontend.

---

## 5. Visual Generation: Mermaid + PlantUML + Python (Local Rendering)

### Decision: Mermaid (client-side) + PlantUML server + Python matplotlib

**Rationale**:
- **Mermaid**: Browser-native rendering in Streamlit; instant visualization.
- **PlantUML**: Server-based rendering for UML/architecture diagrams (optional local PlantUML server or public endpoint).
- **Python matplotlib/plotly**: Data visualizations and charts generated locally.
- **Local execution**: All diagram generation happens on laptop; no cloud rendering needed.

**Implementation Notes**:
- Store diagram definitions (Mermaid code) in SQLite database.
- Visual Agent recommends diagram type based on content.
- Streamlit renders Mermaid diagrams using `streamlit-mermaid` component or raw markdown.
- For PlantUML, use local Java server or public PlantUML server (https://www.plantuml.com/plantuml).
- Python charts saved as static images (PNG/SVG) for platform exports.

---

## 6. Data Storage: SQLite (Local, File-Based)

### Decision: SQLite for all session and reference data

**Rationale**:
- **SQLite**: Lightweight, zero-config, file-based database. Perfect for personal laptop use.
- **No external dependencies**: No server setup, no cloud costs, no network latency.
- **Session history limit**: Keep max 10 recent sessions; auto-delete older sessions to save disk space.
- **ACID transactions**: Full relational support with joins, indexes, constraints.
- **Portability**: Database is a single `.db` file; easy to back up manually (OneDrive, iCloud, Dropbox).
- **Sufficient for MVP**: Personal single-user use; no multi-region or high-scale requirements.

**Alternatives Considered** (rejected for local use):
- **Cosmos DB**: Overkill; requires cloud, costs money, adds latency.
- **PostgreSQL**: Requires server setup; too complex for local laptop use.
- **In-memory only**: No persistence; sessions lost on restart.

**Implementation Notes**:
- **Database Location**: `~/.content-studio/sessions.db` (hidden folder in user home directory).
- **Schema**: Standard SQL schema with tables for:
  - `sessions`: Session metadata and status
  - `outlines`: Outline versions with validation results embedded as JSON
  - `validation_reports`: Fact-checking results
  - `content_drafts`: Final narrative content
  - `platform_versions`: Platform-specific outputs
  - `iteration_feedback`: User feedback rounds
  - Reference tables: `frameworks`, `platforms`, `focus_areas`, `visual_types`
- **Session Limit**: Implement auto-cleanup on app startup: Keep latest 10 sessions; delete older entries.
- **Backup**: Manual user backup via cloud sync (OneDrive, iCloud, Dropbox) of the `~/.content-studio/` folder.
- **Migrations**: Use Alembic for schema changes.
- **No cloud sync**: All data stays local unless user manually backs up; privacy-first design.

---

## 7. Backend: FastAPI (Local Development)

### Decision: FastAPI running locally on laptop (Mac/Windows)

**Rationale**:
- **FastAPI**: Lightweight, async-capable Python framework; excellent for agent workflows with I/O-bound tasks.
- **Local execution**: Runs directly on laptop; no containers or cloud required.
- **Development speed**: Rapid iteration; instant feedback; no deployment overhead.
- **Zero cloud costs**: No compute charges; all processing happens locally.
- **Cross-platform**: Works on Mac and Windows with Python 3.11+.
- **LangGraph integration**: LangGraph state machine runs in-process; fast agent execution.

**Alternative considered** (rejected for local use):
- **Streamlit only**: Could embed all logic in Streamlit, but FastAPI provides better separation of concerns and API testability.
- **Flask**: Older, less async-friendly than FastAPI.

**Implementation Notes**:
- **Run command**: `uvicorn backend.main:app --reload --port 8000`
- **Secrets**: Fetch from Azure Key Vault at startup using Azure SDK + local Azure CLI credentials (`az login`).
- **Agents**: LangGraph orchestrates agents; all state in memory during session; persisted to SQLite after each step.
- **No Docker required**: Direct Python execution for simplicity.
- **Cross-platform paths**: Use `pathlib` for Windows/Mac compatibility.
- **Logging**: Python `logging` module; output to console and local log file.

---

## 8. Frontend: Streamlit (Local Development)

### Decision: Streamlit for rapid prototyping and personal use

**Rationale**:
- **Streamlit**: Fastest path to a working UI; minimal frontend code needed.
- **Python-native**: No JavaScript required; ideal for rapid iteration.
- **Interactive widgets**: Built-in forms, buttons, text inputs, approval gates.
- **Session state**: Streamlit handles session persistence without additional code.
- **Local execution**: Runs on `localhost:8501`; no deployment overhead.
- **Good enough for MVP**: Personal use doesn't require polished SPA experience.
- **Mermaid support**: Can render Mermaid diagrams natively.

**Alternative considered**:
- **Next.js**: Better UX+, but requires TypeScript/React knowledge and more setup time.
- **Gradio**: Similar to Streamlit but less mature for complex workflows.

**Implementation Notes**:
- **Run command**: `streamlit run frontend/app.py`
- **Multi-page app**: Use Streamlit pages for different workflows:
  - `Home.py`: New session creation
  - `History.py`: Browse past sessions
  - `Settings.py`: Configure models, API keys, session limits
- **API calls**: Call FastAPI backend via `requests` library (`http://localhost:8000`).
- **Approval gates**: Use `st.button()` and `st.radio()` for user approval decisions.
- **Visual rendering**: Render Mermaid diagrams using `st.markdown()` with Mermaid syntax or `streamlit-mermaid`.
- **Session state**: Use `st.session_state` to persist data across reruns.

---

## 9. CI/CD & Version Control: Git + GitHub (No Automation for MVP)

### Decision: Git version control; manual testing and deployment

**Rationale**:
- **Git**: Version control for all code and specs; commit regularly.
- **GitHub**: Remote backup and collaboration (optional); private repo recommended.
- **No CI/CD pipelines**: Manual testing and execution for personal laptop use; no automation overhead.
- **Branch strategy**: Simple `main` branch; feature branches for experiments.
- **GitHub Copilot**: Use for coding assistance and agent scaffolding (not for automated deployment).

**Implementation Notes**:
- Commit regularly to local git repository.
- Push to GitHub for backup (optional; use private repo to protect API key references).
- No GitHub Actions workflows required for local development.
- Manual testing via `pytest` before committing.
- `.gitignore`: Exclude SQLite database, `.env` files (if used), `__pycache__`, virtual environments.

---

## 10. Content Moderation & Safety: Azure Content Moderator

### Decision: Azure Content Moderator API (Optional for MVP)

**Rationale**:
- **Azure Content Moderator**: Built-in content filtering for text and images.
- Detects hate speech, profanity, adult content, PII.
- **Optional for personal use**: Can be disabled initially; enable later if publishing broadly.
- Compliance-ready (GDPR, HIPAA) if needed.

**Implementation Notes**:
- Call Content Moderator on final content draft before platform adaptation (optional gate).
- Flag high-confidence risky content; ask user to review.
- Log moderation decisions in SQLite for audit.
- **Can be skipped for MVP**: Personal use assumes user is responsible for content safety.

---

## 11. Deferred for Later (Post-MVP)

The following components are **deferred to a future phase** after the local laptop MVP is proven successful:

### 11a. Disaster Recovery & Automated Backups
- **Current**: Manual file backup via OneDrive/iCloud/Dropbox (SQLite `.db` file is portable)
- **Future**: Automated cloud backups, geo-redundant storage, point-in-time restore

### 11b. Infrastructure as Code (IaC)
- **Current**: Manual setup via Python scripts and local configuration
- **Future**: Azure Bicep templates for cloud deployment if scaling beyond personal use

### 11c. Monitoring & Observability
- **Current**: Local logs via Python `logging` module; print statements for debugging
- **Future**: Application Insights, distributed tracing, cost tracking dashboards

### 11d. Cloud Deployment
- **Current**: Local execution on laptop (Mac/Windows)
- **Future**: Azure Container Apps, Static Web Apps, serverless compute if needed

### 11e. Multi-User Support
- **Current**: Single-user (you) on local laptop
- **Future**: Multi-tenant SaaS with authentication, RBAC, shared workspaces

### 11f. Automated CI/CD
- **Current**: Manual testing and git commits
- **Future**: GitHub Actions for automated testing, linting, security scans

**Decision Rationale**: Focus on MVP functionality first; prove value before adding operational complexity. Keep it simple for personal use.

---

## 12. Testing Strategy (Local Development)

### Decision: Unit + Integration Testing (Manual Execution)

**Levels**:
1. **Unit Tests** → Individual agent functions (reasoning, search, formatting) in isolation.
2. **Integration Tests** → Full workflow (input → validation → outline → framework → content → platform versions).
3. **Contract Tests** → Agent interfaces match expected input/output schemas.

**Tools**:
- `pytest` for unit and integration tests.
- `pydantic` for schema validation (ensures agents pass correct types).
- **Mocking**: Mock Azure services (Key Vault, Bing API, LLM APIs) to run tests without costs.
  - Use `unittest.mock` or `pytest-mock`
  - Mock Azure SDK responses for Key Vault
  - Mock LLM API responses to avoid token costs

**Key test scenarios**:
- Topic intake: Valid input, malformed URL, no description.
- Validation: < 70% confidence (should reject), > 70% confidence (should accept).
- Framework selection: User picks each framework and verifies structure.
- Platform outputs: Each platform gets correct format and tone.
- Approval gates: Outline block, framework selection block, platform version block.
- Key Vault retrieval: Confirm secrets fetched correctly (mocked).
- SQLite operations: Document create/read/update/query all work.

**Execution**:
- Run tests manually: `pytest tests/ -v`
- No automated CI; manual verification before commits.

---

## Phase 0 Findings Summary (LOCAL LAPTOP EDITION)

| Topic | Decision | Confidence | Notes |
|-------|----------|-----------|-------|
| Orchestration | LangGraph (local) | 🟢 High | In-process execution; no cloud |
| Web Search | Bing Search API (cloud) | 🟢 High | Called from local app |
| LLM | Azure AI Foundry + Copilot + Anthropic | 🟢 High | Multi-model routing; cloud inference |
| Visuals | Mermaid + PlantUML + Python | 🟢 High | Local rendering; browser-based |
| Frameworks | 6 templates + custom | 🟢 High | Stored in SQLite reference table |
| Platforms | Auto-generation + review | 🟢 High | Formatted locally |
| Storage | SQLite (local file) | 🟢 High | `~/.content-studio/sessions.db` |
| Secrets | Azure Key Vault | 🟢 High | Fetched via Azure CLI at runtime |
| Backend | FastAPI (local) | 🟢 High | `localhost:8000` |
| Frontend | Streamlit (local) | 🟢 High | `localhost:8501` |
| CI/CD | Git + manual testing | 🟢 High | No automation for MVP |
| Content Safety | Azure Content Moderator (optional) | 🟡 Medium | Can skip for personal use |
| Monitoring | Local logs only | 🟡 Medium | Deferred; `logging` module |
| Disaster Recovery | Manual backup | 🟡 Medium | Deferred; OneDrive/iCloud sync |
| Infrastructure | Manual setup | 🟡 Medium | Deferred; no IaC for local |
| Testing | pytest (manual) | 🟢 High | Unit + integration tests |

**Cloud Services Used** (all called from local laptop):
- Azure Key Vault (secrets)
- Bing Search API (web search)
- Azure AI Foundry (multi-model LLM)
- Azure Content Moderator (optional safety)

**Local Services**:
- FastAPI backend
- Streamlit frontend
- SQLite database
- LangGraph orchestration
- Python logging

---

## Next Phase: Phase 1 Design

✅ **All clarifications resolved for local laptop MVP.**  
✅ **No blocking ambiguities.**  
✅ **Ready to proceed to Phase 1** (data model, contracts, quickstart for local dev).

**Phase 1 Deliverables**:
- `data-model.md`: SQLite schema, session flow
- `contracts/`: Agent I/O schemas, local API endpoints
- `quickstart.md`: Local dev setup (Mac/Windows), first content session walkthrough
