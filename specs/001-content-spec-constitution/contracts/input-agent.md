## Agent: Input Agent

**Role**: Parse user input and extract topic metadata.  
**Input**: User-provided topic (name, description, or URL)  
**Output**: Structured topic data + focus area classification  

### Input Schema

```json
{
  "input_type": "enum[topic_name | topic_description | url]",
  "content": "string (max 500 chars or valid URL)",
  "optional_context": "string (max 500 chars)"
}
```

### Output Schema

```json
{
  "session_id": "uuid",
  "topic": "string (max 500 chars)",
  "topic_type": "enum[topic_name | topic_description | url]",
  "extracted_theme": "string",
  "estimated_audience": "string",
  "content_intent": "Enum[educate | inspire | guide | entertain | challenge]",
  "desired_depth": "Enum[introductory | intermediate | advanced | expert]",
  "focus_area_match": "array[string] or ['OUT_OF_SCOPE']",
  "confidence": "float(0-1)"
}
```

### Behavior

- If `input_type` is `url`, fetch and summarize content.
- Extract theme, audience, intent, depth from content or user description.
- Classify against focus areas using LLM (with curated list).
- Return focus areas if match found; else `['OUT_OF_SCOPE']`.
- Always return a session ID (generated or provided).

### Error Handling

- Invalid URL → Graceful error + ask for alternative.
- Empty input → Prompt user to provide topic.
- Ambiguous topic → Provide clarification suggestions.
