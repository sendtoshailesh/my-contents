# Quickstart: Personal AI Content Studio MVP

**Target Audience**: Developers setting up local development and first-time users of the system.  
**Duration**: ~15 minutes for setup, ~20 minutes for first content session.  
**Assumes**: Python 3.11+, basic CLI knowledge.

---

## Part 1: Local Development Setup

### Step 1: Clone & Install Dependencies

```bash
# Clone the repository
git clone <repo-url> my-contents
cd my-contents

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env with your API keys
# Required:
# - LLM_PROVIDER=anthropic or openai
# - LLM_API_KEY=your_key_here
# - TAVILY_API_KEY=your_key_here

# Open .env in your editor
code .env  # or nano, vim, etc.
```

**Important**: `.env` is in `.gitignore` and should never be committed.

### Step 3: Initialize SQLite Database

```bash
# Create database schema
python -m backend.setup_db

# Verify database exists
ls sessions.db  # Should show database file
```

### Step 4: Start Backend Server

```bash
# Terminal 1: Backend (FastAPI)
cd backend
uvicorn main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

### Step 5: Start Frontend (Streamlit)

```bash
# Terminal 2: Frontend (Streamlit)
streamlit run frontend/app.py

# You should see:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

**Success**: Both servers running! Open `http://localhost:8501` in your browser.

---

## Part 2: First Content Session Walkthrough

### Scenario

You're creating a LinkedIn post about **"LLMs and Emotional Intelligence in Leadership."**

#### Step 1: Topic Intake

**In the UI (Streamlit)**:

1. Click **"New Content Session"**
2. Select input type: **"Topic Name + Description"**
3. Enter topic: `"LLMs and Emotional Intelligence in Leadership"`
4. Optional context: `"For technical leaders who want to understand both the tech and the human side."`
5. Click **"Analyze Topic"**

**Behind the Scenes**:
- **Input Agent** extracts metadata:
  - Theme: "AI applications in leadership"
  - Audience: "Technical leaders"
  - Intent: "Educate + Inspire"
  - Depth: "Intermediate"
  - Focus Areas: `["AI/ML/GenAI", "Emotional Intelligence"]`

**UI Output**:
```
✓ Topic accepted
✓ Focus areas: AI/ML/GenAI, Emotional Intelligence
→ Next: Wait for outline generation...
```

---

#### Step 2: Outline Generation

**Automatic** (takes ~30 seconds):

**Reasoning Agent** generates outline:
```
Content Angle: "How LLM-powered tools can augment (not replace) 
  emotional intelligence in modern leadership"

Why Compelling: "Technical leaders struggle with EI; LLMs offer 
  a bridge to self-awareness and better team dynamics."

Sections:
  1. Hook: The paradox of smarter AI, lonelier leaders
  2. Problem: Why EI matters more than ever in tech
  3. Insight: How LLMs help—by providing real-time feedback
  4. Real-world case: A tech team using EI + LLM coaching
  5. Actionable: 3 ways to leverage LLMs for team development
  6. Takeaway: EI + AI = next-gen leadership
```

**UI Output**:
```
📋 Outline Generated

[Show outline structure + why_compelling]

→ Next: Fact-checking outline...
```

---

#### Step 3: Validation

**Research Agent** validates claims via Tavily:

**Claims checked**:
- "EI impacts team retention" → ✓ 3 credible sources found
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
