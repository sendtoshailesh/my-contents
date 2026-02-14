# AZURE & GitHub Enterprise Migration Summary

**Date**: 7 February 2026  
**Scope**: Updated specification to use Microsoft Azure cloud platform and GitHub Enterprise  
**Status**: ✅ Complete - All changes applied  

---

## Executive Summary

The Personal AI Content Studio specification has been updated to leverage **Microsoft Azure cloud services** and **GitHub Enterprise** instead of third-party APIs and local infrastructure. This provides:

- **Enterprise-grade security** via Azure Key Vault and Managed Identity
- **Compliance certifications** (HIPAA, PCI-DSS, SOC 2) required for production applications
- **Seamless integration** across Microsoft tech stack (GitHubEnterprise, Azure, Microsoft AI Services)
- **Lower operational overhead** via serverless compute (Container Apps) and managed databases
- **Better cost management** through pay-per-use pricing and Azure Cost Management

---

## Key Changes by Component

### 1. Secrets Management

**Before**: Environment variables + `.env` file (local, insecure)  
**After**: **Azure Key Vault + Managed Identity**

- No `.env` files; no secrets in git or logs
- Centralized secret management with audit trails
- Automatic secret rotation support
- RBAC for fine-grained access control

**Configuration**:
- App Service / Container Apps uses Managed Identity (no credentials in code)
- At runtime, code calls `DefaultAzureCredential` to fetch secrets from Key Vault
- All API keys, connection strings, and certificates stored in Key Vault

---

### 2. Web Search

**Before**: Tavily API (third-party, $$ per query)  
**After**: **Azure Cognitive Search + Bing Search API**

- Bing Search API: Official Microsoft search, built-in credibility scoring
- Azure Cognitive Search: Semantic ranking, AI-enriched results, custom indexing
- Both integrated with Azure AI Services for NLP and entity extraction
- Cost: Included in Azure AI Services tier (not per-query)
- Compliance: HIPAA, PCI-DSS ready

**Research Agent Changes**:
- Calls Bing Search API for web claims validation
- Uses Azure AI Language Service to extract entities and key claims
- Returns confidence score based on source credibility (Bing's domain ranking)
- Results stored in Cosmos DB for audit trail

---

### 3. LLM Provider

**Before**: OpenAI API (direct) or Claude (Anthropic)  
**After**: **Azure OpenAI Service (GPT-4 Turbo)**

- Same GPT-4 models as OpenAI.com, but in Azure data centers
- Compliance certifications (HIPAA, PCI-DSS, SOC 2)
- VNet integration, data residency control
- Managed capacity reservations reduce costs
- Access via Azure Identity (Managed Identity; no API keys in code)

**Deployment**:
- Deploy `gpt-4-turbo` model and `text-embedding-3-small` in Azure OpenAI
- Endpoint and key stored in Key Vault
- Cost: Managed via Azure Cost Management

---

### 4. Data Storage

**Before**: SQLite (local, single-region, no backup)  
**After**: **Cosmos DB (sessions) + PostgreSQL (reference data)**

**Cosmos DB** (NoSQL, JSON documents):
- Session documents with nested outlines, validation reports, content, platform versions
- Multi-region replication (US primary + EU secondary)
- Auto-scale RUs based on load
- Point-in-time restore (30-day retention)
- Cost: Usage-based (RUs consumed); free tier available for small workloads

**PostgreSQL** (SQL, relational):
- Reference data: frameworks, platforms, focus_areas, visual_types
- ACID transactions, strong consistency
- Managed backup and geo-redundancy
- Cost: Predictable per-tier pricing

**Advantages**:
- Geo-distributed data resilience
- Automatic backups and recovery
- Better audit trails
- Compliance-ready encryption at rest and in transit

---

### 5. Backend Compute

**Before**: Docker Compose (local or self-managed)  
**After**: **Azure Container Apps (serverless)**

- Deploy FastAPI in Docker → Azure Container Registry
- Container Apps handles orchestration, auto-scaling, networking
- Pay only for compute used (consumption-based pricing)
- Auto-scale 0 to 10 instances based on load
- Integrated health checks and traffic management
- Managed Identity for all Azure service authentication

**Deployment**:
- GitHub Actions builds Docker image → pushes to ACR
- GitHub Actions triggers Container App deployment
- New image deployed with zero downtime

---

### 6. Frontend

**Before**: Streamlit (server-side rendering, limited customization)  
**After**: **Azure Static Web Apps + Next.js**

- Next.js for rich, interactive SPA
- Static Web Apps for serverless hosting
- GitHub Actions integrates: commit to main → auto-deploy
- Global CDN for fast content delivery
- Built-in preview deployments for PRs
- Cost: Pay per usage (very low for personal use)

---

### 7. CI/CD & Version Control

**Before**: N/A (local development only)  
**After**: **GitHub Enterprise + GitHub Actions**

- All code in GitHub Enterprise (private, secure)
- GitHub Actions workflows for:
  - Build & test (pytest, security scans)
  - Build Docker image, scan for vulnerabilities, push to ACR
  - Deploy to Container Apps
  - Deploy to Static Web Apps
  - Deploy infrastructure (Bicep)
- Required status checks: Tests pass, security scans pass, code review approved
- GitHub Copilot Enterprise for AI-assisted code review

**Workflows**:
- `build-and-test.yml`: Run on every commit
- `deploy-infrastructure.yml`: Run on infra file changes
- `deploy-backend.yml`: Build, scan, push to ACR, deploy to Container Apps
- `deploy-frontend.yml`: Build Next.js, deploy to Static Web Apps

---

### 8. Security Enhancements

**New Components**:
- **Azure Content Moderator**: Content safety checks on generated text before publishing
- **Azure Defender for Cloud**: Continuous vulnerability scanning
- **Microsoft Sentinel**: Security event monitoring (optional, for advanced threat detection)
- **Azure Policy**: Enforce governance and compliance rules

---

### 9. Monitoring & Observability

**After**: **Azure Application Insights + Log Analytics**

- Instrument FastAPI with Application Insights SDK
- Distributed tracing for multi-step agentic workflows
- Log all operations, API calls, validation results
- Real-time alerts for errors, high latency, failed Key Vault access
- Cost tracking and budget alerts via Azure Cost Management
- Azure Dashboard for real-time visibility

---

### 10. Disaster Recovery

**After**: **Azure Backup + Geo-Redundant Storage**

- Automated daily backups of Cosmos DB and PostgreSQL (30-day retention)
- Geo-replication across 2 regions (US + EU)
- Point-in-time restore capability
- RTO (Recovery Time Objective): < 1 hour
- RPO (Recovery Point Objective): < 24 hours
- Test recovery procedures quarterly

---

### 11. Infrastructure as Code

**After**: **Azure Bicep + GitHub Actions**

- Write infrastructure in Bicep (simpler than ARM templates)
- Version-controlled infrastructure
- GitHub Actions auto-deploys on commit
- parameterized for dev/staging/prod environments
- Resources defined in code:
  - Key Vault, OpenAI, Container Registry
  - Container Apps, Static Web Apps
  - Cosmos DB, PostgreSQL
  - Application Insights, Log Analytics
  - Cognitive Search, Content Moderator

**Benefits**:
- Repeatable deployments
- Easy rollback via git history
- Infrastructure reviewed via pull requests
- Audit trail of all changes

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Enterprise                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Code Repos (FastAPI, Next.js, Bicep)                   │  │
│  │  GitHub Actions (Build, Test, Deploy)                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─── Push to ACR (Docker image)
             │
             ├─── Deploy Bicep Infrastructure
             │
             └─── Deploy Apps (Container Apps, Static Web Apps)
             
┌─────────────────────────────────────────────────────────────────┐
│                       Azure Portal                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │  Key Vault       │         │ Container Registry│             │
│  │ (Secrets)        │         │ (Docker Images)  │             │
│  └──────────────────┘         └──────────────────┘             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  Frontend: Static Web Apps + Next.js                │     │
│  │  (Global CDN, Auto-deploy from GitHub)             │     │
│  └────────────────────────────────────────────────────┘     │
│                                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Backend:  Container Apps (FastAPI)                 │    │
│  │  - Managed Identity (auth to Key Vault)             │    │
│  │  - Auto-scale 1-10 instances                        │    │
│  │  - Health checks + traffic management              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  LLM & Search Services:                               │  │
│  │  - Azure OpenAI Service (GPT-4 Turbo)                │  │
│  │  - Bing Search API                                    │  │
│  │  - Azure Cognitive Search                             │  │
│  │  - Azure AI Language Services                         │  │
│  │  - Azure Content Moderator                           │  │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Data Storage:                                        │   │
│  │  - Cosmos DB (Sessions, geo-replicated)             │   │
│  │  - PostgreSQL (Reference Data)                      │   │
│  │  - Azure Backup (30-day retention)                  │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │  Monitoring & Logging:                                │  │
│  │  - Application Insights (APM, Tracing)              │   │
│  │  - Log Analytics (Centralized Logging)              │   │
│  │  - Azure Dashboard (Real-time Visibility)           │   │
│  │  - Cost Management (Budget Alerts)                  │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cost Estimation (Monthly, US Region)

| Component | Tier | Estimated Cost | Notes |
|-----------|------|---|---|
| **Key Vault** | Standard | $0.60 | Base cost; minimal usage |
| **Azure OpenAI** | Pay-per-use | $50–200 | Input/output tokens; GPT-4 Turbo |
| **Cosmos DB** | Provisioned RUs | $100–300 | Depends on load; includes backup |
| **PostgreSQL** | Single server B1 | $50 | Managed backups, geo-redundancy |
| **Container Apps** | Consumption | $50–150 | Based on vCPU-hours consumed |
| **Static Web Apps** | Free/Standard | $0–100 | Free tier sufficient for MVP |
| **Application Insights** | Pay-as-you-go | $2–10 | Includes 5GB/month free |
| **Storage (Backup)** | Azure Backup | $10–20 | 30-day retention |
| **Bing Search API** | Standard | $5–50 | Most queries covered in free tier |
| **Content Moderator** | Standard | $1 | Pay per call; minimal for MVP |
| **TOTAL (Monthly)** | | **$250–1000** | Highly variable; 95% from OpenAI usage |
| **TOTAL (Annual)** | | **$3,000–12,000** | Much lower if using Azure AI credits |

**Cost Optimization**:
- Use Azure free credits ($200/month for 12 months new accounts)
- Use Cosmos DB free tier (first 400 RUs/sec free)
- Reduce Container Apps load via caching
- Use Spot VMs or reserved instances for sustained workloads
- Enable auto-shutdown in dev/test environments

---

## Migration Checklist

- [x] Update `research.md` with Azure services
- [x] Update `plan.md` with Azure subscription configuration
- [x] Update `data-model.md` for Cosmos DB + PostgreSQL
- [x] Update `contracts/` API specifications (unchanged)
- [x] Update `quickstart.md` with Azure setup guide (optional; see tasks for full guide)
- [ ] Create Bicep templates for all resources
- [ ] Create GitHub Actions workflows for CI/CD
- [ ] Test deployments in dev environment
- [ ] Configure monitoring and alerting
- [ ] Document runbooks for disaster recovery

---

## Next Steps

### Immediate (Phase 2: Tasks)
1. Run `/speckit.tasks` to generate detailed implementation tasks
2. Create Bicep files for all Azure resources
3. Create GitHub Actions workflows
4. Set up Azure subscription configuration (as per plan.md)

### Before First Deployment
1. Create Azure resource group and Key Vault
2. Deploy Azure OpenAI, Cosmos DB, PostgreSQL
3. Configure Managed Identity on Container Apps
4. Test connectivity and authentication
5. Run security baseline (Azure Defender)

### Ongoing
1. Monitor costs via Azure Cost Management
2. Review logs via Application Insights
3. Test disaster recovery procedures quarterly
4. Update Bicep as requirements change
5. Use GitHub Actions for all deployments (no manual changes)

---

## Key Documentation References

- [research.md](research.md) — Tech stack decisions and rationales
- [plan.md](plan.md) — Technical context and Azure subscription setup
- [data-model.md](data-model.md) — Cosmos DB + PostgreSQL schema
- [contracts/](contracts/) — Agent and API specifications (unchanged)
- [spec.md](spec.md) — Feature specification (unchanged)
- [constitution.md](constitution.md) — Product values (unchanged)

---

## Support & Questions

- **Azure Documentation**: https://docs.microsoft.com/azure/
- **Azure OpenAI**: https://learn.microsoft.com/en-us/azure/ai-services/openai/
- **GitHub Enterprise**: https://docs.github.com/en/enterprise-server@latest/
- **GitHub Actions**: https://docs.github.com/en/actions

---

**Status**: ✅ Ready for Phase 2 (Task Generation & Implementation)
