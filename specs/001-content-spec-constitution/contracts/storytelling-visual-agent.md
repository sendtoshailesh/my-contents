## Agent: Storytelling & Visual Agent

**Role**: Apply storytelling framework and generate visual recommendations.  
**Input**: Approved outline + user framework choice  
**Output**: Content structure with visuals + framework mapping  

### Input Schema

```json
{
  "session_id": "uuid",
  "outline_id": "uuid",
  "framework_choice": "enum[ted | heros_journey | problem_solution_impact | aida | before_after_bridge | custom]",
  "outline_sections": [
    { "section_number": 1, "title": "string", "description": "string" },
    ...
  ],
  "visual_preferences": ["array of visual types or empty for recommendations"]
}
```

### Output Schema

```json
{
  "session_id": "uuid",
  "outline_id": "uuid",
  "framework_choice": "string",
  "framework_explanation": "string (max 500 chars)",
  "framework_structure": [
    { "framework_step": 1, "outline_section": 1, "title": "string" },
    ...
  ],
  "visual_plan": [
    {
      "visual_id": 1,
      "type": "enum[flowchart | architecture | infographic | timeline | comic | mental_model | graph | other]",
      "location": "enum[section_1 | section_2 | ... | appendix]",
      "recommended_tool": "enum[mermaid | plantuml | svg | python | other]",
      "description": "string (what the visual explains)",
      "draft_code": "string (Mermaid/SVG/PlantUML code or placeholder)"
    },
    ...
  ],
  "total_visuals": "integer",
  "opt_out_visuals": "boolean (user may opt out)"
}
```

### Behavior

- Map framework steps to outline sections (may reorder or combine).
- Generate 2–4 visual recommendations based on content type.
- Suggest visual tools (Mermaid for flowcharts, PlantUML for architecture, etc.).
- Provide `draft_code` as a starting point (user can customize).
- Always return `opt_out_visuals = false` (system default: require ≥1 visual).
- If user opts out, update `opt_out_visuals = true` and proceed without visuals.

**LLM Model Routing**:
- **Framework mapping**: GPT-4 Turbo (Azure AI Foundry) for complex reasoning and creative structure
- **Visual recommendations**: GPT-4 Turbo or Claude 3.5 Sonnet for diverse visual strategies
- **Mermaid/PlantUML generation**: GitHub Copilot (Codex) for diagram code generation
- **Fallback**: Claude 3.5 Sonnet if GPT-4 unavailable
- **Temperature**: 0.7 (creative task; allow flexibility in framework application)

### Framework Templates

**TED**: Hook → Context → Insight → Implication → Call-to-action  
**Hero's Journey**: Call to Adventure → Refusal → Meeting the Mentor → Crossing Threshold → Tests → Reward → Return  
**Problem → Solution → Impact**: Problem Setup → Solution Overview → Detailed Steps → Real-world Impact → Takeaways  
**AIDA**: Attention → Interest → Desire → Action  
**Before–After–Bridge**: Current State → Vision → How to Bridge → Action Steps  
**Custom**: User provides structure  

### Error Handling

- Framework not found → Return default (TED) + note.
- Visual recommendation fails → Offer alternatives.
- User opts out → Proceed without visuals (but allow re-add during iteration).
