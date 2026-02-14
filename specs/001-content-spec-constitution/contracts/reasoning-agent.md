## Agent: Reasoning Agent

**Role**: Generate compelling content angle and outline structure.  
**Input**: Extracted topic metadata  
**Output**: Content angle + structured outline with rationale  

### Input Schema

```json
{
  "session_id": "uuid",
  "topic": "string",
  "extracted_theme": "string",
  "estimated_audience": "string",
  "content_intent": "enum[educate | inspire | guide | entertain | challenge]",
  "desired_depth": "enum[introductory | intermediate | advanced | expert]"
}
```

### Output Schema

```json
{
  "session_id": "uuid",
  "outline_version": 1,
  "content_angle": "string (max 500 chars)",
  "target_audience": "string (max 200 chars)",
  "primary_intent": "enum[educate | inspire | guide | entertain | challenge]",
  "why_this_matters": "string (max 500 chars)",
  "why_compelling": "string (max 1000 chars)",
  "sections": [
    { "section_number": 1, "title": "string", "description": "string" },
    ...
  ],
  "unique_angle": "string (what makes this different)"
}
```

### Behavior

- Perform first-principles reasoning on topic.
- Suggest unique angle that hasn't been covered extensively (if possible).
- Map intent to outline structure (e.g., `guide` → Step-by-step sections; `inspire` → Story arc).
- Return 5–7 sections as a logical flow.
- Provide `why_compelling` in plain language (why will this resonate with the audience).

### Error Handling

- Topic too vague → Ask for clarification.
- Unable to generate unique angle → Return solid angle anyway + note limitations.
- Depth mismatch → Adjust section complexity and suggest depth adjustment.
