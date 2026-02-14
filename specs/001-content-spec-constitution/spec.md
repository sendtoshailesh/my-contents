# Feature Specification: Personal AI Content Studio Spec and Constitution

**Feature Branch**: `001-content-spec-constitution`  
**Created**: 2026-02-07  
**Status**: Draft  
**Input**: User description: "follow on spec given in file #file:global-spec.md  file create detailed spec and also create constition."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Approve a validated outline (Priority: P1)

As a single user, I want to enter a topic or URL and receive a fact-checked outline with a clear rationale so I can approve or restart before any content is generated.

**Why this priority**: This is the core value gate that ensures accuracy and relevance before any content exists.

**Independent Test**: Can be fully tested by submitting a topic and confirming that the system returns a validated outline, sources, and an approval decision without generating final content.

**Acceptance Scenarios**:

1. **Given** a topic name or URL, **When** I submit it, **Then** the system returns a structured outline, a content angle, and why it is compelling.
2. **Given** the outline and validation results, **When** I select restart or modify, **Then** the system regenerates or updates the outline before proceeding.
3. **Given** validation confidence is below the threshold, **When** I request to proceed, **Then** the system blocks progression and asks for a new outline.

---

### User Story 2 - Generate content with chosen framework and visuals (Priority: P2)

As a single user, I want to pick a storytelling framework and a visual strategy so the final content is compelling, concise, and easy to grasp.

**Why this priority**: The content must be both engaging and efficient for social channels and blogs.

**Independent Test**: Can be fully tested by approving an outline, selecting a framework and visuals, and verifying a final draft with visuals and sections.

**Acceptance Scenarios**:

1. **Given** an approved outline, **When** I choose a framework and visual style, **Then** the system generates a structured draft that follows that framework and includes the chosen visuals.
2. **Given** the topic requires code, **When** I request code, **Then** the system includes code, a brief explanation, and expected output.

---

### User Story 3 - Adapt outputs per platform and iterate (Priority: P3)

As a single user, I want platform-specific versions and an improvement loop so I can refine the content until I say "ok and good".

**Why this priority**: Each platform has distinct expectations and the user wants iterative control.

**Independent Test**: Can be fully tested by generating at least one platform version and completing a feedback loop to completion.

**Acceptance Scenarios**:

1. **Given** a final draft, **When** I request platform outputs, **Then** the system produces versions for each specified platform with appropriate tone and format.
2. **Given** a generated version, **When** I request improvements, **Then** the system asks for improvement areas and iterates until I respond with "ok and good".

### Edge Cases

- URL is inaccessible or content is paywalled.
- Validation sources conflict or are outdated.
- User declines approval multiple times and wants a restart.
- Topic is outside the allowed focus areas.
- Visual type requested cannot be produced; system must offer alternatives.
- User keeps iterating beyond typical refinement cycles.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a topic name, topic with description, or a URL as input.
- **FR-002**: System MUST extract a core theme, target audience, content intent, and desired depth from the input.
- **FR-003**: System MUST generate a compelling content angle and an outline using deep reasoning about relevance and audience value.
- **FR-004**: System MUST validate outline claims using multiple independent public sources and report a confidence score.
- **FR-005**: System MUST block progression when validation confidence is below 70% and require outline regeneration before any final content is generated.
- **FR-006**: System MUST present the outline, supporting sources, and why the outline is compelling before any final content is generated.
- **FR-007**: System MUST require explicit user approval (approve, modify, restart) to proceed beyond the outline stage.
- **FR-008**: System MUST recommend a storytelling framework based on the topic type and content angle, and allow the user to override with their choice from available frameworks (TED, Hero's Journey, Problem → Solution → Impact, AIDA, Before–After–Bridge, or Custom).
- **FR-009**: System MUST propose and apply a visual strategy that reduces text length and clarifies the concept, including at least one visual in the final content unless the user explicitly opts out.
- **FR-010**: System MUST generate code, explanation, and expected output only when the user explicitly requests code or approves an outline section marked for code.
- **FR-011**: System MUST generate platform-specific versions for LinkedIn, Twitter/X, Reddit, Medium, Substack, and Instagram automatically using platform templates, and present them to the user for review and adjustment.
- **FR-012**: System MUST support an iterative improvement loop, track the number of refinement cycles, and end only when the user says "ok and good".
- **FR-013**: System MUST keep the content focus aligned with the user's professional and interest areas (AI/ML/GenAI, Cloud, Migration & Modernization, Emerging tech trends, Emotional Intelligence) and warn when topics fall outside these areas.
- **FR-014**: System MUST avoid storing secrets in the repository and MUST use environment variables for all sensitive configuration values.
- **FR-015**: System MUST document the selected framework and visual choices for the session.
- **FR-016**: System MUST detect when a topic is outside the allowed focus areas, warn the user with the reason, and allow the user to confirm and proceed or restart with a different topic.

### Key Entities *(include if feature involves data)*

- **Topic Input**: Original topic name, description, or URL with extracted intent, audience, and depth.
- **Outline**: Structured section list with a content angle and rationale.
- **Validation Report**: Sources checked, confidence score, and issues found.
- **Framework Choice**: Selected storytelling structure for the session.
- **Visual Plan**: Chosen visual types and placement guidance.
- **Content Draft**: Full narrative content tied to the approved outline.
- **Platform Version**: Tailored output for each supported platform.
- **Feedback Round**: User feedback and requested improvements.

### Content Focus Areas

The system is designed for content aligned with the following areas:

- **AI / ML / GenAI**: Machine learning, generative AI, LLMs, neural networks, model training, AI ethics, prompt engineering.
- **Cloud**: Cloud infrastructure, cloud platforms (AWS, Azure, GCP), cloud-native architecture, serverless, containers, Kubernetes.
- **Migration & Modernization**: Legacy-to-cloud migration strategies, application modernization, cloud adoption patterns, legacy system updates.
- **Emerging Tech Trends**: Latest developments in technology, emerging frameworks, new standards, tech industry shifts.
- **Emotional Intelligence**: Emotional awareness, interpersonal skills, leadership, team dynamics, workplace psychology, soft skills.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 90% of sessions reach an approved outline within two outline iterations.
- **SC-002**: 95% of sessions include at least two independent sources in the validation report.
- **SC-003**: Users can complete a full end-to-end content cycle in under 20 minutes for a typical topic.
- **SC-004**: 90% of sessions end with the user explicitly responding "ok and good" within three refinement cycles.
- **SC-005**: 100% of generated sessions respect the defined focus areas and do not require storing secrets.

## Clarifications

### Session 2026-02-07

- Q: How should sensitive configuration values (API keys, endpoints) be managed? → A: Environment variables with .env.example template (actual .env in .gitignore)
- Q: What minimum confidence score should the system require for outline validation? → A: 70% confidence score
- Q: How should the system handle topics outside the defined focus areas? → A: Warn user and allow override if they choose to proceed
- Q: Should the system recommend a framework or require explicit user selection? → A: System recommends based on topic type; user can override
- Q: How should platform-specific versions be generated? → A: Generate versions automatically, ask user for adjustments after

## Assumptions

- The user is the only active user in the MVP.
- Publishing remains manual and outside the system scope.
- Users have internet access to allow validation against public sources.
- The system can prompt for alternatives when a requested visual type is not feasible.
- Sensitive configuration values are managed via environment variables with a .env.example template committed to the repository and actual .env files excluded via .gitignore.
