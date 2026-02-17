# 🚀 Complete Step-by-Step Guide to Run the App

**Total Setup Time**: 30-45 minutes  
**Complexity**: Easy  
**Prerequisites**: Python 3.10+, API keys

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Environment Setup](#step-1-environment-setup)
3. [Step 2: Install Dependencies](#step-2-install-dependencies)
4. [Step 3: Configure Secrets](#step-3-configure-secrets)
5. [Step 4: Initialize Database](#step-4-initialize-database)
6. [Step 5: Start Backend Server](#step-5-start-backend-server)
7. [Step 6: Start Frontend App](#step-6-start-frontend-app)
8. [Step 7: Test the Full Workflow](#step-7-test-the-full-workflow)
9. [Understanding Mock vs Real Implementations](#understanding-mock-vs-real-implementations)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### What You Need

- **Python 3.10+** installed (verify: `python3 --version`)
- **Terminal/Command line** access
- **2 Terminal windows** open (backend + frontend run simultaneously)
- **~30 minutes** free time

### API Keys (Required)

You'll need **2 API keys minimum**:

1. **Azure OpenAI or OpenAI GPT-4**
   - Option A: Azure OpenAI (Recommended)
     - Go to: https://portal.azure.com → Azure OpenAI → Create resource
     - Cost: ~$20-50/month for MVP
   
   - Option B: OpenAI direct
     - Go to: https://platform.openai.com → Billing → Add payment method
     - Cost: ~$20-50/month for MVP

2. **Bing Search API**
   - Go to: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
   - Click "Get free trial" or subscribe
   - Cost: ~$5-15/month for MVP

### Optional API Keys

- **Anthropic Claude** (optional): https://console.anthropic.com
- **Ollama** (optional, local): https://ollama.ai

---

## Step 1: Environment Setup

### 1.1 Navigate to Project Directory

```bash
cd /Users/shaileshmishra/my-docs/my-proj/my-contents
```

Verify you see these folders:
```
backend/
frontend/
services/
scripts/
specs/
tests/
```

### 1.2 Create Python Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**Verify activation** - You should see `(venv)` at the start of your terminal line:
```
(venv) $ echo "Ready!"
```

### 1.3 Upgrade pip (Optional but Recommended)

```bash
pip install --upgrade pip
```

---

## Step 2: Install Dependencies

### 2.1 Install All Requirements

```bash
pip install -r requirements.txt
```

This installs ~40 packages including:
- **fastapi** - Backend web framework
- **streamlit** - Frontend UI framework
- **langchain** - LLM orchestration
- **sqlalchemy** - Database ORM
- **keyring** - Secure credential storage
- **openai, anthropic** - LLM APIs
- **requests** - HTTP library for search API
- And more...

**Expected time**: 3-5 minutes

**Verify installation**:
```bash
pip list | grep -E "fastapi|streamlit|langchain|sqlalchemy"
```

You should see versions listed.

---

## Step 3: Configure Secrets

### 3.1 Run Interactive Setup Script

```bash
python scripts/setup_secrets.py
```

This will prompt you for:

```
Enter Azure OpenAI API key (or press Enter to skip): [YOUR_KEY_HERE]
Enter Bing Search API key (or press Enter to skip): [YOUR_KEY_HERE]
Enter Anthropic API key (optional, press Enter to skip): [SKIP]
Enter Ollama base URL (optional, default: http://localhost:11434): [SKIP]
```

**Where to get these keys:**

| Key | Get It From | Time |
|-----|------------|------|
| Azure OpenAI | https://portal.azure.com (search "Azure OpenAI") | 5 min |
| Bing Search | https://www.bingapis.com/products/search | 2 min |
| Anthropic | https://console.anthropic.com (optional) | 2 min |

### 3.2 Verify Secrets Were Saved

**macOS**: Open Keychain Access
```bash
# Or just check in terminal:
python -c "from services.secrets_service import get_secrets_service; s = get_secrets_service(); print('✓ Secrets loaded' if s.get('azure-openai-key') else '✗ Missing key')"
```

**Windows**: Open Credential Manager
- Settings → Accounts → Manage credentials → Generic credentials

---

## Step 4: Initialize Database

### 4.1 Create SQLite Database

```bash
python scripts/setup_db.py
```

**Expected output:**
```
✅ Database initialized at: ~/.content-studio/sessions.db
✅ Schema created with 7 tables
✅ Seed data added
```

### 4.2 Verify Database

```bash
ls -lh ~/.content-studio/sessions.db
```

You should see a file ~100KB.

---

## Step 5: Start Backend Server

### 5.1 Terminal 1: Start FastAPI Backend

**In Terminal 1 (with virtual environment activated):**

```bash
python backend/main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Press CTRL+C to quit
```

**Wait for**:
```
✅ API routes registered
✅ Database initialized
✅ Startup complete - X active sessions
```

### 5.2 Test Backend Health

**In a new terminal (Terminal 3):**

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-16T...",
  "version": "0.1.0"
}
```

**✅ Backend is running!**

---

## Step 6: Start Frontend App

### 6.1 Terminal 2: Start Streamlit Frontend

**In Terminal 2 (with virtual environment activated):**

```bash
cd /Users/shaileshmishra/my-docs/my-proj/my-contents
streamlit run frontend/Home.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 6.2 Open Browser

- Go to: **http://localhost:8501**
- You should see the app with 3 pages on the left sidebar

**✅ Frontend is running!**

---

## Step 7: Test the Full Workflow

### Test Flow: Topic → Outline → Framework → Content → Platforms → Complete

### 7.1 Create a New Session (Page 1: New Session)

1. **Click "New Session"** in sidebar
2. **Enter a topic**: e.g., "How AI is transforming healthcare"
3. **Click "Extract Topic"** button
4. **Review the extracted info**:
   - ✅ Theme extracted
   - ✅ Audience identified
   - ✅ Focus area classified
   - ✅ Confidence score shown

**What's happening**:
- ✅ **REAL**: InputAgent uses actual LLM to classify topic
- ⚠️  **HYBRID**: Falls back to mock if API key missing
- 📍 **Location**: `backend/agents/input_agent.py` lines 37-42

### 7.2 Generate Outline (Same Page)

1. **Click "Generate Outline"** button
2. **Wait for processing** (30-45 seconds typically)
3. **Review generated outline**:
   - ✅ 5-section structure with titles
   - ✅ Content angle described
   - ✅ Target audience set
   - ✅ Difficulty level assigned

**What's happening**:
- ✅ **REAL**: ReasoningAgent creates actual outline using LLM
- ✅ **REAL**: ResearchAgent validates with actual Bing Search API
- ✅ **REAL**: Claims scored for credibility (70% threshold)
- 📍 **Location**: `backend/agents/reasoning_agent.py`, `backend/agents/research_agent.py`

### 7.3 Approve Outline

1. **Review the validation results**:
   - Confidence score
   - Sources found
   - Claims verified
2. **Click "Approve Outline"** button

**What's happening**:
- ✅ **REAL**: Validation checks actual Bing search results
- ✅ **REAL**: Credibility scoring uses real algorithms
- 📍 **Location**: `backend/agents/research_agent.py` lines 50-120

### 7.4 Select Framework (Page 2-like interface)

1. **Wait for framework recommendations** (5-10 seconds)
2. **See 6 framework options**:
   - TED Talk Structure
   - Hero's Journey
   - Problem-Solution-Benefit
   - Before-After-Bridge
   - SCQA (Situation-Complication-Question-Answer)
   - Learn-Apply-Improve

3. **Select one** (e.g., "Hero's Journey")
4. **Opt-in for visuals** (recommended checkbox)

**What's happening**:
- ✅ **REAL**: Framework recommendation based on outline shape
- ✅ **REAL**: StorytellingAgent generates actual visual plans
- 🎨 **REAL**: Mermaid diagrams created for content
- 📍 **Location**: `backend/agents/storytelling_agent.py`

### 7.5 Generate Content

1. **Click "Generate Content"** button
2. **Wait for generation** (60-90 seconds)
3. **Review the generated content**:
   - ✅ Full markdown body text
   - ✅ Content structure matches framework
   - ✅ Mermaid diagrams embedded (2-3 visualizations)

**What's happening**:
- ✅ **REAL**: ContentAgent uses GPT-4 to write full article
- ✅ **REAL**: Mermaid code generated dynamically
- 📍 **Location**: `backend/agents/content_agent.py`

### 7.6 Generate Platform Versions

1. **Click "Generate Platforms"** button
2. **Wait for processing** (2-3 minutes for all 6)
3. **See 6 platform versions**:
   - **LinkedIn**: Professional 1500+ word article
   - **Twitter**: 5-7 tweets with threading
   - **Reddit**: Markdown with subreddits
   - **Medium**: Blog post format
   - **Substack**: Newsletter format
   - **Instagram**: Captions + hashtags

**What's happening**:
- ✅ **REAL**: PlatformAgent uses Llama 3.1 to generate each version
- ✅ **REAL**: Each platform optimized for unique audiences
- ✅ **REAL**: Uses actual LLM calls for each platform
- 📍 **Location**: `backend/agents/platform_agent.py` lines 50-250

### 7.7 Iterate & Refine

1. **Select platform** (e.g., LinkedIn version)
2. **Check feedback boxes**:
   - [ ] Make more conversational
   - [ ] Add more examples
   - [ ] Increase technical depth
   - [ ] Add humor
   - [ ] Improve structure
3. **Add custom feedback** in text box
4. **Click "Regenerate"** button
5. **View updated version** (30 seconds)

**What's happening**:
- ✅ **REAL**: IterationHandler processes all 7 feedback areas
- ✅ **REAL**: Detects "ok and good" completion phrase
- ✅ **REAL**: Regenerates only affected components
- 📍 **Location**: `backend/agents/iteration_handler.py` lines 100-300

### 7.8 Complete Session

1. **After satisfied with content**
2. **Type in final feedback box**: "ok and good"
3. **Click "Complete Session"**
4. **Session marked as complete** ✅

**What's happening**:
- ✅ **REAL**: Session status updated in database
- ✅ **REAL**: Full session exported to history
- 📍 **Location**: `backend/agents/iteration_handler.py` lines 380-420

### 7.9 View Session History (Page 2: History)

1. **Click "History"** in sidebar
2. **See your completed session**
3. **Options**:
   - 📖 **Resume**: Open previous session
   - 💾 **Export**: Save as JSON/Markdown
   - 🗑️ **Delete**: Remove session

**What's happening**:
- ✅ **REAL**: Queries SQLAlchemy models
- ✅ **REAL**: Loads full session with all history
- 📍 **Location**: `frontend/pages/2_History.py`, `backend/api/routes.py` lines 200-250

---

## Understanding Mock vs Real Implementations

### Summary Table

| Component | Status | Details | Location |
|-----------|--------|---------|----------|
| **Input Agent** | ✅ REAL (with mock fallback) | Uses LLM if API key available, falls back to mock | `input_agent.py` lines 37-90 |
| **Reasoning Agent** | ✅ REAL (with mock fallback) | Generates outlines using GPT-4/Claude | `reasoning_agent.py` |
| **Research Agent** | ✅ REAL | Uses actual Bing Search API | `research_agent.py` lines 50-120 |
| **Storytelling Agent** | ✅ REAL | Framework mapping + visual generation | `storytelling_agent.py` |
| **Content Agent** | ✅ REAL (with mock fallback) | Generates full content using LLM | `content_agent.py` lines 60-110 |
| **Platform Agent** | ✅ REAL | 6 platform generators using LLM | `platform_agent.py` lines 50-250 |
| **Iteration Handler** | ✅ REAL | Processes feedback + regenerates | `iteration_handler.py` |

---

### 🎭 When Does It Use Mock?

Mock agents are used **ONLY as fallback** when:

1. **API Key Missing**
   - No Azure OpenAI key provided
   - User skipped key configuration
   - Key expired or invalid

2. **API Failure**
   - Network timeout
   - Rate limit exceeded
   - API service down

3. **Deliberate Debug Mode**
   - You explicitly set `use_mock = True` in code
   - Testing without running API calls

### Example: Input Agent Fallback

```python
# In backend/agents/input_agent.py lines 37-42
try:
    self.llm = ModelRouter()           # Try to load real LLM
    self.use_mock = False
except Exception as e:
    logger.warning(f"Failed to initialize LLM: {e}")
    self.llm = None
    self.use_mock = True               # Fall back to mock
```

**When you see in logs:**
```
⚠️  Failed to initialize LLM: Azure OpenAI API key not found
🎭 Using mock agent
```

This means you need to provide API keys via `setup_secrets.py`.

---

### How to Verify You're Using Real Implementations

#### 1. Check the Logs

**Terminal 1 (Backend)** shows:
```
✓ InputAgent initialized (mock=False)      # ✅ Real
✓ InputAgent initialized (mock=True)       # ⚠️  Mock fallback

🔍 Extracting topic info from: AI in healthcare
→ Calling LLM for classification               # ✅ Real
🎭 Using mock agent                           # ⚠️  Mock
```

#### 2. Check Response Times

- **Real LLM**: 10-30 seconds (network + processing)
- **Mock agent**: <1 second (instant)

#### 3. Check Output Quality

- **Real LLM**: Unique, context-aware responses
- **Mock agent**: Generic placeholder text

---

### Mock Agents Available

These are used ONLY if API keys fail:

#### MockInputAgent
- **File**: `backend/agents/mock_agents.py` lines 10-27
- **Output**: Generic topic classification
- **Used when**: Azure OpenAI key missing

#### MockReasoningAgent
- **File**: `backend/agents/mock_agents.py` lines 30-65
- **Output**: 5-section template outline
- **Used when**: Azure OpenAI key missing

#### MockResearchAgent
- **File**: `backend/agents/mock_agents.py` lines 68-90
- **Output**: 85% confidence, 12 sources
- **Used when**: Bing Search API missing or down

#### MockStorytellingAgent
- **File**: `backend/agents/mock_agents.py` lines 93-135
- **Output**: Framework mapping + 2 Mermaid diagrams
- **Used when**: Azure OpenAI key missing

#### MockContentAgent
- **File**: `backend/agents/mock_agents.py` lines 138-200
- **Output**: Template content with sections
- **Used when**: Azure OpenAI key missing

---

## Troubleshooting

### Problem 1: "Secret not found" Error

**Error message:**
```
❌ Azure OpenAI API key not found in keyring
🎭 Falling back to mock agent
```

**Solution - Run Setup Again:**
```bash
python scripts/setup_secrets.py
```

Then:
1. Enter your Azure OpenAI API key
2. Enter your Bing Search API key
3. Press Enter to skip optional keys
4. Restart backend

### Problem 2: Backend Won't Start

**Error message:**
```
Traceback (most recent call last):
  File "backend/main.py", line 160, in <module>
    uvicorn.run(...)
KeyError: 'azure-openai-key'
```

**Solution:**
1. Make sure secrets are configured: `python scripts/setup_secrets.py`
2. Make sure database is initialized: `python scripts/setup_db.py`
3. Check Python version: `python3 --version` (needs 3.10+)

### Problem 3: Frontend Can't Connect to Backend

**Error message:**
```
❌ Failed to connect to http://localhost:8000/health
```

**Solution:**
1. Check Terminal 1: Is backend running? (should see "Uvicorn running")
2. Test manually: `curl http://localhost:8000/health`
3. Check port not in use: `lsof -i :8000`
4. Restart both: Kill Terminal 1, run `python backend/main.py` again

### Problem 4: Streamlit App Crashes

**Error message:**
```
StreamlitAPIException: Session state is not available
```

**Solution:**
1. Refresh browser: `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows)
2. Clear cache: Click "Always rerun" option
3. Restart frontend: Kill Terminal 2, run `streamlit run frontend/Home.py`

### Problem 5: API Calls Are Very Slow

**Observation:**
```
Takes 2+ minutes to generate content
```

**This is NORMAL:**
- First LLM call: 30-45 sec (research + classification)
- Outline generation: 20-30 sec
- Framework selection: 5-10 sec
- Content generation: 45-90 sec (large model)
- **Total workflow: 2-4 minutes** ✅

**If slower than this**, try:
1. Restart backend
2. Check your internet connection
3. Try a shorter topic (fewer words = faster)

### Problem 6: "Confirmation score 0" Messages

**What it means:**
```
⚠️ Research agent confidence: 0 (no sources found)
```

**Why:**
- Topic too niche (no Wikipedia/news articles)
- Bing API rate limited
- Topic name too vague

**Solution:**
1. Use clearer topic: "AI in healthcare" instead of "AI stuff"
2. Restart backend to reset rate limits
3. Check Bing API quota: https://dev.bingapis.com

---

## Complete Reference

### All 20+ API Endpoints

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/health` | GET | Health check | ✅ Live |
| `/sessions` | POST | Create session | ✅ Real |
| `/sessions/{id}` | GET | Get session details | ✅ Real |
| `/outline` | POST | Generate outline | ✅ Real |
| `/validate` | POST | Validate with search | ✅ Real |
| `/framework` | GET | Get framework options | ✅ Real |
| `/select-framework` | POST | Choose framework | ✅ Real |
| `/content` | POST | Generate content | ✅ Real |
| `/platforms` | POST | Generate all 6 platforms | ✅ Real |
| `/iterate` | POST | Process feedback | ✅ Real |
| `/complete` | POST | Mark session complete | ✅ Real |
| `/sessions/{id}/delete` | DELETE | Delete session | ✅ Real |
| `/cleanup` | POST | Auto-cleanup old | ✅ Real |
| `/export` | GET | Export session | ✅ Real |
| `/resume/{id}` | POST | Resume session | ✅ Real |

---

### Database Schema (7 Tables)

```
Sessions
├── Session (id, topic, status, created_at)
├── Outline (id, session_id, outline_text, angle)
├── ValidationReport (id, session_id, confidence, sources)
├── ContentDraft (id, session_id, framework, content)
├── PlatformVersion (id, content_id, platform, content)
├── IterationFeedback (id, session_id, areas, text)
└── RefData (framework_id, name, templates)
```

---

### Key Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `backend/main.py` | FastAPI app entry | ✅ Complete |
| `backend/api/routes.py` | All 20+ endpoints | ✅ Complete |
| `backend/agents/input_agent.py` | Topic extraction | ✅ Real + Mock fallback |
| `backend/agents/content_agent.py` | Content generation | ✅ Real + Mock fallback |
| `frontend/Home.py` | Navigation | ✅ Complete |
| `frontend/pages/1_New_Session.py` | Workflow UI | ✅ Complete |
| `frontend/pages/2_History.py` | Session history | ✅ Complete |
| `services/llm_service.py` | Multi-model router | ✅ Real |
| `services/search_service.py` | Bing Search API | ✅ Real |

---

## 🎉 You're Ready!

**To run the complete app:**

```bash
# Terminal 1
cd /Users/shaileshmishra/my-docs/my-proj/my-contents
source venv/bin/activate
python backend/main.py

# Terminal 2 (new)
cd /Users/shaileshmishra/my-docs/my-proj/my-contents
source venv/bin/activate
streamlit run frontend/Home.py

# Then open: http://localhost:8501
```

**What to expect:**
- ✅ Full end-to-end workflow working
- ✅ Real LLM + Search API calls
- ✅ Mock fallback if APIs fail
- ✅ 2-4 minute total workflow time
- ✅ All data saved to SQLite database

---

**Next Steps:**
1. Run through the complete workflow once
2. Check logs to verify real LLM calls are being made
3. Try different topics and frameworks
4. Export sessions as JSON/Markdown
5. Read [IMPLEMENTATION_AUDIT.md](IMPLEMENTATION_AUDIT.md) for advanced topics

**Questions?** Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) or [README.md](README.md)
