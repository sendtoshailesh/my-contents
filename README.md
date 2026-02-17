# 🎨 Personal AI Content Studio - MVP v0.1.0

A local-first platform for generating **fact-checked, multi-platform content** with framework-driven storytelling.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- SQLite (included with Python)
- API keys for LLM services (OpenAI/Claude) and Bing Search API

### Installation

```bash
# 1. Clone and navigate to project
cd /Users/shaileshmishra/my-docs/my-proj/my-contents

# 2. Create virtual environment  
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
# Create ~/.content-studio/secrets.json or use keyring
# See HYBRID_SECRETS_QUICK_START.md for details
```

### Running the Application

```bash
# Terminal 1: Start backend API (runs on localhost:8000)
python backend/main.py

# Terminal 2: Start frontend UI (runs on localhost:8501)
streamlit run frontend/Home.py
```

Access the application at: **http://localhost:8501**

---

## 📋 Features

### ✨ Core Workflow

1. **Create Session**: Submit a topic or URL
2. **Approve Outline**: System generates outline with web research validation
3. **Select Framework**: Choose from 6 storytelling frameworks (TED Talk, Hero's Journey, etc.)
4. **Generate Content**: Create multi-platform content with visual plans
5. **Adapt Platforms**: Generate platform-specific versions (LinkedIn, Twitter, Reddit, Medium, Substack, Instagram)
6. **Iterate & Refine**: Collect feedback and regenerate until satisfied
7. **Complete**: Mark as done with "ok and good" phrase

### 🔍 Smart Features

- **Web-based Fact Validation**: 70% confidence threshold for outline approval
- **Multi-Platform Adaptation**: Automatic content reformatting for 6 major platforms
- **Visual Plan Generation**: Mermaid diagrams for complex topics
- **Session Management**: Auto-cleanup every 30 days, max 10 active sessions
- **Local Privacy**: All data stays in `~/.content-studio/sessions.db`
- **Iteration Tracking**: Full feedback loop with version history

---

## 📁 Project Structure

```
├── backend/                  # FastAPI backend
│   ├── main.py             # Server entry point (localhost:8000)
│   ├── api/
│   │   ├── routes.py       # All API endpoints
│   │   └── schemas.py      # Request/response models
│   ├── models/
│   │   └── models.py       # SQLAlchemy ORM definitions
│   ├── agents/             # LLM agent implementations
│   │   ├── content_agent.py
│   │   ├── platform_agent.py
│   │   ├── iteration_handler.py
│   │   └── ...
│   ├── utils/
│   │   ├── logger.py       # Logging configuration
│   │   └── reference_data.py
│   └── orchestration/
│       └── state_graph.py  # Multi-step workflow
├── frontend/               # Streamlit UI
│   ├── Home.py            # Main landing page
│   ├── pages/
│   │   ├── 1_New_Session.py      # Create sessions
│   │   ├── 2_History.py          # View/manage sessions
│   │   └── 3_Settings.py         # Configuration & preferences
│   └── components/        # Reusable UI components
├── services/              # Service layer
│   ├── framework_engine.py
│   ├── llm_service.py
│   └── search_service.py
├── docs/                  # Documentation
├── specs/                 # Specification documents
└── tests/                 # Test suite
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```env
# LLM Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Search Configuration  
BING_SEARCH_API_KEY=...

# Database (default is ~/.content-studio/sessions.db)
DATABASE_URL=sqlite:///~/.content-studio/sessions.db

# Server
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

### API Keys (Secure Storage)

For macOS:
```bash
# Store in Keychain (automatic via code)
security add-generic-password -s openai -a $USER -w your_api_key
```

For Windows:
```powershell
# Store in Credential Manager (automatic via code)
cmdkey /add:openai /user:$env:USERNAME /pass:your_api_key
```

---

## 📚 API Documentation

### Session Endpoints

```
POST   /api/sessions                    Create new session
GET    /api/sessions                    List all sessions (max 10)
GET    /api/sessions/{id}              Get session details
DELETE /api/sessions/{id}              Delete session
POST   /api/sessions/{id}/export       Export session as JSON
```

### Content Endpoints

```
GET    /api/sessions/{id}/outline      Get outline
POST   /api/sessions/{id}/approve      Approve outline
GET    /api/sessions/{id}/validation   Get validation report
GET    /api/frameworks                 List frameworks
POST   /api/sessions/{id}/framework    Select framework
POST   /api/sessions/{id}/content      Generate content
```

### Platform & Iteration

```
POST   /api/sessions/{id}/platforms    Generate platform versions
POST   /api/sessions/{id}/iterate      Process feedback
POST   /api/sessions/{id}/complete     Mark complete
```

### Management

```
POST   /api/sessions/cleanup/abandoned Delete abandoned sessions
POST   /api/sessions/cleanup/old       Delete old sessions
POST   /api/sessions/backup            Backup all sessions
POST   /api/health                     Health check
```

---

## 🗄️ Database Schema

### Core Tables

- **sessions**: Active workflows
- **outlines**: Generated topic structures  
- **content_drafts**: Narrative drafts
- **platform_versions**: Platform-specific adaptations
- **iteration_feedback**: User feedback and refinements
- **validation_reports**: Web research results

### Reference Tables

- **frameworks**: Storytelling templates
- **platforms**: Distribution targets
- **focus_areas**: Topic classifications
- **visual_types**: Visual element types

Auto-created at `~/.content-studio/sessions.db` on first startup.

---

## 🧪 Testing

```bash
# Run full test suite
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest --cov=backend tests/
```

---

## 📊 Monitoring & Logs

Logs are stored in `~/.content-studio/`:

- `app.log` - Backend server logs  
- `streamlit.log` - Frontend logs

View logs in real-time:
```bash
tail -f ~/.content-studio/app.log
```

---

## 🐛 Troubleshooting

### Backend Connection Error
```
Error: connection refused on localhost:8000
→ Solution: Ensure backend is running (python backend/main.py)
```

### API Key Not Working
```
Error: 401 Unauthorized
→ Solution: Check API keys in Settings (tab 1)
              Verify keys are valid in service dashboards
```

### Sessions Not Loading
```
Error: No sessions found
→ Solution: Create a new session (New Session → Submit topic)
            Wait for outline generation (~1-2 minutes)
```

### Outline Rejected  
```
Status: Confidence < 70%
→ Solution: Try more specific topic
            Include concrete details
            Reference established concepts
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

### Local Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt  # if available

# Run linting
flake8 backend/ frontend/ --max-line-length=100

# Format code
black backend/ frontend/

# Type checking
mypy backend/ --ignore-missing-imports
```

---

## 📝 Documentation

- **HYBRID_SECRETS_QUICK_START.md** - Secure API key management
- **IMPLEMENTATION_PROGRESS.md** - Development phase tracking
- **specs/** - Detailed specifications and architecture
- **docs/SEARCH_SERVICE_IMPLEMENTATION.md** - Search service details

---

## 📜 License

Internal Use Only - All rights reserved

---

## 🙋 Support

For questions or issues:
1. Check troubleshooting section above
2. Review logs in `~/.content-studio/`
3. Check `/docs/` and `/specs/` for detailed guides
4. Contact internal support team

---

## 🎯 Roadmap

### Phase 6 (Current - Polish & Cross-Cutting)
✅ Session history display and management  
✅ Settings & configuration UI  
✅ Error handling enhancements  
✅ Auto-cleanup and backups  
✅ Documentation

### Future Phases
- 🔄 Session sharing & collaboration
- 📊 Analytics dashboard
- 🔌 Plugin system for custom agents
- 🌐 Multi-user support
- ☁️ Cloud sync option

---

**Last Updated**: February 16, 2026  
**Version**: 0.1.0 MVP  
**Status**: Phase 6 In Progress
