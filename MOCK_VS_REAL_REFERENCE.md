# 🎭 Mock vs Real Implementations - Complete Reference

**Purpose**: Understand which parts of the app use real APIs vs mock fallbacks  
**Last Updated**: February 16, 2026

---

## 🎯 Quick Summary

| Component | Real Calls | Mock Fallback | Default | When Mock Used |
|-----------|-----------|---------------|---------|-----------------|
| **Input Agent** | ✅ GPT/Claude/Llama | ✅ Yes | Real first | API fails/missing |
| **Reasoning Agent** | ✅ GPT/Claude/Llama | ✅ Yes | Real first | API fails/missing |
| **Research Agent** | ✅ Bing Search API | ✅ Yes | Real first | No API key |
| **Storytelling Agent** | ✅ Framework engine | ✅ Yes | Real first | API fails/missing |
| **Content Agent** | ✅ GPT/Claude/Llama | ✅ Yes | Real first | API fails/missing |
| **Platform Agent** | ✅ Llama 3.1 only | ❌ No | Real first | N/A |
| **Iteration Handler** | ✅ LLM + logic | ❌ No | Real first | N/A |
| **Database** | ✅ SQLite (real) | ❌ No | Real only | N/A |
| **Search Service** | ✅ Bing API | ✅ Yes | Real first | API fails |

---

## 🧠 Agent-by-Agent Breakdown

### 1. INPUT AGENT - Topic Extraction

**File**: `backend/agents/input_agent.py`

#### Real Implementation
```python
# Lines 48-85 (Real LLM Call)
if not self.use_mock:
    prompt = self._build_extraction_prompt(topic)
    response = self.llm.call(
        task_type="classification",
        prompt=prompt,
        max_tokens=500
    )
    extracted = self._parse_json_response(response)
    # Real LLM call happens here
```

**What it does:**
- Uses Llama 3.1 (cost-effective) to classify topic
- Extracts: theme, audience, intent, focus area
- Matches against 5 focus areas: AI, Cloud, Migration, EI, Emerging
- Returns confidence score 0.0-1.0

**API Calls Made:**
- 1 call to Azure OpenAI / Anthropic / Ollama
- Input: ~100 tokens
- Output: ~200 tokens
- Time: 5-15 seconds
- Cost: $0.01-0.05

**Example Output (Real)**:
```json
{
  "topic": "AI in healthcare",
  "theme": "How artificial intelligence is transforming medical diagnosis and treatment",
  "target_audience": "Healthcare professionals",
  "primary_intent": "Educate",
  "focus_area": "AI",
  "is_out_of_scope": false,
  "confidence": 0.92
}
```

#### Mock Implementation
```python
# Lines 77-81 (Mock Fallback)
if self.use_mock:
    logger.debug("🎭 Using mock agent")
    mock_result = MockInputAgent.extract_topic_info(topic)
    # Returns generic template response
```

**Location**: `backend/agents/mock_agents.py` lines 10-27

**What it returns**:
```json
{
  "topic": "AI in healthcare",
  "theme": "ai_in_h",
  "target_audience": "general_public",
  "primary_intent": "educate",
  "focus_area": "AI",
  "is_out_of_scope": false,
  "confidence": 1.0
}
```

**When Mock is Used:**
- ❌ Azure OpenAI key not found
- ❌ API timeout (>30 seconds)
- ❌ Invalid API key format
- ❌ Network error

**Logs Indicator**:
```
✓ InputAgent initialized (mock=False)      # Real
🎭 Using mock agent                        # Mock
```

---

### 2. REASONING AGENT - Outline Generation

**File**: `backend/agents/reasoning_agent.py`

#### Real Implementation
```python
# Lines 60-120 (Real LLM Call)
def generate_outline(self, topic_data: Dict) -> Dict:
    prompt = self._build_outline_prompt(topic_data)
    
    response = self.llm.call(
        task_type="generation",
        prompt=prompt,
        max_tokens=2000,
        temperature=0.7
    )
    
    outline = self._parse_json_response(response)
    return outline
```

**What it does:**
- Generates 5-part detailed outline
- Includes: title, description, key points for each section
- Returns content angle and target audience
- Calculates difficulty level and read time

**API Calls Made:**
- 1 call to Azure OpenAI / Anthropic
- Input: ~300-500 tokens
- Output: ~1000-1500 tokens
- Time: 20-45 seconds
- Cost: $0.05-0.15

**Example Output (Real)**:
```json
{
  "topic": "AI in healthcare",
  "content_angle": "From Robot Assistants to Diagnostic AI: The Medical Revolution Happening Now",
  "sections": [
    {
      "title": "The Current Crisis in Healthcare",
      "description": "Why AI became necessary",
      "key_points": ["Doctor shortage", "Diagnostic errors", "Cost explosion"],
      "order": 1
    },
    ...5 more sections...
  ],
  "estimated_read_time": 8,
  "difficulty_level": "intermediate"
}
```

#### Mock Implementation

**Location**: `backend/agents/mock_agents.py` lines 30-65

**What it returns**:
```json
{
  "topic": "AI in healthcare",
  "content_angle": "Technical exploration of AI in healthcare",
  "sections": [
    {"title": "Introduction", "description": "Overview", ...},
    {"title": "Main Concepts", "description": "Core ideas", ...},
    {"title": "Current State", ...},
    {"title": "Future Implications", ...},
    {"title": "Conclusion", ...}
  ],
  "estimated_read_time": 8,
  "difficulty_level": "intermediate"
}
```

**When Mock is Used:**
- ❌ Azure OpenAI key missing
- ❌ API error (rate limit, timeout)
- ❌ LLM not initialized

---

### 3. RESEARCH AGENT - Web Search Validation

**File**: `backend/agents/research_agent.py`

#### Real Implementation
```python
# Lines 50-120 (Real Bing Search API Call)
def validate_outline(self, outline: Dict) -> Dict:
    claims = self._extract_claims_from_outline(outline)
    
    validation_results = []
    for claim in claims:
        sources = self.search_service.search(claim)
        confidence = self._calculate_credibility(sources)
        validation_results.append({
            "claim": claim,
            "sources": sources,
            "confidence": confidence
        })
    
    return {
        "passed_validation": avg_confidence >= 0.70,
        "confidence_score": avg_confidence,
        "credible_sources_found": len(sources),
        ...
    }
```

**What it does:**
- Extracts 5-8 key claims from outline
- Searches Bing API for each claim (up to 8 parallel)
- Scores credibility of each source
- Returns 70% confidence threshold check

**API Calls Made:**
- 5-8 calls to Bing Search API (parallel)
- Input per call: ~20-50 characters
- Output per call: 10-20 results per query
- Time: 5-15 seconds (parallel)
- Cost: $0.005-0.02 per search

**Example Output (Real)**:
```json
{
  "passed_validation": true,
  "confidence_score": 0.85,
  "credible_sources_found": 42,
  "claims_checked": 8,
  "validation_details": {
    "sources": [
      "https://pubmed.ncbi.nlm.nih.gov/...",
      "https://www.nature.com/...",
      "https://scholar.google.com/..."
    ],
    "verified_claims": 7,
    "unverified_claims": 1,
    "contradictions": 0
  }
}
```

#### Mock Implementation

**Location**: `backend/agents/mock_agents.py` lines 68-90

**What it returns**:
```json
{
  "passed_validation": true,
  "confidence_score": 0.85,
  "credible_sources_found": 12,
  "claims_checked": 8,
  "validation_details": {
    "sources": [
      "https://example.com/article1",
      "https://example.com/article2",
      "https://example.com/article3"
    ],
    "verified_claims": 7,
    "unverified_claims": 1,
    "contradictions": 0
  }
}
```

**When Mock is Used:**
- ❌ Bing Search API key missing
- ❌ API timeout (>30 seconds)
- ❌ Network error
- ⚠️ Rate limited (10 searches/second max)

**Logs Indicator**:
```
🔍 Searching for: "claim text"
Found 23 results                    # Real - actual count
Found 12 results (mock)             # Mock - hardcoded
```

**Important Note**: Research agent is **often using real API** even if other APIs fail, because Bing Search is treated as essential. Only falls back to mock if Bing API is explicitly unavailable.

---

### 4. STORYTELLING AGENT - Framework Mapping

**File**: `backend/agents/storytelling_agent.py`

#### Real Implementation
```python
# Lines 70-150 (Framework Selection + Visual Generation)
def generate_framework_plan(self, outline: Dict, visual_opt_in: bool) -> Dict:
    # Step 1: Recommend framework based on outline shape
    framework = self._recommend_framework(outline)
    
    # Step 2: Map outline sections to framework steps
    framework_structure = self._map_sections_to_framework(
        outline_sections=outline['sections'],
        framework=framework
    )
    
    # Step 3: Generate visual plans (Mermaid diagrams)
    visual_plan = []
    if visual_opt_in:
        for section_idx, section in enumerate(framework_structure, 1):
            visual = self.llm.call(
                task_type="mermaid_generation",
                prompt=f"Create Mermaid diagram for: {section['title']}",
                max_tokens=300
            )
            visual_plan.append({
                "visual_id": section_idx,
                "type": self._determine_visual_type(section),
                "code": visual
            })
    
    return {
        "framework_choice": framework,
        "framework_structure": framework_structure,
        "visual_plan": visual_plan
    }
```

**What it does:**
- Analyzes outline to pick best framework from 6 options
- Maps outline sections to framework steps
- Generates Mermaid diagram code for 2-3 visuals
- No LLM needed if using framework templates

**API Calls Made:**
- 0-3 calls to LLM (only for diagram generation)
- Input: ~100-200 tokens per visual
- Output: ~200-400 tokens per visual
- Time: 10-30 seconds (if visuals enabled)
- Cost: $0.01-0.05

**Example Output (Real - With Visuals)**:
```json
{
  "framework_choice": "Hero's Journey",
  "framework_structure": [
    {"framework_step": 1, "outline_section": 1, "title": "The Starting World"},
    {"framework_step": 2, "outline_section": 2, "title": "The Call to Adventure"},
    ...6 more steps...
  ],
  "visual_plan": [
    {
      "visual_id": 1,
      "type": "flowchart",
      "code": "flowchart LR\nA[Problem] --> B[Analysis]\nB --> C[Solution]",
      "description": "Problem to solution flow"
    },
    ...more visuals...
  ]
}
```

#### Mock Implementation

**Partially** uses mock! The framework selection logic is real, but visual generation is mocked.

**Location**: `backend/agents/mock_agents.py` lines 93-135

**What it mocks**:
- Visual generation (hardcoded Mermaid examples)
- Visual description (generic templates)

**What's real**:
- Framework recommendation algorithm
- Section mapping logic

---

### 5. CONTENT AGENT - Content Generation

**File**: `backend/agents/content_agent.py`

#### Real Implementation
```python
# Lines 60-150 (Real Content Generation)
def generate_content(
    self,
    outline: Dict,
    framework: str,
    visual_plan: List[Dict]
) -> Dict:
    if self.use_mock:
        logger.warning("Falling back to MockContentAgent: API error")
        return MockContentAgent.generate_content(...)
    
    # Build comprehensive prompt
    prompt = self._build_content_prompt(
        outline=outline,
        framework=framework,
        visual_plan=visual_plan,
        framework_templates=self.framework_engine.get_templates(framework)
    )
    
    # Call GPT-4 (large model for quality)
    response = self.llm.call(
        task_type="content_generation",
        model="gpt-4-turbo",
        prompt=prompt,
        max_tokens=4000,
        temperature=0.8
    )
    
    # Parse and structure response
    content_draft = self._parse_and_structure_response(
        response=response,
        framework=framework,
        visual_plan=visual_plan
    )
    
    return content_draft
```

**What it does:**
- Generates full article (2000-3000 words)
- Structures content according to framework
- Integrates visual placeholders
- Includes code examples if technical topic
- Maintains tone and audience focus

**API Calls Made:**
- 1 call to Azure OpenAI GPT-4 (large model)
- Input: ~1000-1500 tokens
- Output: ~4000 tokens
- Time: 45-120 seconds
- Cost: $0.10-0.30 per generation

**Example Output (Real)**:
```markdown
# AI Transforming Healthcare: From Diagnosis to Cure

## Introduction
In the next decade, artificial intelligence will fundamentally reshape how we approach medicine...

## The Current Crisis in Healthcare
[Full content with real insights]

## Visual: Disease Diagnosis Flowchart
[Integrated Mermaid diagram]

## Key Case Studies
[Real examples with citations]

...rest of full article...
```

#### Mock Implementation

**Location**: `backend/agents/mock_agents.py` lines 138-200

**What it returns**:
```markdown
# Generated Content

## Overview
This is a mock content draft.

## Main Concepts
Key ideas and examples go here.

## Visuals
- See Visual 1: Description
```

**When Mock is Used:**
- ❌ GPT-4 API key missing
- ❌ API error/timeout
- ❌ Cost control (if implemented)
- ✅ **Default if initialization fails**

**Logs Indicator**:
```
✅ ContentAgent initialized (0.82 quality score)      # Real
⚠️  Falling back to MockContentAgent                  # Mock
```

---

### 6. PLATFORM AGENT - Multi-Platform Generation

**File**: `backend/agents/platform_agent.py`

#### Real Implementation (100% - NO MOCK)
```python
# Lines 50-250 (All Real - No Mock Fallback)
def generate_all_platforms(self, session_id: str, content: Dict) -> Dict:
    """Generate content for 6 platforms using Llama 3.1"""
    
    platforms = {}
    
    # LinkedIn (1500+ words professional article)
    platforms['linkedin'] = self.generate_linkedin_version(content)
    
    # Twitter (5-7 tweets with threading)
    platforms['twitter'] = self.generate_twitter_threads(content)
    
    # Reddit (Markdown with subreddit suggestions)
    platforms['reddit'] = self.generate_reddit_post(content)
    
    # Medium (Blog format with recommendations)
    platforms['medium'] = self.generate_medium_article(content)
    
    # Substack (Newsletter format with CTA)
    platforms['substack'] = self.generate_substack_post(content)
    
    # Instagram (Captions + hashtags)
    platforms['instagram'] = self.generate_instagram_captions(content)
    
    return platforms
```

**What it does:**
- Generates 6 platform-specific versions
- Each optimized for unique audiences/constraints
- LinkedIn: Professional tone, detailed structure
- Twitter: Concise, emoji usage, threading
- Reddit: Markdown, engagement focus, subreddit match
- Medium: Blog-friendly, recommendations, pay-wall consideration
- Substack: Newsletter style, CTA, personalization
- Instagram: Short captions, hashtags, visual descriptions

**API Calls Made:**
- 6 calls to Llama 3.1 (one per platform)
- Input per call: ~800-1200 tokens
- Output per call: ~500-1500 tokens
- Time: 2-4 minutes total (sequential)
- Cost: $0.01-0.05 per generation (~$0.06-0.30 total)

**Example Output (Real - LinkedIn)**:
```markdown
# How AI is Transforming Healthcare: A Professional Perspective

As healthcare professionals, we're experiencing an unprecedented shift...

[Full professional article with citations and data]

#AI #Healthcare #Innovation #MedicalTechnology
```

**Example Output (Real - Twitter)**:
```
🧵 Thread: How AI is revolutionizing healthcare in 2024

1/ The problem: Doctors overworked, diagnostics delayed, costs soaring...

2/ The solution: AI algorithms that learn from millions of cases...

3/ LinkedIn  Impact: 40% faster diagnosis time...

4/ The next frontier: Personalized treatment plans...
```

#### Important: Platform Agent

- ✅ **100% REAL** - No mock fallback
- ✅ Uses Llama 3.1 specifically (cost-effective)
- ✅ All 6 platforms are always generated with real LLM
- ❌ If Llama API fails, entire endpoint fails (no fallback)

**Logs Indicator**:
```
Generating LinkedIn version...    # Real call 1/6
Generating Twitter threads...     # Real call 2/6
Generating Reddit post...         # Real call 3/6
[More real calls...]
Success: 6/6 platforms generated   # All real if successful
```

---

### 7. ITERATION HANDLER - Feedback Processing

**File**: `backend/agents/iteration_handler.py`

#### Real Implementation (100% - NO MOCK)
```python
# Lines 100-300 (All Real - No Mock)
def process_feedback(
    self,
    session_id: str,
    feedback_areas: List[str],
    feedback_text: str
) -> Dict:
    """Process user feedback and regenerate affected components"""
    
    # Step 1: Parse feedback areas (7 options)
    parsed_areas = self._parse_feedback_areas(feedback_areas)
    # tone, depth, visuals, technicality, humor, examples, structure
    
    # Step 2: Determine what to regenerate
    if "tone" in parsed_areas or "depth" in parsed_areas:
        # Regenerate entire content draft
        new_content = self.content_agent.generate_content(...)
    
    # Step 3: Regenerate platform versions if needed
    if "visuals" in parsed_areas or "structure" in parsed_areas:
        # Regenerate platform versions with new structure
        new_platforms = self.platform_agent.generate_all_platforms(...)
    
    # Step 4: Check for completion phrase
    if self._check_completion_phrase(feedback_text):
        # User said "ok and good" - mark session complete
        return self._complete_session(session_id)
    
    return {
        "iteration_number": iteration_num,
        "affected_components": parsed_areas,
        "regenerated_content": new_content,
        "regenerated_platforms": new_platforms,
        "status": "pending_review"
    }

def _check_completion_phrase(self, text: str) -> bool:
    """Detect 'ok and good' or similar completion phrases"""
    completion_patterns = [
        r"\bok\s+and\s+good\b",
        r"\ball\s+good\b",
        r"\blets?\s+go\b",
        r"\bdone\b",
        r"\bcomplete\b",
        r"\bfinish\b"
    ]
    for pattern in completion_patterns:
        if re.search(pattern, text.lower()):
            return True
    return False
```

**What it does:**
- Processes 7 types of feedback
- Identifies which components to regenerate
- Re-runs affected LLM calls only
- Detects "ok and good" phrase to mark complete
- Tracks iteration count (up to 5 typically)

**API Calls Made:**
- Variable: 0-6 calls depending on feedback areas
- If tone/depth: 1 call to regenerate content
- If visuals/structure: 6 calls to regenerate platforms
- Time: 30 seconds - 4 minutes
- Cost: $0.05-0.35 depending on regeneration scope

**Completion Phrase Detection**:
- ✅ Detects: "ok and good", "all good", "let's go", "done", "complete"
- ✅ Case-insensitive
- ✅ Uses regex patterns
- ✅ Location: `iteration_handler.py` lines 350-365

**Example Output (Real)**:
```json
{
  "iteration_number": 2,
  "affected_components": ["tone", "examples"],
  "regenerated_content": {
    "body_text": "[New content with more conversational tone]",
    "changes": ["Tone made conversational", "Examples added"]
  },
  "regenerated_platforms": {
    "linkedin": "[Updated LinkedIn version]",
    "twitter": "[Updated Twitter threads]",
    ... other platforms...
  },
  "status": "pending_review"
}
```

#### Important: Iteration Handler

- ✅ **100% REAL** - No mock fallback
- ✅ All regeneration uses actual LLM calls
- ✅ "ok and good" phrase detection is regex-based
- ✅ Smart regeneration: only regenerates what's needed

---

## 📊 Fallback Chain Summary

### When API Calls Fail

1. **Try Primary API** (e.g., Azure OpenAI)
2. **Try Fallback #1** (e.g., Anthropic Claude)
3. **Try Fallback #2** (e.g., OpenAI GPT-4)
4. **Try Fallback #3** (e.g., Ollama local)
5. **Fall back to MOCK** (hardcoded template responses)

**Example**: In LLMService
```python
FALLBACK_CHAIN = {
    "llama-3.1": "gpt-4-turbo",      # Try Claude if Llama fails
    "gpt-4-turbo": "claude-3.5",     # Try OpenAI if Claude fails
    "claude-3.5": None               # No more fallbacks
}
```

---

## 🔍 How to Detect Real vs Mock in Logs

### Real LLM Call Log
```
✓ InputAgent initialized (mock=False)
🔍 Extracting topic info from: AI in healthcare
→ Calling LLM with Llama 3.1
← Response received (1234 tokens)
✅ Topic matched to focus area: AI (confidence: 0.92)
```

### Mock Fallback Log
```
⚠️  Failed to initialize LLM: Azure OpenAI API key not found
😭 InputAgent initialized (mock=True)
🔍 Extracting topic info from: AI in healthcare
🎭 Using mock agent
← Mock response returned
✅ Topic matched to mock template: AI (confidence: 1.0)
```

### Research Agent - Real Search
```
🔍 Searching for claim: "AI improving diagnostic accuracy"
← Found 42 results from Bing Search API
✅ Verified: 7 credible sources found
📊 Confidence score: 0.85 (PASSED)
```

### Research Agent - Mock Search
```
🔍 Searching for claim: "AI improving..."
🎭 Using mock search results
← Returned 12 mock results
✅ Confidence score: 0.85 (mock value)
```

---

## 📝 Configuration: Enabling/Disabling Mocks

### Force Real Only (No Mock Fallback)

Edit `backend/main.py`:
```python
# Disable mocks entirely
os.environ["DISABLE_MOCK_AGENTS"] = "true"

# Now if real API fails, endpoint returns error instead of mock
```

### Force Mock Only (Testing)

Edit agent files:
```python
# In input_agent.py
def __init__(self):
    self.use_mock = True  # Always use mock for testing
    self.llm = None
```

### Check Current Configuration

```python
# In your code
agent = InputAgent()
print(f"Using mock: {agent.use_mock}")
# Output: Using mock: False (if API available)
# Output: Using mock: True (if API missing)
```

---

## 🚀 Production Recommendations

### For Single-User MVP (Current)
- ✅ **Recommended**: Keep all mocks enabled (for resilience)
- ✅ **Benefit**: App works even if one API fails
- ⚠️ **Trade-off**: Lower quality if falling back to mock

### For Production Multi-User
- 🔴 **Recommended**: Disable mock agents entirely
- 🔴 **Reason**: Customers expect consistent quality
- 🔴 **Solution**: Add monitoring/alerting for API failures
- 🔴 **Fallback**: Use graceful degradation (error message) instead of mock

---

## 💡 Cost Impact of Mock vs Real

| Action | Real LLM | Mock | Difference |
|--------|----------|------|-----------|
| Extract topic (1 call) | $0.01 | $0 | +$0.01 |
| Generate outline (1 call) | $0.05 | $0 | +$0.05 |
| Validate with search (8 calls) | $0.02 | $0 | +$0.02 |
| Generate content (1 call) | $0.20 | $0 | +$0.20 |
| Generate platforms (6 calls) | $0.06 | $0 | +$0.06 |
| **One full workflow** | **$0.34** | **$0** | **+$0.34** |
| **One month (100 sessions)** | **$34** | **$0** | **+$34** |

**Note**: Real LLM generally faster (2-3 min) vs mock (instant), so prefer real for better UX.

---

## 🎯 Verification Checklist

When you first run the app, verify:

- [ ] Backend logs show `mock=False` for all agents
- [ ] Search service shows "Found [X] results" (not mock count)
- [ ] Response times are 5-30 seconds per operation
- [ ] Content is unique/contextual (not template text)
- [ ] Outline sections match your topic (not generic)
- [ ] Mermaid diagrams are specific to your topic
- [ ] Platform versions are properly formatted
- [ ] Iteration regeneration updates content appropriately

**If any show mock fallback:**
1. Run `python scripts/setup_secrets.py` again
2. Verify API keys are entered correctly
3. Check internet connection
4. Restart backend: `python backend/main.py`

---

**Next Steps:**
1. Follow [RUN_APP_STEP_BY_STEP.md](RUN_APP_STEP_BY_STEP.md) to start the app
2. Watch logs during first workflow to verify real calls
3. Check this document when you see "mock" in output
4. Refer back here when troubleshooting API issues

---

**Questions?**
- Real vs mock behavior: See **Agent-by-Agent Breakdown** section
- How to verify in logs: See **How to Detect Real vs Mock in Logs**
- API fallback logic: See **Fallback Chain Summary**
- Cost implications: See **Cost Impact of Mock vs Real**
