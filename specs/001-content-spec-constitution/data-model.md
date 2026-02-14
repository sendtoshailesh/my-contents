## Storage Architecture: Azure Cosmos DB + PostgreSQL

### Design Pattern

- **Cosmos DB** (NoSQL, JSON documents): Session-centric storage with nested entities
    - High throughput, eventual consistency
    - Geo-distributed for disaster recovery
    - Ideal for semi-structured, rapidly evolving data
  
- **PostgreSQL** (SQL, normalized tables): Reference data with strong consistency
    - Stable schema for frameworks, platforms, focus areas
    - Full ACID transactions if needed
    - Easier querying and updates

### Cosmos DB Schema

**Database**: `sessions_db`  
**Container**: `sessions` (partition key: `/session_id`)

```json
{
    "id": "uuid",
    "session_id": "uuid",
    "created_at": "ISO8601 timestamp",
    "updated_at": "ISO8601 timestamp",
    "status": "enum[input | outline_review | ...]",
    "topic_input": "string",
    "focus_area_match": ["array"],
    "focus_area_confirmed": "boolean",
    "iteration_count": "integer",
    "completed_phrase": "string | null",
  
    "outlines": [
        {
            "id": "uuid",
            "version": 1,
            "content_angle": "string",
            "target_audience": "string",
            "primary_intent": "enum",
            "sections": ["array"],
            "why_compelling": "string",
            "user_approved": "boolean",
            "approval_timestamp": "timestamp | null",
      
            "validation_report": {
                "id": "uuid",
                "confidence_score": 0.85,
                "claims_checked": 5,
                "credible_sources_found": 4,
                "sources": ["array of objects"],
                "issues": ["array"],
                "passed_validation": true,
                "validation_timestamp": "timestamp"
            }
        }
    ],
  
    "content_draft": {
        "id": "uuid",
        "outline_id": "uuid",
        "framework_choice": "ted",
        "framework_explanation": "string",
        "visual_plan": ["array"],
        "body_text": "string",
        "auto_generated_timestamp": "timestamp",
        "include_code": false,
        "code_snippets": ["array"]
    },
  
    "platform_versions": [
        {
            "platform_name": "linkedin",
            "content": "string",
            "visual_references": ["array"],
            "version": 1,
            "generated_timestamp": "timestamp"
        }
    ],
  
    "iteration_feedback": [
        {
            "id": "uuid",
            "iteration_number": 1,
            "feedback_areas": ["array"],
            "freeform_feedback": "string",
            "affected_components": ["array"],
            "regenerated_content": "string",
            "platform_versions_updated": true,
            "feedback_timestamp": "timestamp"
        }
    ]
}
```

### PostgreSQL Schema

```sql
-- Reference data for frameworks
CREATE TABLE frameworks (
        id TEXT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        structure JSONB NOT NULL,
        example_use_case TEXT,
        created_at TIMESTAMP DEFAULT NOW()
);

-- Reference data for platforms
CREATE TABLE platforms (
        id TEXT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE,
        tone VARCHAR(200),
        format VARCHAR(200),
        min_length INTEGER,
        max_length INTEGER,
        visual_requirements TEXT,
        created_at TIMESTAMP DEFAULT NOW()
);

-- Reference data for focus areas
CREATE TABLE focus_areas (
        id TEXT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        keywords JSONB,
        created_at TIMESTAMP DEFAULT NOW()
);

-- Reference data for visual types
CREATE TABLE visual_types (
        id TEXT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        recommended_tools JSONB,
        best_for TEXT,
        created_at TIMESTAMP DEFAULT NOW()
);
```

---
# Data Model: Personal AI Content Studio

**Feature**: Personal AI Content Studio MVP  
**Phase**: 1 (Design)  
**Date**: 2026-02-07

---

## Entities & Relationships

### 1. Session

**Purpose**: Represents a single user content creation workflow from topic intake to platform outputs.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | ✓ | Unique session identifier |
| `created_at` | Timestamp | ✓ | Session start time |
| `updated_at` | Timestamp | ✓ | Last update time |
| `status` | Enum | ✓ | [ `input` \| `outline_review` \| `framework_selection` \| `generating_content` \| `platform_review` \| `iterating` \| `completed` ] |
| `topic` | String (500 chars max) | ✓ | Original topic input (name, description, or URL) |
| `focus_area_match` | Array[String] | ✓ | Matched focus areas (AI, Cloud, etc.) or `['OUT_OF_SCOPE']` |
| `focus_area_confirmed` | Boolean | ✓ | User confirmed out-of-scope topic |
| `iteration_count` | Integer | ✓ | Number of refinement cycles completed (0 initially) |
| `completed_phrase` | String | - | The phrase "ok and good" when session ends |

**Relationships**:
- 1 Session → 1 Outline (current)
- 1 Session → N ValidationReport (history)
- 1 Session → 1 ContentDraft (final)
- 1 Session → N PlatformVersion (one per platform)

**Lifecycle**:
```
input → outline_review → (approval gate) → framework_selection → 
generating_content → platform_review → iterating → completed
```

---

### 2. Outline

**Purpose**: Structured content plan with content angle, sections, and factual validation results.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | ✓ | Unique outline identifier |
| `session_id` | UUID | ✓ | Foreign key to Session |
| `version` | Integer | ✓ | Outline version (1, 2, 3...) for regenerations |
| `content_angle` | String (500 chars) | ✓ | Why this angle matters and who it's for |
| `target_audience` | String (200 chars) | ✓ | Primary audience description |
| `primary_intent` | Enum | ✓ | [ `educate` \| `inspire` \| `guide` \| `entertain` \| `challenge` ] |
| `sections` | Array[String] | ✓ | Ordered list of outline sections (e.g., ["Hook", "Problem", "Solution", ...]) |
| `why_compelling` | String (1000 chars) | ✓ | Plain-language explanation of why this outline will resonate |
| `user_approved` | Boolean | ✓ | User explicitly approved before proceeding to framework selection |
| `approval_timestamp` | Timestamp | - | When user approved (or null if pending) |

**Relationships**:
- Many Outline → 1 Session (one session can have multiple outline versions)
- 1 Outline → 1 ValidationReport (fact-check results)

---

### 3. ValidationReport

**Purpose**: Tracks fact-checking results from web search and source credibility scoring.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | ✓ | Unique validation report ID |
| `outline_id` | UUID | ✓ | Foreign key to Outline |
| `confidence_score` | Float (0–1) | ✓ | Percentage of claims with credible sources (70% threshold) |
| `claims_checked` | Integer | ✓ | Total number of key claims extracted |
| `credible_sources_found` | Integer | ✓ | Number of claims with supporting sources |
| `sources` | Array[Object] | ✓ | List of sources checked: `{ url, title, credibility_score, claim_supported }` |
| `issues` | Array[Object] | - | List of problems found: `{ issue_type, description, severity }` |
| `passed_validation` | Boolean | ✓ | `confidence_score >= 0.70` |
| `validation_timestamp` | Timestamp | ✓ | When validation was performed |

**Relationships**:
- 1 ValidationReport → 1 Outline

---

### 4. ContentDraft

**Purpose**: The final narrative content before platform adaptation.

**Fields**:

| Field | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | UUID | ✓ | Unique content draft ID |
| `session_id` | UUID | ✓ | Foreign key to Session |
| `outline_id` | UUID | ✓ | Which outline was used |
| `framework_choice` | String | ✓ | Selected storytelling framework (TED, Hero's Journey, etc.) |
| `framework_explanation` | String (500 chars) | ✓ | Why this framework was recommended |
| `visual_plan` | Array[Object] | ✓ | List of visuals: `{ type, location, description, mermaid_code or svg_url }` |
| `body_text` | String (10,000 chars) | ✓ | Full narrative content (before platform adaptation) |
| `auto_generated_timestamp` | Timestamp | ✓ | When content was generated |
| `include_code` | Boolean | ✓ | Whether code examples are included |
| `code_snippets` | Array[Object] | - | If included: `{ language, code, explanation, expected_output }` |

**Relationships**:
- 1 ContentDraft → 1 Session
- 1 ContentDraft → 1 Outline

---

### 5. PlatformVersion

**Purpose**: Tailored output for a specific platform (LinkedIn, Twitter, Instagram, etc.).

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | ✓ | Unique platform version ID |
| `session_id` | UUID | ✓ | Foreign key to Session |
| `platform_name` | Enum | ✓ | [ `linkedin` \| `twitter` \| `reddit` \| `medium` \| `substack` \| `instagram` ] |
| `content` | String | ✓ | Platform-adapted text |
| `visual_references` | Array[String] | - | References to visuals (embedded or linked per platform norms) |
| `version` | Integer | ✓ | Which version of platform content (after iterations) |
| `generated_timestamp` | Timestamp | ✓ | When this version was generated |

**Relationships**:
- Many PlatformVersion → 1 Session

---

### 6. IterationFeedback

**Purpose**: Tracks user refinement requests and system responses.

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | UUID | ✓ | Unique feedback entry ID |
| `session_id` | UUID | ✓ | Foreign key to Session |
| `iteration_number` | Integer | ✓ | Which refinement cycle (1, 2, 3...) |
| `feedback_areas` | Array[String] | ✓ | User-selected areas: [ `tone` \| `depth` \| `visuals` \| `technicality` \| `humor` \| `examples` \| `structure` \| `other` ] |
| `freeform_feedback` | String (1000 chars) | - | User's custom feedback text |
| `affected_components` | Array[String] | ✓ | Which elements to regenerate (content, platform versions, visuals) |
| `regenerated_content` | String | - | Updated content after feedback |
| `platform_versions_updated` | Boolean | ✓ | Whether platform versions were regenerated |
| `feedback_timestamp` | Timestamp | ✓ | When feedback was submitted |

**Relationships**:
- Many IterationFeedback → 1 Session (multiple feedback rounds)

---

## Data Flow Diagram

```
[User Input]
    ↓
┌─────────────────────┐
│ Session Created     │
│ (status: input)     │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Outline Generated   │
│ (v1, v2, ... vN)    │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Validation Report   │   ← Web Search & Source Credibility
│ (70% threshold)     │
└─────────────────────┘
    ↓ (passed?)
    ├─ NO → Regenerate Outline (v2, loop)
    │
    └─ YES
        ↓
    ┌─────────────────────┐
    │ User Approves       │
    │ (outline_approved)  │
    └─────────────────────┘
        ↓
    ┌─────────────────────┐
    │ Framework Selected  │
    └─────────────────────┘
        ↓
    ┌─────────────────────┐
    │ Visual Plan         │
    │ Selected & Confirmed│
    └─────────────────────┘
        ↓
    ┌─────────────────────┐
    │ ContentDraft        │
    │ Generated           │
    └─────────────────────┘
        ↓
    ┌─────────────────────┐
    │ PlatformVersions    │   ← Per-platform tailoring
    │ (6 versions)        │       (LinkedIn, Twitter, Reddit, etc.)
    └─────────────────────┘
        ↓
    ┌─────────────────────┐
    │ User Reviews        │
    │ & Requests          │
    │ Feedback            │
    └─────────────────────┘
        ↓
    ├─ "ok and good"? → Session.completed_phrase set → END
    │
    └─ Improvement requested?
        → Regenerate affected content → Loop back to platform versions
```

---

## Storage Schema (SQLite)

**Note**: For local development only. Production uses **Azure Cosmos DB** (sessions) + **PostgreSQL** (reference data).

For details on Cosmos DB and PostgreSQL schema, see "Storage Architecture: Azure Cosmos DB + PostgreSQL" section above.

---

## State Management (LangGraph)

**SessionState** (managed by LangGraph):

```python
@dataclass
class SessionState:
    session_id: str
    topic_input: str
    focus_areas: List[str]
    outline: Outline  # Current version
    validation_report: ValidationReport
    outline_approved: bool
    framework_choice: str
    visual_plan: List[Dict]
    content_draft: ContentDraft
    platform_versions: Dict[str, str]  # platform → content
    iteration_count: int
    completed: bool
    messages: List[Dict]  # Audit trail
```

Each agent reads from `SessionState`, performs its task, and updates state. LangGraph persists state to Database after each agent completes.

---

## Validation Rules

- **Topic Input**: Non-empty, max 500 chars, or valid URL.
- **Outline**: Must have 3–7 sections; `why_compelling` must be non-empty.
- **ValidationReport**: `confidence_score >= 0.70` required to proceed.
- **Framework Choice**: Must be one of 6 predefined or `custom`.
- **ContentDraft**: `body_text` must be non-empty, >= 200 chars.
- **PlatformVersion**: Platform-specific minimum length (LinkedIn ≥ 300 chars, Twitter ≥ 280 chars per tweet, etc.).
- **IterationFeedback**: At least one feedback area selected; cannot have `completed_phrase` set until user says "ok and good".

---

## Relationships Summary

```
Session (1)
├── Outline (multiple versions)
│   └── ValidationReport (1 per outline)
├── ContentDraft (1, uses latest approved outline)
├── PlatformVersion (up to 6: LinkedIn, Twitter, Reddit, Medium, Substack, Instagram)
└── IterationFeedback (multiple rounds)
```

All entities are timestamped for audit, versioned for recovery, and linked to Session for traceability.
