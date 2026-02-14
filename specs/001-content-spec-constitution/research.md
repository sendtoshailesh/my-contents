# Phase 0: Research & Clarifications

**Feature**: Personal AI Content Studio MVP  
**Date**: 2026-02-07  
**Status**: Complete

---

## Executive Summary

All key architectural, technology, and workflow decisions have been researched and clarified. No blocking ambiguities remain. The project is ready to move to Phase 1 (design).

---

## 1. Agentic Orchestration Framework

### Decision: LangGraph

**Rationale**:
- LangGraph is purpose-built for multi-step agentic workflows with state management and human-in-the-loop approvals.
- Native support for branching, loops, and conditional routing (essential for approval gates).
- Strong integration with LangChain ecosystem for LLM calls and tool use.
- Better debugging and tracing than CrewAI for a personal tool.

**Alternatives Considered**:
- **CrewAI**: Simpler syntax, but less flexible for approval gates. State management less transparent.
- **AutoGen**: Microsoft's framework, but heavier and geared toward multi-agent negotiation (not needed here).
- **Custom async orchestration**: Risky; would require building approval gate logic from scratch.

**Implementation Notes**:
- Use LangGraph's `StateGraph` to manage session state (topic, outline, framework, visuals, content).
- Define separate `Node` functions for each agent (input, reasoning, research, outline, storytelling, visual, content, platform).
- Use `add_conditional_edges` for approval gates (outline review, framework selection, platform output review).
- Store session state in SQLite or file-based store for recovery and audit.

---

## 3. Web Search & Fact Validation: Azure Cognitive Search + Bing Search API

### Decision: Azure Cognitive Search + Bing Search API (UPGRADED from Tavily)

**Rationale**:
- **Azure Cognitive Search**: Enterprise-grade search service with AI enrichment, semantic ranking, and vector search. Indexes content and provides full-text + semantic search capabilities.
- **Bing Search API** (via Azure Marketplace): Official Microsoft search API, built-in entity recognition and credibility scoring. Integrates seamlessly with Azure AI Services.
- Seamless integration with Azure AI Language Service for NLP, entity extraction, and content enrichment.
- RBAC, audit logging, and compliance certifications (HIPAA, PCI-DSS).
- Scales with workload; no expensive per-query third-party API costs.
- Bing Search includes freshness filters, source credibility scoring, and entity recognition out-of-the-box.

**Alternatives Considered** (rejected):
- **Tavily**: Third-party dependency; requires separate API key management; not Azure-native; no compliance certifications.
- **Google Search API**: Not integrated with Azure ecosystem; higher cost at scale; less control over data residency.
- **Manual web scraping**: Fragile, violates ToS, slow, no credibility scoring.

**Implementation Notes**:
- Provision **Bing Search API** via Azure Marketplace (integrated billing).
- Provision **Azure Cognitive Search** for indexing your own content + enrichment.
- **Research Agent** calls Bing Search API for each key claim extracted from outline.
- Use **Azure AI Language Service** to extract entities and key claims from outline sections.
- Score credibility based on Bing's domain authority + source ranking.
- Calculate confidence score = (credible sources found / searches performed) with 70% threshold.
- Store search results in **Azure Cosmos DB** for audit trail and session recovery.
- Use Bing's built-in `freshness=Week` filter for recent, high-quality sources.

---


## 4. LLM Provider: Azure OpenAI Service

### Decision: Azure OpenAI Service (GPT-4 Turbo + Embeddings)

**Rationale**:
- **Azure OpenAI** is Microsoft-managed OpenAI access with enterprise SLAs, VNet support, and compliance certifications (HIPAA, PCI-DSS, SOC 2).
- Same models as OpenAI (GPT-4, GPT-4 Turbo) with low-latency endpoints in Azure data centers.
- Seamless integration with other Azure AI Services (Language, Content Moderator, etc.).
- RBAC, audit logging, and cost management via Azure Cost Management.
- Supports long context windows (128k tokens) for complex reasoning tasks (outline generation, content synthesis).
- Managed capacity reservations reduce costs significantly at scale.
- Data residency control (EU, US, etc.) for compliance.

**Alternatives Considered** (rejected):
- **OpenAI API directly**: Less control over data location; no VNet integration; no managed SLA.
- **Claude via Anthropic**: Not integrated with Azure; adds external dependency; harder to manage at scale.
- **Local LLMs (Llama, Mistral)**: Require GPU infrastructure; lower reasoning quality; maintenance overhead.

**Implementation Notes**:
- Deploy Azure OpenAI resource in your Azure subscription (resource group).
- Deploy GPT-4 Turbo model for reasoning and content generation.
- Deploy text-embedding-3-small for semantic search and content similarity matching.
- Store API endpoint and key in Azure Key Vault (accessed via Managed Identity).
- Use structured output (JSON schemas) to ensure agents return parseable responses.
- Set temperature: `0.7` for reasoning (consistent but creative), `0.3` for validation (factual, safe).
- Monitor usage via Azure Monitor; set up cost alerts via Azure Cost Management.
---

## 5. Visual Generation: Mermaid, PlantUML, SVG (unchanged)

### Decision: Mermaid (primary) + PlantUML (fallback) + Python/SVG (for custom diagrams)

**Rationale**:
- Mermaid is browser-native and renders instantly. No server-side rendering needed.
- PlantUML for UML/architecture diagrams where Mermaid falls short.
- Python matplotlib/plotly for data visualizations and charts.
- SVG for custom illustrations if needed (can be hand-coded or generated via Python).

**Alternatives Considered**:
- **Graphviz**: Powerful but CLI-dependent; more complex to integrate.
- **D3.js**: Overkill for content-focused visuals; adds frontend complexity.
- **Canvas/Canvas.js**: Not semantic; hard to update or modify programmatically.

**Implementation Notes**:
- Store diagram definitions (Mermaid code) in session, not rendered images (improves editability).
- Visual Agent recommends diagram type based on content (flow → flowchart, architecture → graph, timeline → timeline, etc.).
- Return diagram code + suggestion text; frontend renders with Mermaid.js.
- For code output visuals (hello world, etc.), use Python REPL output or annotated code blocks.

---

## 6. Data Storage: Azure Cosmos DB (NoSQL) + Azure Database for PostgreSQL

### Decision: Cosmos DB (sessions & content) + PostgreSQL (reference data)

**Rationale**:
- **Cosmos DB**: Excellent for semi-structured session documents, JSON complex objects, and rapid iteration. Multi-region replication for disaster recovery.
- **PostgreSQL**: Structured relational data with ACID transactions, strong consistency. Managed via Azure Database for PostgreSQL.
- Hybrid approach: Store session documents in Cosmos DB; store reference data (frameworks, platforms, focus_areas) in PostgreSQL.
- Both provide automatic backups, point-in-time recovery, and monitoring via Azure Monitor.
- RBAC and VNet integration for security. Encryption at rest and in transit.

**Alternatives Considered** (rejected):
- **SQLite (local)**: No scalability, no managed backups, no RBAC, no compliance support.
- **Cosmos DB only**: Overkill for simple relational reference data; cost inefficient.
- **PostgreSQL only**: Not ideal for nested JSON session documents; denormalization needed.

**Implementation Notes**:
- **Cosmos DB**: Create container for `sessions` document collection. Store `Session`, `Outline`, `ValidationReport`, `ContentDraft`, `PlatformVersion`, `IterationFeedback` as nested structures within session documents.
- **PostgreSQL**: Create tables for `frameworks`, `platforms`, `focus_areas`, `visual_types`, `users` (for future multi-user expansion).
- Store connection strings in Azure Key Vault (accessed via Managed Identity).
- Enable Azure Backup for disaster recovery (30-day retention).
- Set up geo-replication for Cosmos DB across 2 regions (US + EU).

---

## 7. Backend: Azure Container Apps + FastAPI

### Decision: Azure Container Apps (serverless) + FastAPI

**Rationale**:
- **Azure Container Apps**: Serverless container orchestration, auto-scaling (0 to N instances), built-in networking, low ops overhead.
- No need to manage Kubernetes or container infrastructure yourself.
- Pay-per-execution pricing; optimal for variable/bursty agentic workloads.
- **Managed Identity** integration; connects to Key Vault and other Azure services seamlessly.
- GitHub Actions integration for automated deployment.
- Built-in health checks, traffic splitting, and traffic management (useful for canary deployments).
- **FastAPI**: Lightweight, async-capable, excellent for agent workflows with multiple I/O operations.

**Alternative**: Azure App Service (managed VMs) if you need more customization or persistent resources (not recommended for this use case).

**Implementation Notes**:
- Containerize FastAPI app via Docker; store image in Azure Container Registry (ACR).
- Deploy to Container Apps via GitHub Actions (auto-deploy on commit to main).
- Configure environment via Container App object properties (pull secrets from Key Vault).
- Set autoscaling: min 1 instance, max 10 (cost control); scale on CPU/memory.
- Set up health check: `/health` endpoint (returns 200 OK).

---

## 8. Frontend: Azure Static Web Apps + Next.js

### Decision: Azure Static Web Apps + Next.js (or React SPA)

**Rationale**:
- **Azure Static Web Apps**: Serverless hosting for static sites and SPAs. Built-in CI/CD with GitHub Actions.
- **Next.js**: React framework with SSR/SSG, better UX and SEO than Streamlit.
- GitHub integration: Auto-deploy on commit to `main`; preview deployments for PRs.
- Low cost; pay per usage (hosting + compute for functions).
- Built-in authentication (Azure AD integration for future).
- Global CDN for fast content delivery.

**Alternative**: Streamlit (if you want faster prototyping; less customizable UI).

**Implementation Notes**:
- Build Next.js app; deploy to GitHub.
- Connect Static Web Apps to GitHub repo; auto-deploy on commit.
- Configure environment variables via Static Web Apps settings (or inline in GitHub Actions).
- Create Azure Function for API (or use Container Apps backend as API endpoint).
- Set up API routes in Static Web Apps to proxy calls to Container Apps backend.

---

## 9. Storytelling Frameworks: Predefined vs. Custom

### Decision: 6 predefined frameworks + custom option

**Frameworks**:

| Framework | Use Case | Structure |
|-----------|----------|-----------|
| **TED** | Tech talks, thought leadership | Hook → Context → Insight → Implication → Call-to-action |
| **Hero's Journey** | Personal stories, transformations | Call to Adventure → Refusal → Meeting the Mentor → Crossing Threshold → Tests → Reward → Return |
| **Problem → Solution → Impact** | How-to, guides, technical posts | Problem Setup → Solution Overview → Detailed Steps → Real-world Impact → Takeaways |
| **AIDA** | Engagement hooks, LinkedIn posts | Attention → Interest → Desire → Action |
| **Before–After–Bridge** | Emotional/change-focused | Current State → Vision → How to Bridge the Gap → Action Steps |
| **Custom** | User-defined structure | User provides section titles and descriptions |

**Implementation Notes**:
- Each framework has a template (section names + suggested content guidelines).
- Storytelling Agent applies framework by mapping outline sections onto framework structure.
- User can view framework template before final content generation and confirm or customize.

---

## 10. Platform Specialization: Predefined Templates

### Decision: Platform-specific templates generated automatically, reviewed by user

**Platform Templates**:

| Platform | Tone | Format | Length | Key Constraints |
|----------|------|--------|--------|-----------------|
| **LinkedIn** | Professional, thought leadership | 1–3 paragraphs with optional image/article link | 500–1500 chars | Engagement-focused, actionable takeaways |
| **Twitter/X** | Punchy, conversational, trendy | Thread (5–10 tweets linked) or standalone | 280 chars per tweet | Short sentences, hooks, hashtags |
| **Reddit** | Discussion-oriented, authentic | Post + comments section setup | 1000–3000 chars | Community-aware, source links, discussion prompts |
| **Medium / Substack** | Long-form, narrative-rich | Full article with headers, visuals, code | 2000–5000 words | In-depth reasoning, examples, visuals integrated |
| **Instagram** | Visual-first, casual, emoji-friendly | Carousel captions (5–7 slides) | 200–300 chars per slide | Visual-driven; each slide has a hook |

**Implementation Notes**:
- Platform Agent receives the full content draft and transforms it per template.
- Use LLM prompt per platform with specific guidelines (e.g., "For Twitter, break into punchy one-liners with #hashtags").
- Return platform version + a brief note on what was changed and why.
- User reviews versions and provides feedback in the iteration loop.

---

## 11. CI/CD & Version Control: GitHub Enterprise + GitHub Actions

### Decision: GitHub Enterprise Server (or GitHub.com with Enterprise features) + GitHub Actions

**Rationale**:
- **GitHub Enterprise**: Centralized repository management, advanced security (GitHub Advanced Security), audit logging, IP whitelisting.
- **GitHub Actions**: Native CI/CD for Azure deployments. No need for separate CI/CD tool.
- **GitHub Copilot Enterprise**: AI-assisted code review, PR summaries, and generation aligned with Microsoft tech stack.
- Branch protection rules, mandatory reviews, and automated testing gates.
- Secrets management: GitHub Secrets can sync with Azure Key Vault (via GitHub Actions).

**Implementation Notes**:
- Store all code in GitHub Enterprise (organization account).
- Create GitHub Action workflows for:
	- **Build & Test**: Run pytest, pylint, security scans (Trivy for container images).
	- **Build Docker Image**: Build image, scan for vulnerabilities, push to Azure Container Registry.
	- **Deploy to Container Apps**: Update Container App with new image (pull from ACR).
	- **Deploy Frontend**: Build Next.js, deploy to Static Web Apps.
	- **Deploy Infrastructure**: Run Bicep deployment if infrastructure changed.
- Required status checks: Tests pass, security scans pass, code review approved.
- Use GitHub Secrets for non-sensitive values; store actual credentials in Azure Key Vault (accessed via Managed Identity in container).

---

## 12. Content Moderation & Safety: Azure Content Moderator

### Decision: Azure Content Moderator API

**Rationale**:
- Built-in content filtering for text and images.
- Detects hate speech, profanity, adult content, personally identifiable information (PII).
- Provides confidence scores for moderation decisions.
- Integrates seamlessly with content generation pipeline.
- Compliance-ready (GDPR, HIPAA, PCI-DSS).

**Implementation Notes**:
- Call Content Moderator on final content draft before platform adaptation.
- Flag high-confidence risky content; ask user to review and confirm.
- Log all moderation decision for audit and compliance.
- Store moderation results in Cosmos DB with session.

---

## 13. Monitoring & Observability: Azure Monitor + Application Insights

### Decision: Azure Application Insights + Azure Log Analytics

**Rationale**:
- **Application Insights**: Real-time monitoring, performance metrics, exception tracking, user behavior analytics.
- **Log Analytics**: Centralized logging for all Azure services + app logs.
- Distributed tracing for multi-step agentic workflows.
- Cost tracking and budget alerts.
- Integration with Azure Dashboard for real-time visibility.
- Automated anomaly detection and smart alerts.

**Implementation Notes**:
- Instrument FastAPI app with Application Insights SDK.
- Log all agent operations, API calls, state transitions, and validation results.
- Set up alerts: Errors (immediate), high latency (> 5s), Key Vault access failures.
- Create Azure Dashboard showing: Active sessions, success rate, agent latency, cost trends.
- Daily cost reports sent via Logic Apps.

---

## 14. Disaster Recovery & Backups: Azure Backup + Geo-Redundancy

### Decision: Azure Backup + Geo-Redundant Storage (GRS)

**Rationale**:
- **Azure Backup**: Automated daily backups of Cosmos DB and PostgreSQL with point-in-time restore (30-day retention).
- **Geo-Redundant Storage**: Automatic replication across regions (e.g., US Primary + Europe Secondary).
- **Azure Site Recovery**: Failover configuration for Container Apps if primary region fails.
- RTO (Recovery Time Objective): < 1 hour; RPO (Recovery Point Objective): < 24 hours.

**Implementation Notes**:
- Enable automatic backups for both databases (30-day retention policy).
- Test restore procedures quarterly to ensure RTO/RPO targets are met.
- Set up geo-replication for Cosmos DB across US + Europe regions.
- Document runbooks for disaster recovery scenarios.

---

## 15. Infrastructure as Code: Azure Bicep + GitHub Actions

### Decision: Azure Bicep + GitHub Actions for automated deployment

**Rationale**:
- **Azure Bicep**: Declarative IaC for Azure resources. Simpler and more readable than ARM templates. Version-controlled infrastructure.
- **GitHub Actions**: Automated infrastructure deployment on commit. Infrastructure changes reviewed via PR before deployment.
- Repeatable, auditable deployments. Easy rollback via version control.

**Infrastructure to Deploy**:
- Azure Key Vault (secrets storage)
- Azure OpenAI Service (GPT-4 deployment)
- Azure Container Registry (Docker image storage)
- Azure Container Apps (FastAPI backend)
- Azure Static Web Apps (Next.js frontend)
- Azure Cosmos DB (session storage)
- Azure Database for PostgreSQL (reference data)
- Azure Application Insights (monitoring)
- Azure Cognitive Search (semantic search)
- Bing Search API (provisioned via Marketplace)
- Azure Content Moderator (content safety)
- Azure Log Analytics (centralized logging)

**Implementation Notes**:
- Create `infra/` directory with `.bicep` files for each resource (e.g., `keyvault.bicep`, `container-apps.bicep`, `databases.bicep`).
- Create main `main.bicep` that orchestrates all resources.
- Create GitHub Action workflow: `deploy-infrastructure.yml` that runs `az deployment group create` on commit to `main`.
- Store Azure subscription ID and resource group name in GitHub Secrets.
- Require infrastructure review approval before deployment to production.

### Decision: SQLite (local) + file-based session snapshots

**Rationale**:
- SQLite is lightweight, requires no external service, and plays nicely with local development.
- Each session is stored as a JSON snapshot for easy review and recovery.
- No authentication required (single-user MVP).

**Alternatives Considered**:
- **PostgreSQL**: Overkill for single-user MVP; requires server setup.
- **Firebase/Supabase**: Adds external dependency; violates single-user local-first principle.
- **In-memory only**: Fragile; no audit trail or recovery.

**Implementation Notes**:
- Session table: `id | topic | outline | outline_approved | framework_choice | visual_plan | content_draft | platform_versions | created_at | updated_at`.
- Store full session JSON in a `sessions/` directory (date-stamped).
- Provide a History view to browse past sessions and reuse outlines/content.

---

## 8. Secrets Management: Azure Key Vault + Managed Identity

### Decision: Azure Key Vault + Managed Identity (UPGRADED from env variables)

**Rationale**:
- Azure Key Vault is enterprise-grade, audited, and complies with security standards (HIPAA, PCI-DSS, SOC 2).
- Managed Identity (via App Service or Container Apps) eliminates the need for hardcoded credentials or `.env` files.
- No secrets in git, environment files, or code.
- Automatic secret rotation support.
- Audit trails for all secret access via Azure Monitor.
- RBAC for fine-grained access control.

**Secrets to Store**:
- Azure OpenAI API endpoint and key
- Bing Search API key
- Cosmos DB connection string
- PostgreSQL connection string
- Application Insights instrumentation key
- GitHub Enterprise token (for CI/CD)

**Implementation Notes**:
- Create Azure Key Vault resource in your resource group.
- Enable Managed Identity on Container Apps and Static Web Apps.
- Grant managed identity `Key Vault Secrets User` role via RBAC.
- In code, use `DefaultAzureCredential` (Azure SDK) to authenticate and retrieve secrets at runtime.
- No `.env` files needed; all configuration via Key Vault and application settings.
- Regular security scans via Azure Security Center.

---

## 9. Focus Area Scope & Out-of-Scope Detection

### Decision: Predefined focus area list + LLM-based classification

**Clarification (from planning phase)**:
- Defined focus areas: AI/ML/GenAI, Cloud, Migration & Modernization, Emerging tech trends, Emotional Intelligence.
- Input Agent (with LLM assistance) classifies the topic against these areas.
- If topic is outside: system warns the user and allows override.
- No hard rejection; respects user expertise.

**Implementation Notes**:
- Use LLM prompt: "Classify this topic into [list of areas]. If none match, respond 'OUT_OF_SCOPE'."
- If out-of-scope, show a warning with the classification result and ask user to confirm.
- Log decision for debugging.

---

## 10. Validation Confidence Threshold

### Decision: 70% minimum confidence score

**Clarification (from planning phase)**:
- Confidence score = (credible sources supporting key claims / total sources found).
- If confidence < 70%, system blocks progression and asks for outline regeneration.
- 70% balances rigor (catches misinformation) with pragmatism (allows emerging topics).

**Implementation Notes**:
- Research Agent calculates score after searching each claim.
- Return score in validation report to user.
- If regenerating, provide LLM with feedback on weak claims to improve next outline.

---

## 16. Testing Strategy (Azure-native mocking)

### Decision: Unit + Integration + Contract Testing

**Levels**:
1. **Unit Tests** → Individual agent functions (reasoning, search, formatting) in isolation.
2. **Integration Tests** → Full workflow (input → validation → outline → framework → content → platform versions).
3. **Contract Tests** → Agent interfaces match expected input/output schemas.

**Tools**:
- `pytest` for unit and integration tests.
- `pydantic` for schema validation (ensures agents pass correct types).
- Mocking for Azure services (Key Vault, Cosmos DB, OpenAI, Search) to run tests without cost.
- Use Azure SDK mocking libraries: `azure-identity` mock, `azure-cosmos` mock, `openai` mock.

**Key test scenarios**:
- Topic intake: Valid input, malformed URL, no description.
- Validation: < 70% confidence (should reject), > 70% confidence (should accept).
- Framework selection: User picks each framework and verifies structure.
- Platform outputs: Each platform gets correct format and tone.
- Approval gates: Outline block, framework selection block, platform version block.
- Key Vault retrieval: Confirm secrets are fetched correctly.
- Cosmos DB operations: Document create/read/update/query.

---

## Phase 0 Findings Summary (Azure + GitHub Enterprise Edition)

| Topic | Decision | Confidence | Status |
|-------|----------|-----------|--------|
| Orchestration | LangGraph | 🟢 High | Cloud-agnostic; works with all backends |
| Web Search | Azure Cognitive Search + Bing API | 🟢 High | UPGRADED from Tavily; now Azure-native |
| LLM | Azure OpenAI Service (GPT-4 Turbo) | 🟢 High | UPGRADED from OpenAI API; compliance-ready |
| Visuals | Mermaid + PlantUML + Python | 🟢 High | Cloud-agnostic; client-side or Container Apps rendering |
| Frameworks | 6 templates + custom | 🟢 High | Platform-agnostic; stored in PostgreSQL |
| Platforms | Auto-generation + review | 🟢 High | Platform-agnostic; formatted by Content Agent |
| Storage (Sessions) | Cosmos DB (NoSQL) | 🟢 High | UPGRADED from SQLite; geo-redundant, compliant |
| Storage (Reference) | PostgreSQL | 🟢 High | NEW; structured data for frameworks, platforms, etc. |
| Secrets | Azure Key Vault + Managed Identity | 🟢 High | UPGRADED from env vars; enterprise-grade security |
| Backend | Azure Container Apps + FastAPI | 🟢 High | UPGRADED from Docker Compose; serverless, auto-scale |
| Frontend | Azure Static Web Apps + Next.js | 🟢 High | UPGRADED from Streamlit; better UX, global CDN |
| CI/CD | GitHub Enterprise + GitHub Actions | 🟢 High | NEW; integrated with Azure for automated deployment |
| Content Safety | Azure Content Moderator | 🟢 High | NEW; compliance requirement for user-generated content |
| Monitoring | Application Insights + Log Analytics | 🟢 High | NEW; distributed tracing, cost tracking, anomaly detection |
| Disaster Recovery | Azure Backup + Geo-Redundancy | 🟢 High | NEW; RTO < 1h, RPO < 24h, cross-region failover |
| Infrastructure | Azure Bicep + GitHub Actions | 🟢 High | NEW; version-controlled, repeatable deployments |
| Testing | Unit + Integration + Contract | 🟢 High | Unchanged; mocking Azure services for cost efficiency |*/span*

---

## Next Phase: Phase 1 Design

✅ **All clarifications resolved.**  
✅ **No blocking ambiguities.**  
✅ **Ready to proceed to Phase 1** (data model, contracts, quickstart).

**Phase 1 Deliverables**:
- `data-model.md`: Entity relationships, session flow
- `contracts/`: Agent I/O schemas, API endpoints
- `quickstart.md`: Local dev setup, first content session walkthrough
