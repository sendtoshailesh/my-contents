"""
API Routes - FastAPI endpoints
All endpoints for session management, content generation, and feedback
"""

from fastapi import APIRouter, HTTPException, Query, Path, BackgroundTasks
from typing import List, Optional
import uuid
from datetime import datetime
import logging
import json

from backend.api.schemas import (
    SessionCreate, SessionResponse, SessionList, OutlineResponse, OutlineApprove,
    ValidationReportResponse, FrameworkList, FrameworkInfo, FrameworkSelect,
    FrameworkSelectionResponse, ContentGenerate, ContentDraftResponse,
    PlatformVersionResponse, PlatformVersionList, IterationRequest,
    IterationFeedbackResponse, SessionComplete, SessionSummary, BaseResponse,
    ErrorResponse, UserSettings, HealthResponse, VisualPlan, VisualReference,
    FrameworkStepMapping
)
from backend.models.models import (
    get_db_session, Session, Outline, ValidationReport, ContentDraft,
    PlatformVersion, IterationFeedback
)
from services.framework_engine import get_framework_engine
from services.search_service import BingSearchService
from backend.utils.reference_data import get_reference_data
from backend.orchestration.state_graph import run_us1_workflow
from backend.agents.storytelling_agent import get_storytelling_agent
from backend.agents.content_agent import get_content_agent

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["content-studio"])


# ============= Session Endpoints =============

@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreate, background_tasks: BackgroundTasks):
    """
    Create new content generation session and trigger US1 workflow.
    
    Workflow runs asynchronously:
    1. Input extraction (topic classification)
    2. Outline generation (structure + content angle)
    3. Research validation (web search + credibility scoring)
    
    Returns immediately with session created.
    """
    try:
        db = get_db_session()
        session_id = str(uuid.uuid4())
        
        new_session = Session(
            id=session_id,
            topic=request.topic,
            url=request.url,
            status='input',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_session)
        db.commit()
        
        logger.info(f"✅ Created session {session_id} for topic: {request.topic}")
        
        # Add background task to run US1 workflow
        background_tasks.add_task(
            _run_us1_workflow_task,
            session_id=session_id,
            topic=request.topic,
            url=request.url
        )
        
        logger.info(f"🚀 Queued US1 workflow for session {session_id}")
        
        return SessionResponse(
            id=new_session.id,
            topic=new_session.topic,
            url=new_session.url,
            status=new_session.status,
            iteration_count=new_session.iteration_count,
            created_at=new_session.created_at,
            updated_at=new_session.updated_at
        )
    except Exception as e:
        logger.error(f"❌ Error creating session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/sessions", response_model=SessionList)
async def list_sessions(limit: int = Query(10, le=100)):
    """List all sessions (max 10)"""
    try:
        db = get_db_session()
        sessions = db.query(Session).order_by(Session.created_at.desc()).limit(min(limit, 10)).all()
        
        return SessionList(
            success=True,
            sessions=[
                SessionResponse(
                    id=s.id,
                    topic=s.topic,
                    url=s.url,
                    status=s.status,
                    iteration_count=s.iteration_count,
                    created_at=s.created_at,
                    updated_at=s.updated_at
                )
                for s in sessions
            ],
            total=len(sessions)
        )
    except Exception as e:
        logger.error(f"❌ Error listing sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str = Path(..., description="Session ID")):
    """Get session details"""
    try:
        db = get_db_session()
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            id=session.id,
            topic=session.topic,
            url=session.url,
            status=session.status,
            iteration_count=session.iteration_count,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# ============= Outline Endpoints =============

@router.get("/sessions/{session_id}/outline", response_model=OutlineResponse)
async def get_outline(session_id: str = Path(..., description="Session ID")):
    """Get outline for session"""
    try:
        db = get_db_session()
        outline = db.query(Outline).filter(Outline.session_id == session_id).first()
        
        if not outline:
            raise HTTPException(status_code=404, detail="Outline not found")
        
        # Parse sections JSON
        import json
        sections = json.loads(outline.sections) if isinstance(outline.sections, str) else outline.sections
        
        return OutlineResponse(
            id=outline.id,
            session_id=outline.session_id,
            version=outline.version,
            content_angle=outline.content_angle,
            target_audience=outline.target_audience,
            primary_intent=outline.primary_intent,
            sections=sections,
            user_approved=bool(outline.user_approved),
            created_at=outline.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting outline: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/sessions/{session_id}/approve", response_model=BaseResponse)
async def approve_outline(
    session_id: str = Path(..., description="Session ID"),
    request: OutlineApprove = None
):
    """Approve an outline"""
    try:
        db = get_db_session()
        session = db.query(Session).filter(Session.id == session_id).first()
        outline = db.query(Outline).filter(Outline.session_id == session_id).first()
        
        if not outline:
            raise HTTPException(status_code=404, detail="Outline not found")
        
        outline.user_approved = 1 if request.approved else 0
        session.status = 'framework_selection' if request.approved else 'input'
        session.updated_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"✅ Outline {'approved' if request.approved else 'rejected'} for session {session_id}")
        
        return BaseResponse(
            success=True,
            message=f"Outline {'approved' if request.approved else 'rejected'}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error approving outline: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# ============= Validation Report Endpoints =============

@router.get("/sessions/{session_id}/validation", response_model=ValidationReportResponse)
async def get_validation_report(session_id: str = Path(..., description="Session ID")):
    """Get validation report for session"""
    try:
        db = get_db_session()
        outline = db.query(Outline).filter(Outline.session_id == session_id).first()
        
        if not outline:
            raise HTTPException(status_code=404, detail="Outline not found")
        
        report = db.query(ValidationReport).filter(ValidationReport.outline_id == outline.id).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Validation report not found")
        
        return ValidationReportResponse(
            id=report.id,
            outline_id=report.outline_id,
            confidence_score=report.confidence_score,
            credible_sources_found=report.credible_sources_found,
            claims_checked=report.claims_checked,
            passed_validation=bool(report.passed_validation),
            validation_details=None,
            created_at=report.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting validation report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# ============= Framework Endpoints =============

@router.get("/frameworks", response_model=FrameworkList)
async def get_frameworks():
    """Get all available storytelling frameworks"""
    try:
        engine = get_framework_engine()
        frameworks = engine.get_frameworks()
        
        return FrameworkList(
            success=True,
            frameworks=[
                FrameworkInfo(
                    id=f['id'],
                    name=f['name'],
                    description=f['description'],
                    steps=f['steps'],
                    best_for=f['best_for']
                )
                for f in frameworks
            ]
        )
    except Exception as e:
        logger.error(f"❌ Error getting frameworks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/framework", response_model=FrameworkSelectionResponse)
async def select_framework(
    session_id: str = Path(..., description="Session ID"),
    request: FrameworkSelect = None
):
    """Select a framework and generate a visual plan"""
    try:
        if request is None:
            request = FrameworkSelect()

        db = get_db_session()
        session = db.query(Session).filter(Session.id == session_id).first()
        outline = db.query(Outline).filter(Outline.session_id == session_id).first()

        if not session or not outline:
            raise HTTPException(status_code=404, detail="Session or outline not found")
        if not outline.user_approved:
            raise HTTPException(status_code=400, detail="Outline must be approved first")

        sections = json.loads(outline.sections) if isinstance(outline.sections, str) else outline.sections
        outline_payload = {
            "content_angle": outline.content_angle,
            "target_audience": outline.target_audience,
            "primary_intent": outline.primary_intent,
            "sections": sections
        }

        storytelling_agent = get_storytelling_agent()
        recommended = storytelling_agent.recommend_framework(outline_payload)
        framework_choice = request.framework_id or recommended

        plan = storytelling_agent.generate_framework_plan(
            outline=outline_payload,
            framework_choice=framework_choice,
            visual_opt_in=request.visual_opt_in,
            visual_preferences=request.visual_preferences
        )

        session.status = "generating_content"
        session.updated_at = datetime.utcnow()
        db.commit()

        framework_structure = [
            FrameworkStepMapping(
                framework_step=str(item.get("framework_step")),
                outline_section=str(item.get("outline_section")),
                order=item.get("order", idx + 1)
            )
            for idx, item in enumerate(plan.get("framework_structure", []))
        ]

        visual_plan = [
            VisualReference(
                visual_id=item.get("visual_id"),
                type=item.get("type", "visual"),
                location=item.get("location"),
                description=item.get("description", ""),
                rationale=item.get("rationale"),
                recommended_tool=item.get("recommended_tool"),
                draft_code=item.get("draft_code")
            )
            for item in plan.get("visual_plan", [])
        ]

        return FrameworkSelectionResponse(
            session_id=session_id,
            framework_choice=framework_choice,
            recommended_framework=recommended,
            framework_explanation=plan.get("framework_explanation"),
            framework_structure=framework_structure,
            visual_plan=visual_plan,
            total_visuals=plan.get("total_visuals", len(visual_plan)),
            opt_out_visuals=plan.get("opt_out_visuals", False)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error selecting framework: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/sessions/{session_id}/content", response_model=ContentDraftResponse)
async def generate_content(
    session_id: str,
    request: ContentGenerate
):
    """Generate content draft (User Story 2)"""
    try:
        db = get_db_session()
        session = db.query(Session).filter(Session.id == session_id).first()
        outline = db.query(Outline).filter(Outline.session_id == session_id).first()

        if not session or not outline:
            raise HTTPException(status_code=404, detail="Session or outline not found")
        if not outline.user_approved:
            raise HTTPException(status_code=400, detail="Outline must be approved first")

        sections = json.loads(outline.sections) if isinstance(outline.sections, str) else outline.sections
        outline_payload = {
            "content_angle": outline.content_angle,
            "target_audience": outline.target_audience,
            "primary_intent": outline.primary_intent,
            "sections": sections
        }

        storytelling_agent = get_storytelling_agent()
        framework_choice = request.framework_choice or storytelling_agent.recommend_framework(outline_payload)

        if request.visual_plan:
            visual_plan = [item.model_dump() for item in request.visual_plan]
        else:
            plan = storytelling_agent.generate_framework_plan(
                outline=outline_payload,
                framework_choice=framework_choice,
                visual_opt_in=True,
                visual_preferences=None
            )
            visual_plan = plan.get("visual_plan", [])

        framework_structure = storytelling_agent.framework_engine.map_outline_to_framework(
            outline_sections=[s.get("title", "Section") for s in sections],
            framework_id=framework_choice
        )

        content_agent = get_content_agent()
        content = content_agent.generate_content(
            outline=outline_payload,
            framework_choice=framework_choice,
            framework_structure=framework_structure,
            visual_plan=visual_plan,
            include_code=request.include_code
        )

        draft = db.query(ContentDraft).filter(ContentDraft.session_id == session_id).first()
        now = datetime.utcnow()
        if not draft:
            draft = ContentDraft(
                id=str(uuid.uuid4()),
                session_id=session_id,
                body_text=content["body_text"],
                framework_choice=framework_choice,
                visual_plan=json.dumps(visual_plan),
                code_snippets=json.dumps(content.get("code_snippets", [])),
                created_at=now,
                updated_at=now
            )
            db.add(draft)
        else:
            draft.body_text = content["body_text"]
            draft.framework_choice = framework_choice
            draft.visual_plan = json.dumps(visual_plan)
            draft.code_snippets = json.dumps(content.get("code_snippets", []))
            draft.updated_at = now

        session.status = "platform_review"
        session.updated_at = now
        db.commit()

        visual_plan_response = _build_visual_plan_response(visual_plan)
        code_snippets = content.get("code_snippets", [])

        return ContentDraftResponse(
            id=draft.id,
            session_id=draft.session_id,
            body_text=draft.body_text,
            framework_choice=draft.framework_choice,
            visual_plan=visual_plan_response,
            code_snippets=code_snippets,
            created_at=draft.created_at,
            updated_at=draft.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating content draft: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/sessions/{session_id}/content", response_model=ContentDraftResponse)
async def get_content(session_id: str):
    """Retrieve content draft for session"""
    try:
        db = get_db_session()
        draft = db.query(ContentDraft).filter(ContentDraft.session_id == session_id).first()
        if not draft:
            raise HTTPException(status_code=404, detail="Content draft not found")

        visual_plan = json.loads(draft.visual_plan) if draft.visual_plan else []
        code_snippets = json.loads(draft.code_snippets) if draft.code_snippets else []

        return ContentDraftResponse(
            id=draft.id,
            session_id=draft.session_id,
            body_text=draft.body_text,
            framework_choice=draft.framework_choice,
            visual_plan=_build_visual_plan_response(visual_plan),
            code_snippets=code_snippets,
            created_at=draft.created_at,
            updated_at=draft.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting content draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# ============= Health Check =============

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """API health check"""
    try:
        db = get_db_session()
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    finally:
        db.close()
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow(),
        database=db_status,
        secrets="configured",
        services={
            "framework_engine": "ready",
            "search_service": "ready",
            "llm_service": "ready"
        }
    )


# ============= Background Tasks =============

def _run_us1_workflow_task(session_id: str, topic: str, url: Optional[str] = None):
    """
    Background task to run US1 workflow (input → reasoning → research).
    
    Executed asynchronously after session creation.
    Updates session status and persists results to database.
    """
    try:
        logger.info(f"🚀 [BACKGROUND] Starting US1 workflow for session {session_id}")
        
        # Run workflow
        final_state = run_us1_workflow(topic=topic, url=url, session_id=session_id)
        
        # Update session status based on workflow result
        db = get_db_session()
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if session:
            if final_state['workflow_status'] == 'approved':
                session.status = 'outline_review'
                logger.info(f"✅ [BACKGROUND] Workflow approved for session {session_id}")
            else:
                session.status = 'input'  # Blocked, user needs to restart/retry
                logger.warning(f"⚠ [BACKGROUND] Workflow failed for session {session_id}: {final_state['workflow_status']}")
            
            session.updated_at = datetime.utcnow()
            db.commit()
        
        logger.info(f"✅ [BACKGROUND] US1 workflow complete for session {session_id}")
        
    except Exception as e:
        logger.error(f"❌ [BACKGROUND] US1 workflow error for session {session_id}: {e}", exc_info=True)
        # Update session to error state
        try:
            db = get_db_session()
            session = db.query(Session).filter(Session.id == session_id).first()
            if session:
                session.status = 'input'
                session.updated_at = datetime.utcnow()
                db.commit()
        except:
            pass


def _build_visual_plan_response(visual_plan: List[dict]) -> VisualPlan:
    visuals = [
        VisualReference(
            visual_id=item.get("visual_id"),
            type=item.get("type", "visual"),
            location=item.get("location"),
            description=item.get("description", ""),
            rationale=item.get("rationale"),
            recommended_tool=item.get("recommended_tool"),
            draft_code=item.get("draft_code")
        )
        for item in visual_plan
    ]
    mermaid_count = sum(1 for item in visual_plan if item.get("recommended_tool") == "mermaid")
    return VisualPlan(
        visuals=visuals,
        total_visuals=len(visuals),
        mermaid_diagrams=mermaid_count
    )


# ============= Stub Endpoints (To Be Implemented in Phase 3) =============

@router.post("/sessions/{session_id}/outline")
async def generate_outline(session_id: str):
    """Generate outline from topic (Phase 3: User Story 1)"""
    raise HTTPException(status_code=501, detail="Not yet implemented - Phase 3")

@router.post("/sessions/{session_id}/platforms")
async def generate_platforms(session_id: str):
    """Generate platform-specific versions (Phase 5: User Story 3)"""
    raise HTTPException(status_code=501, detail="Not yet implemented - Phase 5")

@router.post("/sessions/{session_id}/iterate")
async def iterate_content(session_id: str):
    """Iterate content based on feedback (Phase 5: User Story 3)"""
    raise HTTPException(status_code=501, detail="Not yet implemented - Phase 5")
