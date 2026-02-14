## Session Management API

**Role**: Orchestrate session state and coordinate agent calls.  
**Protocol**: REST or GraphQL (FastAPI backend, Streamlit frontend)  
**Base URL**: `http://localhost:8000/api/v1` (dev) or production endpoint  

---

## Core Endpoints

### POST `/sessions`

**Purpose**: Create a new session.

**Request**:
```json
{
  "topic_input": "string (topic name, description, or URL)",
  "optional_context": "string (optional)"
}
```

**Response** (201 Created):
```json
{
  "session_id": "uuid",
  "status": "input",
  "created_at": "ISO8601 timestamp",
  "next_step": "Provide topic for analysis"
}
```

---

### GET `/sessions/{session_id}`

**Purpose**: Retrieve session state.

**Response** (200 OK):
```json
{
  "session_id": "uuid",
  "status": "enum[input | outline_review | framework_selection | ...]",
  "topic": "string",
  "focus_area_match": ["array"],
  "outline": { "...outline object..." },
  "validation_report": { "...validation object..." },
  "content_draft": { "...content object or null..." },
  "platform_versions": [{ "...platform object..." }],
  "iteration_count": "integer",
  "completed": "boolean"
}
```

---

### POST `/sessions/{session_id}/outline/generate`

**Purpose**: Trigger outline generation and validation.

**Request**:
```json
{
  "regenerate": "boolean (true to skip outline history)"
}
```

**Response** (200 OK):
```json
{
  "session_id": "uuid",
  "outline": { "...outline object..." },
  "validation_report": { "...validation object..." },
  "passed_validation": "boolean",
  "status": "outline_review",
  "next_action": "User approves outline or regenerates"
}
```

---

### POST `/sessions/{session_id}/outline/approve`

**Purpose**: User approves outline.

**Request**:
```json
{
  "approved": "boolean",
  "comments": "string (optional)"
}
```

**Response** (200 OK):
```json
{
  "session_id": "uuid",
  "outline_approved": true,
  "status": "framework_selection",
  "available_frameworks": ["ted", "heros_journey", ...],
  "recommended_framework": "string"
}
```

---

### POST `/sessions/{session_id}/framework/select`

**Purpose**: User selects storytelling framework.

**Request**:
```json
{
  "framework_choice": "string",
  "visual_preferences": ["array of visual types or empty"]
}
```

**Response** (200 OK):
```json
{
  "session_id": "uuid",
  "framework_choice": "string",
  "visual_plan": [{ "...visual object..." }],
  "status": "generating_content",
  "next_action": "Content generation in progress"
}
```

---

### POST `/sessions/{session_id}/content/generate`

**Purpose**: Generate final content draft.

**Request**:
```json
{
  "include_code": "boolean (optional)"
}
```

**Response** (200 OK):
```json
{
  "session_id": "uuid",
  "content_draft": { "...content object..." },
  "status": "platform_review",
  "next_action": "Platform versions generating"
}
```

---

### POST `/sessions/{session_id}/platforms/generate`

**Purpose**: Generate platform-specific versions.

**Request**:
```json
{
  "platforms": ["linkedin", "twitter", "reddit", "medium", "substack", "instagram"]
}
```

**Response** (200 OK):
```json
{
  "session_id": "uuid",
  "platform_versions": [
    { "platform": "linkedin", "content": "string", "..." },
    ...
  ],
  "status": "platform_review",
  "next_action": "User reviews or requests improvements"
}
```

---

### POST `/sessions/{session_id}/feedback`

**Purpose**: Submit refinement feedback.

**Request**:
```json
{
  "feedback_areas": ["tone", "depth", "visuals", ...],
  "freeform_feedback": "string",
  "affected_components": ["content", "platform_versions", "visuals"]
}
```

**Response** (200 OK):
```json
{
  "session_id": "uuid",
  "iteration_number": "integer",
  "status": "iterating",
  "regenerated_content": "boolean",
  "updated_platform_versions": "boolean",
  "next_action": "Review updated versions or submit more feedback"
}
```

---

### POST `/sessions/{session_id}/complete`

**Purpose**: Mark session as complete.

**Request**:
```json
{
  "completion_phrase": "string (must be 'ok and good')"
}
```

**Response** (200 OK):
```json
{
  "session_id": "uuid",
  "status": "completed",
  "completed_at": "ISO8601 timestamp",
  "summary": "string (session summary)"
}
```

---

### GET `/sessions`

**Purpose**: List all sessions (filterable by date, status).

**Query Parameters**:
- `status`: Filter by session status
- `start_date`: ISO8601 datetime
- `end_date`: ISO8601 datetime
- `limit`: Max results (default 10)

**Response** (200 OK):
```json
{
  "sessions": [
    { "session_id": "uuid", "created_at": "...", "status": "...", "topic": "..." },
    ...
  ],
  "total_count": "integer"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "INVALID_REQUEST",
  "message": "string (describes the problem)",
  "details": { "...optional details..." }
}
```

### 404 Not Found
```json
{
  "error": "SESSION_NOT_FOUND",
  "message": "Session {session_id} does not exist"
}
```

### 422 Unprocessable Entity
```json
{
  "error": "VALIDATION_FAILED",
  "message": "Outline confidence < 70%",
  "field": "validation_report.confidence_score",
  "details": { "...details..." }
}
```

### 500 Internal Server Error
```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred",
  "request_id": "uuid (for debugging)"
}
```

---

## Authentication & Rate Limiting

- **Auth**: None (single-user MVP; no authentication required).
- **Rate Limiting**: Not enforced (single user assumption).
- **CORS**: Enabled for `localhost:3000`, `localhost:8501` (Streamlit/Next.js).

---

## Session State Diagram (API Flow)

```
POST /sessions
  ↓
GET /sessions/{id}
  ↓ (topic extracted, focus area checked)
POST /{id}/outline/generate
  ↓ (outline + validation)
POST /{id}/outline/approve
  ↓ (user approves)
POST /{id}/framework/select
  ↓ (framework + visuals selected)
POST /{id}/content/generate
  ↓ (content drafted)
POST /{id}/platforms/generate
  ↓ (platform versions created)
POST /{id}/feedback (loop allowed)
  ↓
POST /{id}/complete (when "ok and good")
```
