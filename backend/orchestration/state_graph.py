"""
LangGraph State Machine Orchestration (T034-T038)

Orchestrates the complete User Story 1 workflow using LangGraph StateGraph.

Flow: Input → Reasoning → Research → (Validation passes) → Outline Review
                                   ↓ (Validation fails)
                                   ↻ Back to Reasoning (retry)

State persistence:
- After each agent completes, save state to SQLite
- Enable mid-session recovery and auditing
"""

import json
import logging
from typing import TypedDict, Literal, Optional
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END
from backend.agents.input_agent import get_input_agent
from backend.agents.reasoning_agent import get_reasoning_agent  
from backend.agents.research_agent import get_research_agent
from backend.agents.storytelling_agent import get_storytelling_agent
from backend.agents.content_agent import get_content_agent
from backend.models.models import (
    get_db_session, Session, Outline, ValidationReport, ContentDraft
)
from backend.utils.logger import backend_logger

# Logger
logger = logging.getLogger("backend.orchestration.state_graph")


# ============= State Definition =============

class SessionState(TypedDict):
    """
    Complete session state for User Story 1 workflow.
    
    Tracks all data as it flows through agents.
    """
    # Session metadata
    session_id: str
    topic: str
    url: Optional[str]
    
    # Step 1: Input extraction
    topic_data: Optional[dict]
    input_error: Optional[str]
    
    # Step 2: Outline generation  
    outline: Optional[dict]
    reasoning_error: Optional[str]
    outline_version: int
    
    # Step 3: Research validation
    validation_report: Optional[dict]
    research_error: Optional[str]
    validation_attempts: int

    # Step 4: Storytelling + visuals
    framework_choice: Optional[str]
    framework_plan: Optional[dict]
    storytelling_error: Optional[str]

    # Step 5: Content generation
    content_draft: Optional[dict]
    content_error: Optional[str]
    
    # Workflow control
    workflow_status: Literal["input", "reasoning", "research", "approved", "failed"]
    last_update: str
    created_at: str


# ============= Nodes (Agent Calls) =============

def input_node(state: SessionState) -> SessionState:
    """
    Node 1: Extract topic information.
    
    Calls InputAgent to extract theme, audience, intent, focus_area.
    """
    logger.info(f"📝 [INPUT] Processing topic: {state['topic']}")
    
    try:
        input_agent = get_input_agent()
        topic_data = input_agent.extract_topic_info(state['topic'])
        
        state['topic_data'] = topic_data
        state['input_error'] = None
        state['workflow_status'] = 'reasoning'
        
        logger.info(f"✓ [INPUT] Extracted: {topic_data['focus_area']}")
        
        # Warn if out of scope
        if topic_data['is_out_of_scope']:
            logger.warning(f"⚠ [INPUT] Topic is OUT_OF_SCOPE: {topic_data.get('warning')}")
        
        # Persist to database
        _save_state_checkpoint(state, checkpoint='input_complete')
        
        return state
        
    except Exception as e:
        logger.error(f"❌ [INPUT] Error: {e}")
        state['input_error'] = str(e)
        state['workflow_status'] = 'failed'
        return state


def reasoning_node(state: SessionState) -> SessionState:
    """
    Node 2: Generate outline from topic data.
    
    Calls ReasoningAgent to create structured outline with sections.
    """
    logger.info(f"🧠 [REASONING] Generating outline for: {state['topic']}")
    
    try:
        if not state.get('topic_data'):
            raise ValueError("No topic data available - run input node first")
        
        reasoning_agent = get_reasoning_agent()
        outline = reasoning_agent.generate_outline(state['topic_data'])
        
        # Validate outline structure
        if not reasoning_agent.validate_outline(outline):
            raise ValueError("Generated outline failed validation")
        
        state['outline'] = outline
        state['reasoning_error'] = None
        state['outline_version'] += 1
        state['workflow_status'] = 'research'
        
        logger.info(f"✓ [REASONING] Generated {outline['num_sections']} sections")
        
        # Persist to database
        _save_state_checkpoint(state, checkpoint='outline_generated')
        
        return state
        
    except Exception as e:
        logger.error(f"❌ [REASONING] Error: {e}")
        state['reasoning_error'] = str(e)
        state['workflow_status'] = 'failed'
        return state


def research_node(state: SessionState) -> SessionState:
    """
    Node 3: Validate outline through web research.
    
    Calls ResearchAgent to extract claims and verify through Bing search.
    """
    logger.info(f"🔍 [RESEARCH] Validating outline")
    
    try:
        if not state.get('outline'):
            raise ValueError("No outline available - run reasoning node first")
        
        research_agent = get_research_agent()
        validation_report = research_agent.validate_outline(state['outline'])
        
        state['validation_report'] = validation_report
        state['research_error'] = None
        state['validation_attempts'] += 1
        
        # Check if validation passed
        if validation_report.get('passed_validation'):
            state['workflow_status'] = 'approved'
            logger.info(f"✓ [RESEARCH] Validation PASSED: {validation_report['confidence_score']:.1%}")
        else:
            state['workflow_status'] = 'reasoning'  # Retry reasoning
            logger.warning(f"⚠ [RESEARCH] Validation FAILED: {validation_report['confidence_score']:.1%}")
        
        # Persist to database
        _save_state_checkpoint(state, checkpoint='validation_complete')
        
        return state
        
    except Exception as e:
        logger.error(f"❌ [RESEARCH] Error: {e}")
        state['research_error'] = str(e)
        state['workflow_status'] = 'failed'
        return state


def storytelling_node(state: SessionState) -> SessionState:
    """Node 4: Apply framework and generate visual plan."""
    logger.info("🎯 [STORYTELLING] Applying framework")

    try:
        if not state.get("outline"):
            raise ValueError("No outline available - run reasoning node first")

        storytelling_agent = get_storytelling_agent()
        plan = storytelling_agent.generate_framework_plan(
            outline=state["outline"],
            framework_choice=state.get("framework_choice"),
            visual_opt_in=True,
            visual_preferences=None
        )

        state["framework_choice"] = plan.get("framework_choice")
        state["framework_plan"] = plan
        state["storytelling_error"] = None

        _save_state_checkpoint(state, checkpoint="framework_selected")
        return state
    except Exception as e:
        logger.error(f"❌ [STORYTELLING] Error: {e}")
        state["storytelling_error"] = str(e)
        state["workflow_status"] = "failed"
        return state


def content_node(state: SessionState) -> SessionState:
    """Node 5: Generate content draft."""
    logger.info("🧩 [CONTENT] Generating draft")

    try:
        if not state.get("outline") or not state.get("framework_plan"):
            raise ValueError("Missing outline or framework plan")

        content_agent = get_content_agent()
        plan = state["framework_plan"]
        content = content_agent.generate_content(
            outline=state["outline"],
            framework_choice=plan.get("framework_choice"),
            framework_structure=plan.get("framework_structure", []),
            visual_plan=plan.get("visual_plan", []),
            include_code=False
        )

        state["content_draft"] = content
        state["content_error"] = None

        _save_state_checkpoint(state, checkpoint="content_generated")
        return state
    except Exception as e:
        logger.error(f"❌ [CONTENT] Error: {e}")
        state["content_error"] = str(e)
        state["workflow_status"] = "failed"
        return state


def approval_gate_node(state: SessionState) -> SessionState:
    """Node to verify outline approval before US2 starts."""
    if state.get("workflow_status") != "approved":
        logger.warning("⚠ [GATE] Outline not approved - stopping US2 workflow")
        state["workflow_status"] = "failed"
    return state


def should_start_us2(state: SessionState) -> str:
    """Route to storytelling only if outline approved."""
    return "storytelling" if state.get("workflow_status") == "approved" else "end"


# ============= Edges (Routing Logic) =============

def should_retry_reasoning(state: SessionState) -> str:
    """
    Conditional edge: If validation failed and attempts < 3, retry reasoning.
    
    Returns: "reasoning" to retry, or "end" to terminate
    """
    if state['workflow_status'] == 'reasoning' and state['validation_attempts'] < 3:
        logger.info(f"🔄 [EDGE] Retrying reasoning (attempt {state['validation_attempts']}/3)")
        return "reasoning"
    elif state['validation_attempts'] >= 3:
        logger.error(f"❌ [EDGE] Max validation attempts reached (3)")
        state['workflow_status'] = 'failed'
        return "end"
    else:
        return "end"


def should_continue_to_research(state: SessionState) -> str:
    """
    Conditional edge: If input and reasoning succeeded, proceed to research.
    
    Returns: "research" to validate, or "end" to terminate on error
    """
    if state['workflow_status'] == 'failed':
        logger.error(f"❌ [EDGE] Workflow failed at: {state['input_error'] or state['reasoning_error'] or state['research_error']}")
        return "end"
    
    if state['workflow_status'] == 'research':
        return "research"
    
    return "end"


def is_workflow_complete(state: SessionState) -> str:
    """
    Conditional edge: Check if workflow is complete or needs retry.
    
    Returns: "end" if approved or max retries reached
    """
    if state['workflow_status'] == 'approved':
        logger.info(f"✅ [EDGE] Workflow APPROVED")
        return "end"
    
    if state['workflow_status'] == 'failed':
        logger.error(f"❌ [EDGE] Workflow FAILED")
        return "end"
    
    if state['workflow_status'] == 'reasoning' and state['validation_attempts'] >= 3:
        logger.error(f"❌ [EDGE] Max retries exceeded")
        state['workflow_status'] = 'failed'
        return "end"
    
    # Continue to research if ready
    if state['workflow_status'] == 'research':
        return "research"
    
    return "end"


# ============= State Persistence =============

def _save_state_checkpoint(state: SessionState, checkpoint: str):
    """
    Save state checkpoint to SQLite for recovery and auditing.
    
    Args:
        state: Current session state
        checkpoint: Checkpoint name (e.g., 'input_complete', 'outline_generated')
    """
    try:
        db = get_db_session()
        now = datetime.utcnow()
        
        # Update session status
        session = db.query(Session).filter(Session.id == state['session_id']).first()
        if session:
            session.updated_at = now
            db.commit()
        
        # Save outline if generated
        if state.get('outline') and checkpoint in ['outline_generated', 'validation_complete']:
            outline = db.query(Outline).filter(Outline.session_id == state['session_id']).first()
            
            if not outline:
                outline = Outline(
                    id=str(uuid.uuid4()),
                    session_id=state['session_id'],
                    version=state['outline_version'],
                    content_angle=state['outline'].get('content_angle', ''),
                    target_audience=state['outline'].get('target_audience', ''),
                    primary_intent=state['outline'].get('primary_intent', ''),
                    sections=json.dumps(state['outline'].get('sections', [])),
                    user_approved=0,
                    created_at=now
                )
                db.add(outline)
            else:
                outline.version = state['outline_version']
                outline.content_angle = state['outline'].get('content_angle', '')
                outline.sections = json.dumps(state['outline'].get('sections', []))
                outline.updated_at = now
            
            db.commit()
        
        # Save validation report if complete
        if state.get('validation_report') and checkpoint == 'validation_complete':
            outline = db.query(Outline).filter(Outline.session_id == state['session_id']).first()
            
            if outline:
                report = db.query(ValidationReport).filter(ValidationReport.outline_id == outline.id).first()
                
                if not report:
                    report = ValidationReport(
                        id=str(uuid.uuid4()),
                        outline_id=outline.id,
                        confidence_score=state['validation_report'].get('confidence_score', 0.0),
                        credible_sources_found=state['validation_report'].get('credible_sources_found', 0),
                        claims_checked=state['validation_report'].get('claims_checked', 0),
                        validation_details=json.dumps(state['validation_report'].get('validation_details', {})),
                        passed_validation=1 if state['validation_report'].get('passed_validation') else 0,
                        created_at=now
                    )
                    db.add(report)
                else:
                    report.confidence_score = state['validation_report'].get('confidence_score', 0.0)
                    report.credible_sources_found = state['validation_report'].get('credible_sources_found', 0)
                    report.claims_checked = state['validation_report'].get('claims_checked', 0)
                    report.passed_validation = 1 if state['validation_report'].get('passed_validation') else 0
                    report.updated_at = now
                
                db.commit()

        # Save content draft if generated
        if state.get("content_draft") and checkpoint == "content_generated":
            draft = db.query(ContentDraft).filter(ContentDraft.session_id == state["session_id"]).first()
            payload = state["content_draft"]

            if not draft:
                draft = ContentDraft(
                    id=str(uuid.uuid4()),
                    session_id=state["session_id"],
                    body_text=payload.get("body_text", ""),
                    framework_choice=payload.get("framework_choice"),
                    visual_plan=json.dumps(state.get("framework_plan", {}).get("visual_plan", [])),
                    code_snippets=json.dumps(payload.get("code_snippets", [])),
                    created_at=now,
                    updated_at=now
                )
                db.add(draft)
            else:
                draft.body_text = payload.get("body_text", "")
                draft.framework_choice = payload.get("framework_choice")
                draft.visual_plan = json.dumps(state.get("framework_plan", {}).get("visual_plan", []))
                draft.code_snippets = json.dumps(payload.get("code_snippets", []))
                draft.updated_at = now

            db.commit()
        
        logger.debug(f"✓ [PERSIST] Checkpoint '{checkpoint}' saved")
        
    except Exception as e:
        logger.error(f"❌ [PERSIST] Error saving checkpoint: {e}")
    finally:
        db.close()


# ============= Graph Construction =============

def build_state_graph() -> StateGraph:
    """
    Build LangGraph StateGraph for User Story 1 workflow.
    
    Returns:
        Compiled StateGraph ready for execution
    
    Structure:
        START
          ↓
        INPUT (InputAgent)
          ↓
        REASONING (ReasoningAgent)
          ↓
        RESEARCH (ResearchAgent)
          ↓
        [Validation Check]
          ↓ PASS        ↓ FAIL (retry < 3)
        END              REASONING (loop)
              ↑
             [Max retries?]
              ↓
             Failed → END
    """
    
    # Create state graph
    workflow = StateGraph(SessionState)
    
    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("reasoning", reasoning_node)
    workflow.add_node("research", research_node)
    workflow.add_node("storytelling", storytelling_node)
    workflow.add_node("content", content_node)
    
    # Define edges
    workflow.set_entry_point("input")
    
    # input → reasoning
    workflow.add_edge("input", "reasoning")
    
    # reasoning → research (always proceed to validation)
    workflow.add_edge("reasoning", "research")
    
    # research → check result (conditional routing)
    workflow.add_conditional_edges(
        "research",
        is_workflow_complete,
        {
            "research": "research",  # This shouldn't happen (prevents infinite loop)
            "end": END
        }
    )
    
    # Alternative: retry logic (if we want to auto-retry)
    # workflow.add_conditional_edges(
    #     "research",
    #     should_retry_reasoning,
    #     {"reasoning": "reasoning", "end": END}
    # )
    
    logger.info("✓ StateGraph built successfully")
    
    return workflow.compile()


def build_us2_graph() -> StateGraph:
    """
    Build LangGraph StateGraph for User Story 2 workflow.

    Structure:
        STORYTELLING -> CONTENT -> END
    """
    workflow = StateGraph(SessionState)
    workflow.add_node("approval_gate", approval_gate_node)
    workflow.add_node("storytelling", storytelling_node)
    workflow.add_node("content", content_node)

    workflow.set_entry_point("approval_gate")
    workflow.add_conditional_edges(
        "approval_gate",
        should_start_us2,
        {"storytelling": "storytelling", "end": END}
    )
    workflow.add_edge("storytelling", "content")
    workflow.add_edge("content", END)

    logger.info("✓ US2 StateGraph built successfully")
    return workflow.compile()


def run_us2_workflow(session_id: str, framework_choice: Optional[str] = None) -> SessionState:
    """Run US2 workflow using existing approved outline."""
    db = get_db_session()
    try:
        outline = db.query(Outline).filter(Outline.session_id == session_id).first()
        if not outline or not outline.user_approved:
            initial_status = "failed"
            outline_payload = None
        else:
            initial_status = "approved"
            outline_payload = {
                "content_angle": outline.content_angle,
                "target_audience": outline.target_audience,
                "primary_intent": outline.primary_intent,
                "sections": json.loads(outline.sections) if isinstance(outline.sections, str) else outline.sections
            }

        initial_state: SessionState = {
            "session_id": session_id,
            "topic": outline.content_angle if outline else "",
            "url": None,
            "topic_data": None,
            "input_error": None,
            "outline": outline_payload,
            "reasoning_error": None,
            "outline_version": outline.version if outline else 0,
            "validation_report": None,
            "research_error": None,
            "validation_attempts": 0,
            "framework_choice": framework_choice,
            "framework_plan": None,
            "storytelling_error": None,
            "content_draft": None,
            "content_error": None,
            "workflow_status": initial_status,
            "last_update": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        }

        graph = build_us2_graph()
        return graph.invoke(initial_state)
    finally:
        db.close()


# ============= Execution =============

def run_us1_workflow(
    topic: str,
    url: Optional[str] = None,
    session_id: Optional[str] = None
) -> SessionState:
    """
    Execute User Story 1 complete workflow.
    
    Args:
        topic: User topic
        url: Optional URL to extract from
        session_id: Optional session ID (if continuing existing session)
    
    Returns:
        Final SessionState after all agents complete
    
    Example:
        >>> state = run_us1_workflow("AI in healthcare")
        >>> if state['workflow_status'] == 'approved':
        ...     print(f"Outline approved with {len(state['outline']['sections'])} sections")
    """
    
    # Initialize session state
    if not session_id:
        session_id = str(uuid.uuid4())
    
    initial_state: SessionState = {
        "session_id": session_id,
        "topic": topic,
        "url": url,
        "topic_data": None,
        "input_error": None,
        "outline": None,
        "reasoning_error": None,
        "outline_version": 0,
        "validation_report": None,
        "research_error": None,
        "validation_attempts": 0,
        "framework_choice": None,
        "framework_plan": None,
        "storytelling_error": None,
        "content_draft": None,
        "content_error": None,
        "workflow_status": "input",
        "last_update": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }
    
    logger.info(f"🚀 Starting US1 workflow for: {topic}")
    
    # Build and compile graph
    graph = build_state_graph()
    
    # Run workflow
    final_state = graph.invoke(initial_state)
    
    logger.info(f"✅ Workflow complete - Status: {final_state['workflow_status']}")
    
    return final_state


# Module initialization
logger.info("✓ LangGraph orchestration module loaded")
