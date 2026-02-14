## Agent: Research & Validation Agent

**Role**: Validate outline claims via web search and credibility scoring.  
**Input**: Outline with sections and claims  
**Output**: Validation report with confidence score  

### Input Schema

```json
{
  "session_id": "uuid",
  "outline_version": 1,
  "sections": [
    { "title": "string", "description": "string" },
    ...
  ]
}
```

### Output Schema

```json
{
  "session_id": "uuid",
  "outline_version": 1,
  "validation_id": "uuid",
  "confidence_score": "float(0-1)",
  "claims_checked": "integer",
  "credible_sources_found": "integer",
  "sources": [
    {
      "url": "string",
      "title": "string",
      "domain": "string",
      "claim_supported": true,
      "credibility_score": "float(0-1)"
    },
    ...
  ],
  "issues": [
    {
      "severity": "enum[low | medium | high]",
      "claim": "string",
      "issue_type": "enum[no_sources | weak_sources | conflicting_sources | outdated]",
      "description": "string"
    },
    ...
  ],
  "passed_validation": "boolean (confidence_score >= 0.70)",
  "recommendations": "string (if failed, how to improve)"
}
```

### Behavior

- Extract key claims from outline sections using **Claude 3.5 Sonnet** (structured output).
- For each claim, perform 2–3 web searches using **Bing Search API** (Azure Cognitive Services).
- Score credibility of sources (prefer official, peer-reviewed, recent).
- Use **Llama 3.1** (Azure AI Foundry) for source classification and credibility scoring (cost-effective).
- Calculate `confidence_score = credible_sources / total_claims`.
- If `confidence_score >= 0.70` → `passed_validation = true`.
- Flag weak, conflicting, or outdated claims for user awareness.
- Return sources + issues list for transparency.

**LLM Model Routing**:
- **Claim extraction**: Claude 3.5 Sonnet (Anthropic API or GitHub Copilot) for JSON parsing
- **Source classification**: Llama 3.1 (Azure AI Foundry) for credibility scoring (cost-effective)
- **Fallback**: GPT-4 Turbo if primary models unavailable

### Thresholds

- `credibility_score >= 0.8` per source → credible.
- `credibility_score 0.5–0.8` → medium; requires additional verification.
- `credibility_score < 0.5` → low; flag as weak source.

### Error Handling

- Web search unavailable → Return error + ask to retry.
- No sources found for all claims → `passed_validation = false` + recommend outline revision.
- Too few sources for depth requested → Flag depth mismatch.
- Conflicting sources → Return both perspectives; let user decide.
