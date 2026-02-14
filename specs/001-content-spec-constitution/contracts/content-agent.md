## Agent: Content Generation Agent

**Role**: Synthesize final narrative content using approved outline, framework, and visuals.  
**Input**: Approved outline + framework structure + visual plan  
**Output**: Full content draft ready for platform adaptation  

### Input Schema

```json
{
  "session_id": "uuid",
  "outline_id": "uuid",
  "framework_choice": "string",
  "framework_structure": [
    { "framework_step": 1, "section": "string" },
    ...
  ],
  "visual_plan": [
    { "visual_id": 1, "type": "string", "description": "string" },
    ...
  ],
  "include_code": "boolean",
  "code_preferences": "object (optional: language, complexity)"
}
```

### Output Schema

```json
{
  "session_id": "uuid",
  "outline_id": "uuid",
  "framework_choice": "string",
  "body_text": "string (2000–5000 words)",
  "visual_integration_points": [
    { "visual_id": 1, "placement": "after_section_2", "caption": "string" },
    ...
  ],
  "code_snippets": [
    {
      "section": "integer",
      "language": "enum[python | javascript | react | sql | other]",
      "code": "string",
      "explanation": "string",
      "expected_output": "string"
    }
  ],
  "content_quality_score": "float(0-1)",
  "warnings": ["array of optional warnings (e.g., 'Assumed intermediate knowledge')"]
}
```

### Behavior

- Generate narrative following the framework structure.
- Weave in insights and examples from the outline.
- Insert visual references (e.g., "[See Visual 1: Flow diagram]").
- If `include_code = true`, generate code examples relevant to topic.
- Ensure clarity and conciseness; avoid jargon unless appropriate.
- Target word count: 2000–5000 words for base content.
- Return `content_quality_score` (self-assessment of quality).

**LLM Model Routing**:
- **Narrative synthesis**: GPT-4 Turbo (Azure AI Foundry) for creative writing and storytelling (primary)
- **Alternative**: Claude 3.5 Sonnet (Anthropic API) for structured, factual content
- **Code generation**: GitHub Copilot (Codex) for code snippets and explanations
- **Self-assessment**: Llama 3.1 (Azure AI Foundry) for basic quality scoring (cost-effective)
- **Fallback**: GPT-4 Turbo if Claude unavailable
- **Temperature**: 0.7 (creative task; allow natural language variation)

### Content Guidelines

- Use active voice.
- Keep paragraphs short (2–4 sentences).
- Use headers to structure sections.
- Provide concrete examples or case studies.
- Conclude with actionable takeaways.

### Code Snippet Rules

- Include comments in code.
- Provide expected output or sample run results.
- Limit to 1–3 snippets per content piece (keep content focused).
- Support Python, JavaScript, React, SQL, Mermaid, PlantUML.

### Error Handling

- Framework mismatch → Log warning + adjust content structure.
- Missing visual descriptions → Use placeholder + flag for manual review.
- Content too short or too long → Warn but proceed (user can refine).
