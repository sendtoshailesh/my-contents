# Backend Agents Module

Implementation of agents for the Personal AI Content Studio MVP 1 (Phase 3, User Story 1).

## Overview

The agents module provides automated content outline generation through two main agents:

1. **InputAgent (T021-T024)** - Extracts topic metadata and determines focus area
2. **ReasoningAgent (T025-T028)** - Generates compelling content outlines

Together, they form the critical path for MVP 1: **User Topic → Outline Approval**

## Architecture

```
User Input (topic string)
        ↓
InputAgent.extract_topic_info()
  → Uses Llama 3.1 (classification task)
  → Returns: topic_data dict
        ↓
ReasoningAgent.generate_outline()
  → Uses GPT-4 Turbo (reasoning task)
  → Returns: outline dict with sections
        ↓
Outline Ready for Approval
```

## InputAgent (T021-T024)

### Purpose
- Extract topic, audience, intent from user input
- Match to focus areas (AI, Cloud, Migration, Emotional Intelligence, Emerging Tech)
- Warn if OUT_OF_SCOPE but allow override

### Usage

```python
from backend.agents.input_agent import get_input_agent

# Get singleton instance
agent = get_input_agent()

# Extract topic information
topic_data = agent.extract_topic_info("AI in healthcare")

# Returns:
# {
#     'topic': 'AI in healthcare',
#     'theme': 'How artificial intelligence is transforming medical diagnosis...',
#     'audience': 'Hospital administrators and medical professionals',
#     'intent': 'inform',
#     'focus_area': 'AI',  # or 'OUT_OF_SCOPE'
#     'is_out_of_scope': False,
#     'warning': None,
#     'confidence': 0.95,
#     'detected_focus_area_raw': 'AI'
# }
```

### Methods

#### `extract_topic_info(topic: str) -> Dict`
Extracts topic metadata using Llama 3.1 classification.

**Parameters:**
- `topic` (str): User-provided topic (e.g., "AI in healthcare")

**Returns:**
- Dictionary with keys:
  - `topic`: Original topic string
  - `theme`: What this is really about (single sentence)
  - `audience`: Target audience description
  - `intent`: Primary intent (inform, persuade, entertain, guide, challenge)
  - `focus_area`: Matched focus area ID or "OUT_OF_SCOPE"
  - `is_out_of_scope`: Boolean flag
  - `warning`: Warning message if out-of-scope, None otherwise
  - `confidence`: Match confidence (0.0-1.0)
  - `detected_focus_area_raw`: Raw LLM-detected focus area

**Example:**
```python
agent = get_input_agent()
result = agent.extract_topic_info("Quantum computing basics")
print(f"Focus Area: {result['focus_area']}")  # EMERGING_TECH
print(f"Confidence: {result['confidence']:.0%}")  # 85%
```

#### `match_focus_area(detected_area: str) -> Tuple[str, float]`
Matches detected focus area to reference data using keyword matching.

**Parameters:**
- `detected_area` (str): Focus area detected by LLM

**Returns:**
- Tuple of (focus_area_id, confidence)
  - `focus_area_id`: ID from reference data or "OUT_OF_SCOPE"
  - `confidence`: Match confidence (0.0-1.0)

**Example:**
```python
agent = get_input_agent()
area, conf = agent.match_focus_area("Machine Learning")
# Returns: ("AI", 0.9)
```

## ReasoningAgent (T025-T028)

### Purpose
- Generate outline from topic_data using GPT-4 Turbo
- Create 4-6 outline sections with titles and descriptions
- Specify content_angle (why this angle matters)
- Return structured outline with all metadata

### Usage

```python
from backend.agents.reasoning_agent import get_reasoning_agent

# Get singleton instance
agent = get_reasoning_agent()

# Generate outline from topic_data
topic_data = {
    'topic': 'AI in healthcare',
    'theme': 'How AI is transforming medical diagnosis',
    'audience': 'Hospital administrators',
    'intent': 'inform',
    'focus_area': 'AI'
}

outline = agent.generate_outline(topic_data)

# Returns:
# {
#     'topic': 'AI in healthcare',
#     'sections': [
#         {
#             'title': 'The Healthcare Diagnosis Challenge',
#             'description': 'Current limitations in diagnosis speed...',
#             'order': 1
#         },
#         ...
#     ],
#     'content_angle': 'Why AI is transforming healthcare through early diagnosis',
#     'target_audience': 'Hospital administrators',
#     'primary_intent': 'inform',
#     'num_sections': 5,
#     'outline_rationale': 'Structure moves from problem to solution...',
#     'why_this_matters': 'Early diagnosis saves lives and reduces costs'
# }
```

### Methods

#### `generate_outline(topic_data: Dict) -> Dict`
Generates detailed content outline using GPT-4 Turbo reasoning.

**Parameters:**
- `topic_data` (dict): Dictionary from InputAgent with keys:
  - `topic` (str): Original topic
  - `theme` (str): What this is about
  - `audience` (str): Target audience
  - `intent` (str): Primary intent
  - `focus_area` (str): Focus area ID or "OUT_OF_SCOPE"
  - `is_out_of_scope` (bool): Out-of-scope flag

**Returns:**
- Dictionary with keys:
  - `topic`: Original topic string
  - `sections`: List of section dicts (4-6 sections)
  - `content_angle`: Compelling reason why this angle works
  - `target_audience`: Target audience string
  - `primary_intent`: Primary intent
  - `num_sections`: Number of sections
  - `outline_rationale`: Explanation of section structure
  - `why_this_matters`: Why this topic/angle matters

**Example:**
```python
agent = get_reasoning_agent()
outline = agent.generate_outline(topic_data)
for section in outline['sections']:
    print(f"{section['order']}. {section['title']}")
```

#### `validate_outline(outline: Dict) -> bool`
Validates outline structure completeness and correctness.

**Parameters:**
- `outline` (dict): Outline dictionary to validate

**Returns:**
- True if valid, False otherwise

**Validation Checks:**
- All required fields present
- At least 4 sections
- Each section has title and description

## Integration Example

Use `ContentOutlineWorkflow` for end-to-end processing:

```python
from backend.agents.integration import ContentOutlineWorkflow

workflow = ContentOutlineWorkflow()

# Process single topic
outline = workflow.process_topic("AI in healthcare")
if outline:
    print(f"Generated {outline['num_sections']} sections")
    for section in outline['sections']:
        print(f"  - {section['title']}")

# Process batch of topics
topics = [
    "Cloud migration strategies",
    "Emotional intelligence in leadership",
    "Quantum computing fundamentals"
]
outlines = workflow.process_topics_batch(topics)
```

## Focus Areas

The system classifies topics into these focus areas:

| ID | Name | Keywords | Examples |
|----|------|----------|----------|
| AI | Artificial Intelligence | AI, ML, deep learning, neural, LLM | AI in healthcare, machine learning basics |
| CLOUD | Cloud Computing | Cloud, Azure, AWS, serverless, containers | Cloud migration, containerization |
| MIGRATION | Migration | Migration, upgrade, refactor, modernization | Legacy modernization, system upgrade |
| EI | Emotional Intelligence | Emotional, empathy, wellness, leadership | Leadership development, team dynamics |
| EMERGING | Emerging Tech | Quantum, blockchain, metaverse, IoT | Quantum computing, blockchain basics |

## Intent Types

Topics can have different primary intents:

- **inform**: Provide information and knowledge
- **persuade**: Convince audience to adopt a viewpoint
- **entertain**: Engage and entertain audience
- **guide**: Provide step-by-step guidance
- **challenge**: Challenge assumptions or conventional thinking

## Error Handling

### Out-of-Scope Topics
When a topic doesn't match any focus area:
- InputAgent sets `is_out_of_scope=True` with warning message
- ReasoningAgent can still generate outline (if allowed by caller)
- Use `allow_out_of_scope=True` in workflow to override

### JSON Parsing Failures
Both agents gracefully handle LLM response parsing:
- Removes markdown code blocks automatically
- Falls back to default structure if JSON invalid
- Logs warnings for debugging

## Testing

Run the test suite:

```bash
# Run all agent tests
python -m pytest tests/test_agents.py -v

# Run specific test class
python -m pytest tests/test_agents.py::TestInputAgentTopicExtraction -v

# Run with coverage
python -m pytest tests/test_agents.py --cov=backend.agents
```

### Test Coverage

- **T021-T022**: Topic extraction with various topics
- **T023-T024**: Focus area matching and out-of-scope detection
- **T025-T027**: Outline generation with different intents
- **T028**: Outline validation
- Integration tests: Full workflow from topic to outline
- JSON parsing: Handles various LLM response formats

## Configuration

### Environment Variables

Required (set via secrets service):
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `AZURE_AI_KEY`: Azure OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)

### Secrets Management

Secrets are managed through hybrid service:
1. **Primary**: OS Keychain (via keyring library)
2. **Fallback**: Azure Key Vault

Set up secrets:
```bash
python scripts/setup_secrets.py
```

## Model Selection

The agents use ModelRouter for optimal model selection:

| Agent | Task Type | Model | Reason |
|-------|-----------|-------|--------|
| InputAgent | Classification | Llama 3.1 | Cost-effective topic extraction |
| ReasoningAgent | Reasoning | GPT-4 Turbo | Complex reasoning for outline generation |

Temperature settings:
- Classification: 0.3 (factual)
- Reasoning: 0.7 (creative)

## Troubleshooting

### "Topic extraction failed"
- Check LLM service connectivity
- Verify API keys in secrets
- Review logs for LLM response content

### "No focus area match"
- Topic may not fit current categories
- Check if intent is recognized (inform, persuade, etc.)
- Enable `allow_out_of_scope=True` to proceed anyway

### "Outline validation failed"
- Verify outline has 4-6 sections
- Check section structure (title, description required)
- Review LLM response for formatting issues

## Future Enhancements

- [ ] **Research Agent**: Fact-checking and source gathering
- [ ] **Orchestration Agent**: Workflow coordination
- [ ] **Content Generation Agent**: Transform outline to full content
- [ ] **Visual Agent**: Generate diagrams and visualizations
- [ ] **Storytelling Agent**: Narrative structure and arc
- [ ] **Multi-language support**: Translate outlines to other languages
- [ ] **Outline refinement**: User feedback loop to improve outlines

## API Reference

### InputAgent

```python
class InputAgent:
    def __init__(self)
    def extract_topic_info(topic: str) -> Dict
    def match_focus_area(detected_area: str) -> Tuple[str, float]
    
def get_input_agent() -> InputAgent  # Singleton
```

### ReasoningAgent

```python
class ReasoningAgent:
    def __init__(self)
    def generate_outline(topic_data: Dict) -> Dict
    def validate_outline(outline: Dict) -> bool
    
def get_reasoning_agent() -> ReasoningAgent  # Singleton
```

### ContentOutlineWorkflow

```python
class ContentOutlineWorkflow:
    def __init__(self)
    def process_topic(topic: str, allow_out_of_scope: bool = False) -> Optional[Dict]
    def process_topics_batch(topics: list[str]) -> list[Dict]
```

## References

- **Tasks Implemented**: T021-T028 (Phase 3, User Story 1)
- **Critical Path**: User Topic → InputAgent → ReasoningAgent → Outline Approval
- **Related Contracts**:
  - [Input Agent Contract](../specs/001-content-spec-constitution/contracts/input-agent.md)
  - [Reasoning Agent Contract](../specs/001-content-spec-constitution/contracts/reasoning-agent.md)
