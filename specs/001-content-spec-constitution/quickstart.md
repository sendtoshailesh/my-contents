# Quickstart: Personal AI Content Studio MVP - v0.1.0

**Phase**: 6 (Final - Polish & Cross-Cutting Concerns)  
**Target Audience**: Developers and content creators  
**Setup Time**: ~10 minutes | First Session: ~15-20 minutes  
**Requirements**: Python 3.10+, API keys (OpenAI/Claude, Bing Search)

---

## Part 1: Setup (10 minutes)

### 1.1 Install & Configure

```bash
# Navigate to project
cd /Users/shaileshmishra/my-docs/my-proj/my-contents

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 1.2 Configure API Keys

**Option A: .env file** (easiest for local dev)
```bash
# Create .env in project root
cat > .env << EOF
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
BING_SEARCH_API_KEY=...
EOF
```

**Option B: OS Keyring** (more secure)
```bash
# macOS Keychain
security add-generic-password -s openai -a $USER -w your_key_here
security add-generic-password -s anthropic -a $USER -w your_key_here
security add-generic-password -s bing_search -a $USER -w your_key_here
```

See `HYBRID_SECRETS_QUICK_START.md` for details.

### 1.3 Start Servers

**Terminal 1: Backend API** (http://localhost:8000)
```bash
python backend/main.py
```

You should see:
```
✅ Database initialized
✅ API routes registered
🚀 Starting server on http://localhost:8000
```

**Terminal 2: Frontend UI** (http://localhost:8501)
```bash
streamlit run frontend/Home.py
```

You should see:
```
Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

Open **http://localhost:8501** in your browser ✨

---

## Part 2: First Session (15-20 minutes)

### Scenario: Create LinkedIn Post

Topic: **"AI-Assisted Decision Making in Remote Teams"**

### Step 1: Create Session (1-2 min)

1. Click **"New Session"** in sidebar
2. Enter topic: `AI-Assisted Decision Making in Remote Teams`
3. Click **"Create Session"** button
4. System extracts topic and shows: ✅ Session created

**Behind the scenes**:
- Input Agent classifies topic
- Reasoning Agent generates outline with web research
- Research Agent validates claims (70% confidence threshold)

### Step 2: Review & Approve Outline (3-5 min)

**You see**:
```
📋 Outline Generated

Content Angle: How AI tools bridge decision gaps in remote teams

Why Compelling: Remote teams lack real-time feedback; AI helps async collaboration

Sections:
  1. The remote work reality
  2. Decision-making challenges
  3. AI as the great equalizer
  4. Real-world example: Team using Claude for brainstorms
  5. 3 practical applications
  6. When NOT to use AI

Research Results:
  ✅ Confidence: 78%
  ✅ Sources found: 12
  ✅ Passed validation
```

- Review content
- If confidence < 70%, click "Regenerate"
- If happy, click **"✅ Approve Outline"**

### Step 3: Select Framework (2 min)

**Choose from 6 storytelling frameworks**:
- 🎬 **TED Talk**: Narrative + insight
- ⚔️ **Hero's Journey**: Challenge + transformation
- 💡 **Problem-Solution**: Issue + actionable fix
- 📊 **Listicle**: Numbered tips
- ⚖️ **Comparison**: Side-by-side analysis  
- 📚 **Tutorial**: Step-by-step guide

**Select**: Problem-Solution (most relevant)
→ System recommends framework and shows visual plan

### Step 4: Generate Content (3-5 min)

Click **"Generate Content"** → AI creates multi-section draft

**Output**:
```
# AI-Assisted Decision Making in Remote Teams

## The Problem
Remote teams lack real-time feedback loops...

## The Solution
AI tools provide async decision support...

[Includes visuals, links, code examples if relevant]
```

### Step 5: Adapt for Platforms (2-3 min)

Click **"Generate Platform Versions"** → System creates:
- 📌 **LinkedIn**: Professional, 500-3000 chars
- 𝕏 **Twitter/X**: Thread format, 280-28K chars
- 🤖 **Reddit**: Authentic, discussion-focused
- 📖 **Medium**: Long-form, technical depth
- 📧 **Substack**: Newsletter, personal voice
- 📸 **Instagram**: Visual-first, captions

### Step 6: Iterate (Optional - 3-5 min)

Feedback? Click **"Get Feedback"** and specify:
- **Tone**: More conversational/formal/technical
- **Depth**: Add more details/simplify
- **Examples**: More/fewer real-world examples
- **Structure**: Reorganize sections

System regenerates based on feedback.

### Step 7: Complete (< 1 min)

When satisfied:
1. Click **"✅ Mark Complete"**
2. Type: `ok and good`
3. System saves session to history

**Session now appears in History tab** ✨

---

## Part 3: Advanced Features

### Session Management (Settings tab)

**View current sessions**:
- Settings → Session Management
- See count: X / 10 active sessions

**Manual cleanup**:
- Delete abandoned sessions
- Delete sessions > 30 days old
- Auto-cleanup removes sessions at startup

**Backup all sessions**:
- Settings → Backup & Export
- Download JSON with all sessions
- Useful for archiving completed work

### Preferences (Settings tab)

**Configure defaults**:
- Preferred LLM model (GPT-4, Claude 3, etc.)
- Default framework
- Visual preferences
- Confidence threshold

### View History (History tab)

**Three views**:
1. **All Sessions**: Complete list with stats
2. **In Progress**: Currently active sessions
3. **Completed**: Finished content

**Actions**:
- **Resume**: Continue unfinished session
- **Export**: Download session as JSON
- **Delete**: Remove session

---

## Part 4: API Usage (Advanced)

### REST API Endpoints

**Create session**:
```bash
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Your topic here",
    "url": "optional_url"
  }'
```

**List sessions**:
```bash
curl http://localhost:8000/api/sessions
```

**Get session details**:
```bash
curl http://localhost:8000/api/sessions/{session_id}
```

**Export session**:
```bash
curl -X POST http://localhost:8000/api/sessions/{session_id}/export
```

See `/api/docs` for complete OpenAPI documentation.

---

## 📊 Database Location

All data stored locally:
```
~/.content-studio/
├── sessions.db          # SQLite database
├── app.log             # Backend logs
└── streamlit.log       # Frontend logs
```

**To inspect database**:
```bash
sqlite3 ~/.content-studio/sessions.db
.tables                 # List all tables
SELECT COUNT(*) FROM sessions;
```

---

## 🐛 Troubleshooting

### Backend won't start
```
Error: Address already in use (port 8000)
Fix: Kill process on port 8000
  lsof -ti:8000 | xargs kill -9
```

### Frontend can't reach backend
```
Error: connection refused
Fix: Ensure backend is running in Terminal 1
  Check: curl http://localhost:8000/health
```

### Outline rejected (< 70% confidence)
```
Reason: Claims not well-supported
Fix:
  - Make topic more specific
  - Include concrete examples
  - Reference established concepts
```

### Sessions not appearing
```
Reason: Backend not initialized
Fix:
  - Stop and restart backend
  - Check ~/.content-studio/sessions.db exists
```

---

## 📈 Performance Notes

**Typical timings**:
- Outline generation: 30-60 seconds
- Content generation: 1-2 minutes
- Platform adaptation: 30-60 seconds
- Iteration: 1-2 minutes

**Total time per session**: 5-10 minutes (including user review time)

---

## 🔒 Security & Privacy

✅ **All data stays local**
- No cloud uploads
- SQLite database in home directory
- API keys in OS keyring or .env (not committed)

✅ **Secure by default**
- CORS limited to localhost
- No external data sharing
- Logs sanitized (no keys printed)

---

## 📚 Next Steps

1. **Try the walkthrough** above (15 min)
2. **Explore Settings** to configure preferences
3. **Check History** to manage sessions
4. **Review Documentation**:
   - `README.md` - Full feature overview
   - `CONTRIBUTING.md` - Development guide
   - `specs/` - Architecture details
5. **Read Logs** for insights:
   - `tail -f ~/.content-studio/app.log`

---

## 🚀 What's Included

**Phase 6 Features** (Complete ✅):
- ✅ Session history display (max 10)
- ✅ Resume/export/delete sessions
- ✅ Settings & configuration UI
- ✅ Model selection preferences
- ✅ Visual preferences  
- ✅ Manual cleanup controls
- ✅ Backup/export feature
- ✅ Comprehensive error handling
- ✅ Request/response logging
- ✅ User-friendly error messages
- ✅ Documentation (README, CONTRIBUTING)

**Version**: 0.1.0 MVP  
**Status**: Phase 6 Complete  
**Last Updated**: February 16, 2026

---

**Questions?** Check README.md or CONTRIBUTING.md for more details!
- "LLM feedback can improve self-awareness" → ✓ 2 credible sources
- "Technical teams struggle with EI" → ✓ 4 credible sources

**Validation Report**:
```
Confidence Score: 85% ✓ (Passed! Threshold: 70%)

Claims Checked: 3
Credible Sources Found: 9
Avg Credibility Score: 0.88

Sources:
  ✓ HBR: "Why EI Matters in Tech Teams" (2024)
  ✓ McKinsey: "AI in Leadership Development" (2023)
  ✓ Stanford AI Index: "LLMs for Coaching" (2024)

No issues flagged.
```

**UI Output**:
```
✓ Outline validated (85% confidence)
[Show validation report + sources]

Approve to proceed? [Yes] [Modify] [Restart]
```

---

#### Step 4: Approval Gate #1

**User clicks**: `[Yes, approve outline]`

**UI Response**:
```
✓ Outline approved
→ Next: Select storytelling framework and visuals...
```

---

#### Step 5: Framework & Visual Selection

**UI displays**:

```
Framework Recommendation: "TED"
Why: "Your topic benefits from a narrative arc: 
  Hook (paradox) → Solution (LLMs) → Impact (team dynamics)"

Other Options:
  • Hero's Journey
  • Problem → Solution → Impact (selected by default)
  • AIDA
  • Before–After–Bridge
  • Custom...

[Select Framework] [TED ✓] [Change]
```

**User accepts TED framework** → System maps sections to TED structure.

**Visual Recommendations**:

```
We recommend 3 visuals for your content:

1. Flow diagram: "How LLMs augment EI in leadership"
   Tool: Mermaid | Location: Section 3 (Insight)
   
2. Timeline: "Evolution of EI in tech teams"
   Tool: Mermaid | Location: Section 2 (Problem)
   
3. Infographic: "3 ways to leverage LLMs for team dev"
   Tool: Python/SVG | Location: Section 5 (Actionable)

Confirm these visuals? [Yes] [Customize] [None]
```

**User clicks**: `[Yes, confirm visuals]`

---

#### Step 6: Content Generation

**Automatic** (takes ~45 seconds):

**Content Agent** generates full narrative:

```
🎯 Generated Content (Draft)

---

**Title**: "How LLMs Can Make You a Better Leader: 
  A Paradox in the AI Age"

**Hook**: 
  We're hiring the smartest AI ever built. But are 
  our teams happier? Research suggests not. Smarter 
  tech doesn't always mean smarter leadership...

[Mermaid diagram: Flow diagram showing EI + LLM feedback loop]

**Problem**: 
  Technical leaders excel at logic but often struggle 
  with emotional intelligence. 85% of engineers report 
  difficulty understanding their team's emotional needs...

[Timeline visualization]

**Insight**: 
  Here's the counterintuitive truth: LLMs aren't here 
  to replace EI. They're here to train it. By providing 
  real-time feedback on communication patterns...

**Case Study**: 
  At TechCorp, a team used an LLM-powered reflection 
  tool to analyze their team meetings. Result: 40% 
  improvement in retention within 6 months...

**Actionable: 3 Ways to Leverage LLMs**:
  1. Weekly Reflection: Use an LLM to analyze your 
     interactions and suggest improvements.
  2. Team Coaching: Provide LLM-generated feedback 
     to team members (with care).
  3. Emotional Pattern Recognition: Use LLMs to 
     identify team stress patterns early.

[Infographic: 3-step visual]

**Takeaway**: 
  The future of leadership isn't smarter AI or better 
  EI in isolation. It's the symbiosis of both. Use LLMs 
  as your partner—not your replacement—in building 
  emotionally intelligent teams.

---

Word Count: 2,847 | Readability: Intermediate | Code Snippets: 0
```

**UI Output**:
```
✓ Content generated (2,847 words)
→ Next: Generating platform-specific versions...
```

---

#### Step 7: Platform-Specific Versions

**Automatic** (takes ~20 seconds):

**Platform Agent** adapts for 6 platforms:

| Platform | Output Example | Status |
|----------|---|---|
| LinkedIn | "🧠 **How LLMs Can Make You a Better Leader**... [500 chars]" | ✓ |
| Twitter | "🧠 How are smarter AIs making lonelier leaders?... [Thread of 7 tweets]" | ✓ |
| Reddit | "[Discussion post on r/leadership] Here's my take on LLMs & EI..." | ✓ |
| Medium | "[Full article with sections, visuals integrated]" | ✓ |
| Substack | "[Newsletter-formatted version]" | ✓ |
| Instagram | "[Carousel: 5 slides with EI + LLM tips]" | ✓ |

**UI Output**:
```
✓ Platform versions generated

[Tab selector: LinkedIn | Twitter | Reddit | Medium | Substack | Instagram]

Currently viewing: LinkedIn
─────────────────────────────────────
🧠 **How LLMs Can Make You a Better Leader**

In an age of smarter AI, why do teams feel lonelier?

[Shows LinkedIn version]

👍 Approve all? [Yes] [Review] [Edit]
```

---

#### Step 8: Approval Gate #2 (Platform Versions)

**User clicks**: `[Yes, approve all]`

**UI Response**:
```
✓ Platform versions approved

Ready to publish? (Manual publishing only)
────────────────────────────────────────

To publish, copy your content version:
  • LinkedIn: [view] [copy] [export]
  • Twitter: [view] [copy] [export]
  • Reddit: [view] [copy] [export]
  • And more...

Or: Request refinements below.
```

---

#### Step 9: Refinement Loop

**User reads all versions and decides to refine**.

**Requests improvement**:
```
📝 What would you like to improve?

Feedback Areas (select all that apply):
  ☑ Tone
  ☐ Depth
  ☐ Visuals
  ☐ Technicality
  ☑ Humor
  ☐ Examples
  ☐ Structure

Freeform Feedback:
"LinkedIn feels too formal. Add a touch of humor. 
Also, Reddit version is too long—trim it."

[Submit Feedback]
```

**System regenerates**:
- Adjusts tone (adds mild humor, especially in LinkedIn hook).
- Shortens Reddit version by 30%.
- Updates all platform versions accordingly.

**UI Output**:
```
✓ Feedback processed

Regenerated:
  • LinkedIn: [shorter hook with humor]
  • Reddit: [trimmed by 30%, more casual]
  • Other platforms: Updated for consistency

Ready to go? 
  [Yes, these look good]  [More refinements]
```

---

#### Step 10: Session Complete

**User reviews and is satisfied**.

**User types**: `"ok and good"`

**UI Output**:
```
✅ Session Complete!

─────────────────────────────────
Summary
─────────────────────────────────
Topic: LLMs and EI in Leadership
Outline Approval: Iteration 1
Framework: TED
Visuals: 3 diagrams
Refinement Cycles: 1
Duration: 18 minutes

Platform Outputs Ready:
  ✓ LinkedIn (500 chars)
  ✓ Twitter (7-tweet thread)
  ✓ Reddit (1,200 chars)
  ✓ Medium (2,800 words)
  ✓ Substack (2,500 chars)
  ✓ Instagram (5-slide carousel)

Next Steps:
  1. Download or copy versions above
  2. Publish to your platforms manually
  3. Start another session or view history

[Download All] [View History] [New Session]
```

---

## Part 3: Key Takeaways

### Development Workflow

1. **Backend** (FastAPI) handles all agents and data logic.
2. **Frontend** (Streamlit) displays UI and manages session flow.
3. **Database** (SQLite) stores sessions for audit and recovery.
4. All agent calls are **logged** for debugging.

### Session Approval Gates

```
Input Accepted
    ↓
Outline Generated & Validated (70% confidence required)
    ↓
User Approves Outline ← [Gate 1: No = regenerate]
    ↓
Framework & Visuals Selected
    ↓
Content Generated
    ↓
Platform Versions Generated
    ↓
User Reviews & Refines (loop allowed)
    ↓
User says "ok and good" → Session Complete
```

### Common Commands

```bash
# View logs
tail -f backend/logs/agent.log

# Check validation threshold
grep "confidence_score" backend/src/services/research_service.py

# View all sessions
sqlite3 sessions.db "SELECT id, topic, status FROM sessions;"

# Run tests
pytest tests/

# Reset database (dev only!)
rm sessions.db && python -m backend.setup_db
```

---

## Troubleshooting

### OpenAI / Anthropic API Key Error

```
ERROR: LLM_API_KEY not found in environment
```

**Solution**: 
```bash
# Ensure .env has your key
echo "LLM_API_KEY=sk-..." >> .env

# Reload terminal
source venv/bin/activate
```

### Tavily API Timeout

```
ERROR: Research Agent failed—Tavily search timeout
```

**Solution**:
- Check internet connection.
- Verify `TAVILY_API_KEY` in `.env`.
- Retry in a moment (API rate limits).

### Streamlit Caching Issue

```
ERROR: Fresh values for cached function not computing
```

**Solution**:
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit/cache
streamlit run frontend/app.py --logger.level=debug
```

### Database Locked

```
ERROR: database is locked
```

**Solution**:
```bash
# Make sure only one process is using the DB
pkill -f "python.*
" 
rm sessions.db  # Start fresh if needed
python -m backend.setup_db
```

---

## Next Steps

1. **Create your first content session** using the walkthrough above.
2. **Review `contracts/`** to understand agent I/O formats.
3. **Check `data-model.md`** for database schema.
4. **Run tests**: `pytest tests/ -v`
5. **Browse backend code**: `backend/src/agents/` for agent logic.

---

## Support & Documentation

- **API Docs**: After backend starts, visit `http://localhost:8000/docs` (Swagger UI).
- **Data Model**: See [data-model.md](data-model.md)
- **Agent Contracts**: See `contracts/` directory
- **Feature Spec**: See [spec.md](spec.md)
- **Constitution**: See [constitution.md](constitution.md)
