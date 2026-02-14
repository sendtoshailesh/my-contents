## Agent: Platform Formatter Agent

**Role**: Adapt content draft to platform-specific formats and tones.  
**Input**: Content draft + target platform(s)  
**Output**: Platform-specific content versions  

### Input Schema

```json
{
  "session_id": "uuid",
  "content_draft_id": "uuid",
  "body_text": "string",
  "visual_plan": [array of visuals],
  "target_platforms": [
    "enum[linkedin | twitter | reddit | medium | substack | instagram]"
  ]
}
```

### Output Schema

```json
{
  "session_id": "uuid",
  "platform_versions": [
    {
      "platform": "enum[linkedin | twitter | reddit | medium | substack | instagram]",
      "content": "string",
      "tone": "string (e.g., 'professional, thought-leadership')",
      "format": "string (e.g., 'thread, article, carousel')",
      "changes_made": "string (summary of adaptations)",
      "visual_references": ["array of visual placements"]
    },
    ...
  ]
}
```

### Platform Specifications

#### LinkedIn
- **Tone**: Professional, thought leadership
- **Format**: 1–3 paragraphs or article link
- **Length**: 500–1500 chars
- **Visuals**: Embedded images or linked articles
- **Key Elements**: Actionable insights, professional language, engagement hook

#### Twitter/X
- **Tone**: Punchy, conversational
- **Format**: Thread (5–10 connected tweets) or standalone
- **Length**: 280 chars per tweet
- **Visuals**: Link to visual (not embedded in tweet logic)
- **Key Elements**: Hook, short sentences, trending hashtags, call-to-retweet

#### Reddit
- **Tone**: Discussion-oriented, authentic
- **Format**: Post + discussion starter
- **Length**: 1000–3000 chars
- **Visuals**: Links or inline descriptions
- **Key Elements**: Community awareness, original opinion, source links, discussion prompts

#### Medium / Substack
- **Tone**: Long-form, narrative-rich
- **Format**: Full article with sections
- **Length**: 2000–5000 words
- **Visuals**: Embedded images, code blocks, diagrams
- **Key Elements**: Depth, examples, personal voice, clear takeaways

#### Instagram
- **Tone**: Casual, visual-first
- **Format**: Carousel captions (5–7 slides)
- **Length**: 200–300 chars per slide
- **Visuals**: Carousel images (Instagram-friendly aspect ratio)
- **Key Elements**: Emoji-friendly, visual hooks, one idea per slide, call-to-action

### Behavior

- For each platform, apply format rules (length, tone, structure).
- Extract or adapt visuals for platform norms (e.g., LinkedIn article link vs. Instagram carousel).
- For **Twitter**, break content into tweet-sized chunks with thread markers.
- For **Instagram**, suggest 5–7 visual slide titles that map to content sections.
- For **Medium/Substack**, preserve article structure + integrate visuals.
- Return `changes_made` summary (helps user understand adaptations).

### Error Handling

- Platform unsupported → Return error + suggest closest alternative.
- Content too long for platform → Truncate intelligently + flag.
- Visual mismatch → Suggest platform-appropriate alternatives.
