# ⚡ 5-Minute Quick Start - Copy & Paste Commands

**Total Time**: 30-45 minutes  
**All commands below are ready to copy-paste**

---

## 🚀 The 5-Step Launch Sequence

### Step 1: Clone & Activate (5 min)

```bash
# Navigate to project
cd /Users/shaileshmishra/my-docs/my-proj/my-contents

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) at terminal prompt now
```

### Step 2: Install Dependencies (5 min)

```bash
pip install -r requirements.txt

# Verify (should show versions)
pip list | grep -E "fastapi|streamlit|langchain"
```

### Step 3: Configure Secrets (3 min)

```bash
python scripts/setup_secrets.py

# You'll be prompted:
# Enter Azure OpenAI API key: [PASTE_YOUR_KEY]
# Enter Bing Search API key: [PASTE_YOUR_KEY]
# Optional keys: Just press Enter to skip
```

**Where to get API keys:**
- Azure OpenAI: https://portal.azure.com (search "Azure OpenAI")
- Bing Search: https://www.bingapis.com/products/search

### Step 4: Initialize Database (2 min)

```bash
python scripts/setup_db.py

# Should show:
# ✅ Database initialized at: ~/.content-studio/sessions.db
```

### Step 5: Start the App (2 terminals)

**Terminal 1 - Backend:**
```bash
# Keep virtual environment activated
python backend/main.py

# Should show:
# ✅ Uvicorn running on http://127.0.0.1:8000
# ✅ Database initialized
# ✅ API routes registered
```

**Terminal 2 - Frontend:**
```bash
# NEW terminal, activate venv again
cd /Users/shaileshmishra/my-docs/my-proj/my-contents
source venv/bin/activate

# Start Streamlit
streamlit run frontend/Home.py

# Should show:
# Local URL: http://localhost:8501
```

### Open Browser

Go to: **http://localhost:8501** ✅

---

## 📋 Complete Workflow (One Session)

**This tests ALL functionality end-to-end:**

1. **Click: "New Session"** → Enter topic → Click "Extract Topic" ✅
   - Extracts metadata (audience, intent, focus area)
   - Real LLM call if API key available

2. **Click: "Generate Outline"** → Wait 30 sec → See 5-section outline ✅
   - Real LLM generates structured outline
   - Mock fallback if API missing

3. **Click: "Validate Outline"** → See sources found ✅
   - Real Bing Search API validates claims
   - Shows confidence score (must be >70%)

4. **Click: "Approve"** → Get framework options ✅
   - Shows 6 frameworks: TED Talk, Hero's Journey, etc.

5. **Select framework** → Check "Include visuals" → Click "Next" ✅
   - Framework mapping with Mermaid diagrams

6. **Click: "Generate Content"** → Wait 60-90 sec ✅
   - Full article with visual placeholders
   - 2000-3000 words

7. **Click: "Generate Platforms"** → Wait 2-3 min ✅
   - LinkedIn version (1500+ words)
   - Twitter threads (5-7 tweets)
   - Reddit post (markdown)
   - Medium article
   - Substack newsletter
   - Instagram captions

8. **Click on a platform** → Check feedback boxes → Click "Regenerate" ✅
   - Selects feedback areas
   - Re-runs affected LLM calls
   - Updates just that platform

9. **Type "ok and good"** in feedback box → Click "Complete" ✅
   - System detects completion phrase
   - Marks session done

10. **Click: "History"** → See your session ✅
    - Resume, export, or delete

**Total time**: 5-8 minutes (mostly waiting for LLM) ⏱️

---

## 🧪 Testing (Optional)

```bash
# Run all tests
pytest tests/ -v

# Run specific agent tests
pytest tests/test_agents.py -v

# Run search service tests
pytest tests/test_search_service.py -v

# Run platform generation tests
pytest tests/test_platform_iteration.py -v
```

**Expected**: All 50+ tests pass ✅

---

## 🔍 Verify Everything Works

```bash
# Health check (in new terminal)
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","timestamp":"...","version":"0.1.0"}

# View logs (Terminal 1)
# Should show real LLM calls:
# ✓ InputAgent initialized (mock=False)
# 🔍 Extracting topic info
# ← Response received (1234 tokens)
```

---

## 🎭 Understanding Mock vs Real

### You're Getting REAL Calls When:
```
✓ InputAgent initialized (mock=False)
✓ ReasoningAgent initialized (mock=False)
← Found 42 results from Bing Search       # Real search
✅ Confidence score: 0.85                 # Real validation
Response times: 5-30 seconds per call     # Real LLM speed
```

### You're Getting MOCK (Fallback) When:
```
⚠️  Failed to initialize LLM: API key not found
🎭 Using mock agent
← Found 12 results (mock)                 # Hardcoded mock
Response times: <1 second                 # Instant (fake)
Content is generic template               # Not context-aware
```

**To fix mock fallback:**
```bash
# Re-run secrets setup
python scripts/setup_secrets.py

# Enter your API keys, then restart backend
# Ctrl+C in Terminal 1, then:
python backend/main.py
```

---

## 📊 Real vs Mock Breakdown

| Component | Real | Mock | When Mock Used |
|-----------|------|------|-----------------|
| Input extraction | ✅ LLM | ✅ Template | No API key |
| Outline generation | ✅ LLM | ✅ Template | No API key |
| Web search validation | ✅ Bing API | ✅ Hardcoded | No Bing key |
| Framework mapping | ✅ Logic | ✅ Logic | Never |
| Content generation | ✅ GPT-4 | ✅ Template | No API key |
| Platform generation | ✅ Llama 3.1 | ❌ None | Fails entirely |
| Iteration feedback | ✅ LLM | ❌ None | Fails entirely |

**Bottom line**: Platform & iteration run real only, no mock fallback.

---

## 🆘 Common Issues & Fixes

| Problem | Error Message | Fix |
|---------|-------|-----|
| Missing API key | `API key not found` | Run `python scripts/setup_secrets.py` again |
| Backend won't start | `Port 8000 already in use` | `lsof -i :8000` then kill process |
| Frontend can't connect | `Connection refused` | Verify Terminal 1 shows "Uvicorn running" |
| Very slow responses | Takes 5+ min per operation | Normal (LLM processing time), not an error |
| Mermaid diagrams not showing | Blank section | Refresh browser, it may load after 30 sec |
| "Confidence score 0" | Research validation failed | Use clearer topic, or restart backend |

---

## 📚 Documentation Map

**Where to go for:**
- 🎯 "How do I run this?" → **[RUN_APP_STEP_BY_STEP.md](RUN_APP_STEP_BY_STEP.md)** (comprehensive)
- 🎭 "What's real vs mock?" → **[MOCK_VS_REAL_REFERENCE.md](MOCK_VS_REAL_REFERENCE.md)** (detailed)
- 📋 "Quick status check" → **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** (1 page)
- 🏗️ "Architecture overview" → **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** (15 min read)
- 🔍 "What's complete/incomplete?" → **[IMPLEMENTATION_AUDIT.md](IMPLEMENTATION_AUDIT.md)** (comprehensive)
- 📁 "File structure" → **[FILE_INVENTORY.md](FILE_INVENTORY.md)** (reference)
- 🗺️ "All documentation" → **[STATUS_INDEX.md](STATUS_INDEX.md)** (overview)

---

## 🎯 API Endpoints Quick Reference

```bash
# Create session
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI in healthcare"}'

# Get session
curl http://localhost:8000/sessions/{session_id}

# Generate outline
curl -X POST http://localhost:8000/outline \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "topic_data": {...}}'

# Generate platforms
curl -X POST http://localhost:8000/platforms \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "content_id": "yyy"}'

# Process feedback
curl -X POST http://localhost:8000/iterate \
  -H "Content-Type: application/json" \
  -d '{"session_id": "xxx", "feedback_areas": ["tone"], ...}'
```

---

## 💾 Database Location

```bash
# SQLite database is here:
~/.content-studio/sessions.db

# View it with sqlite3:
sqlite3 ~/.content-studio/sessions.db

# List tables:
.tables

# See sessions:
SELECT id, topic, status FROM Session LIMIT 5;
```

---

## 🚨 Emergency Stops

**If something breaks:**

```bash
# Kill backend (Ctrl+C in Terminal 1)
# Kill frontend (Ctrl+C in Terminal 2)

# Clear database and reset
rm ~/.content-studio/sessions.db
python scripts/setup_db.py

# Clear cache and cookies (Streamlit)
# Browser: Settings → Clear browsing data

# Restart everything:
# Terminal 1: python backend/main.py
# Terminal 2: streamlit run frontend/Home.py
```

---

## ✅ Success Checklist

After setup, you should have:
- [ ] Virtual environment activated (see `(venv)` in terminal)
- [ ] Dependencies installed (150+ packages)
- [ ] API keys configured (Azure OpenAI + Bing Search minimum)
- [ ] Database created (~100KB SQLite file)
- [ ] Backend running on port 8000 (Uvicorn logs visible)
- [ ] Frontend running on port 8501 (Streamlit logs visible)
- [ ] Browser opens to http://localhost:8501 ✅
- [ ] "New Session" page loads without errors
- [ ] Can enter a topic and click "Extract Topic"
- [ ] Gets response in 5-15 seconds (real LLM) or <1 sec (mock)

**If all ✅, you're ready to create content!**

---

## 🎉 You're Done Setting Up!

**Next**: Go to [RUN_APP_STEP_BY_STEP.md - Step 7](RUN_APP_STEP_BY_STEP.md#step-7-test-the-full-workflow) to test the complete workflow.

**Questions?** Check the [MOCK_VS_REAL_REFERENCE.md](MOCK_VS_REAL_REFERENCE.md) to understand what's real vs mocked.

Remember:
- ✅ App works with just real LLM calls
- ⚡ Falls back to mock templates if APIs fail
- 📊 Check logs to see which mode you're in
- 🔑 Need API keys for full functionality: `python scripts/setup_secrets.py`

**Happy content creating! 🚀**
