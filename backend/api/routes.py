"""
API Routes - FastAPI endpoints
All endpoints for session management, content generation, and feedback
"""

from fastapi import APIRouter, HTTPException, Query, Path, BackgroundTasks
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
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
from backend.agents.platform_agent import get_platform_agent
from backend.agents.iteration_handler import get_iteration_handler

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


# ============= Platform & Iteration Endpoints (Phase 5: User Story 3) =============

@router.post("/sessions/{session_id}/platforms", response_model=PlatformVersionList)
async def generate_platforms(session_id: str, background_tasks: BackgroundTasks):
    """
    Generate platform-specific versions for all 6 platforms.
    
    Prerequisites:
    - Session must have approved outline
    - Content draft must exist
    
    Generates versions for:
    - LinkedIn (professional, 500-3000 chars)
    - Twitter/X (thread, 280-28000 chars)
    - Reddit (authentic, 300-40000 chars)
    - Medium (narrative, 1000-10000 chars)
    - Substack (newsletter, 800-8000 chars)
    - Instagram (visual-first, 100-2200 chars)
    
    Returns platform versions immediately.
    """
    logger.info(f"[API] Generating platforms for session {session_id}")
    
    # Verify session exists and has content draft
    db = get_db_session()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
        
        # Check for content draft
        draft = db.query(ContentDraft).filter(
            ContentDraft.session_id == session_id
        ).first()
        
        if not draft:
            raise HTTPException(
                status_code=400, 
                detail="Cannot generate platforms without content draft. Generate content first."
            )
        
        # Update session status
        session.status = "generating_platforms"
        session.updated_at = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()
    
    # Generate platform versions (synchronous for now, can be async)
    try:
        platform_agent = get_platform_agent()
        versions = platform_agent.generate_all_platforms(session_id=session_id)
        
        # Retrieve saved versions from database
        db = get_db_session()
        try:
            platform_versions = db.query(PlatformVersion).filter(
                PlatformVersion.session_id == session_id
            ).all()
            
            # Update session status
            session = db.query(Session).filter(Session.id == session_id).first()
            session.status = "platform_review"
            session.updated_at = datetime.utcnow()
            db.commit()
            
            # Format response
            versions_list = []
            for pv in platform_versions:
                versions_list.append(PlatformVersionResponse(
                    platform_name=pv.platform_name,
                    version=pv.version,
                    content=pv.content,
                    character_count=len(pv.content),
                    created_at=pv.created_at.isoformat()
                ))
            
            return PlatformVersionList(
                session_id=session_id,
                versions=versions_list,
                total_platforms=len(versions_list),
                status="platform_review"
            )
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"[API] Failed to generate platforms: {e}")
        
        # Update session status to error
        db = get_db_session()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            if session:
                session.status = "error"
                session.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
        
        raise HTTPException(status_code=500, detail=f"Failed to generate platforms: {str(e)}")


@router.post("/sessions/{session_id}/iterate", response_model=IterationFeedbackResponse)
async def iterate_content(session_id: str, request: IterationRequest):
    """
    Process user feedback and regenerate content.
    
    Feedback Areas:
    - tone: Adjust formality, emotion, voice
    - depth: More/less detail, technical depth
    - visuals: Add/remove/modify visual elements
    - technicality: Increase/decrease technical complexity
    - humor: Adjust humor level
    - examples: Add/remove/change examples
    - structure: Reorganize sections, flow
    
    Affected Components:
    - content_draft: Main content body
    - platform_versions: Platform-specific adaptations
    - visuals: Visual plan and diagrams
    
    Can iterate multiple times until user says "ok and good".
    """
    logger.info(f"[API] Processing iteration for session {session_id}")
    
    # Verify session exists
    db = get_db_session()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
        
        if session.status == "completed":
            raise HTTPException(
                status_code=400,
                detail="Session already completed. Cannot iterate further."
            )
    finally:
        db.close()
    
    # Process feedback
    try:
        iteration_handler = get_iteration_handler()
        result = iteration_handler.process_feedback(
            session_id=session_id,
            feedback_areas=request.feedback_areas,
            feedback_text=request.feedback_text,
            affected_components=request.affected_components,
            specific_platforms=request.specific_platforms
        )
        
        return IterationFeedbackResponse(
            session_id=session_id,
            iteration_number=result["iteration_number"],
            affected_components=result["affected_components"],
            regenerated_content=result["regenerated_content"],
            updated_platform_versions=result["updated_platform_versions"],
            status=result["status"],
            message=f"Iteration #{result['iteration_number']} completed. Review updated content."
        )
        
    except ValueError as e:
        logger.error(f"[API] Invalid feedback: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Failed to process iteration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")


@router.post("/sessions/{session_id}/complete", response_model=SessionSummary)
async def complete_session(session_id: str, request: SessionComplete):
    """
    Mark session as complete with "ok and good" phrase.
    
    Validates completion phrase and finalizes session.
    """
    logger.info(f"[API] Completing session {session_id}")
    
    try:
        iteration_handler = get_iteration_handler()
        result = iteration_handler.complete_session(
            session_id=session_id,
            completion_phrase=request.completion_phrase
        )
        
        return SessionSummary(
            session_id=result["session_id"],
            status=result["status"],
            completed_at=result["completed_at"],
            iteration_count=result["iteration_count"],
            summary=result["summary"]
        )
        
    except ValueError as e:
        logger.error(f"[API] Invalid completion phrase: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[API] Failed to complete session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")


# ============= Session Management (Phase 6) =============

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str = Path(..., description="Session ID")):
    """Delete a session and all related data"""
    try:
        db = get_db_session()
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Delete session (cascades to related data)
        db.delete(session)
        db.commit()
        logger.info(f"✅ Deleted session {session_id}")
        
        return BaseResponse(
            success=True,
            message=f"Session {session_id} deleted"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/sessions/{session_id}/export")
async def export_session(session_id: str = Path(..., description="Session ID")):
    """Export session data as JSON"""
    try:
        db = get_db_session()
        session = db.query(Session).filter(Session.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Collect session data
        export_data = {
            "session": {
                "id": session.id,
                "topic": session.topic,
                "url": session.url,
                "status": session.status,
                "iteration_count": session.iteration_count,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            },
            "outline": None,
            "content": None,
            "platforms": [],
            "iterations": []
        }
        
        # Get outline if exists
        outline = db.query(Outline).filter(Outline.session_id == session_id).first()
        if outline:
            sections = json.loads(outline.sections) if isinstance(outline.sections, str) else outline.sections
            export_data["outline"] = {
                "content_angle": outline.content_angle,
                "target_audience": outline.target_audience,
                "primary_intent": outline.primary_intent,
                "sections": sections,
                "user_approved": bool(outline.user_approved),
                "created_at": outline.created_at.isoformat()
            }
        
        # Get content draft if exists
        draft = db.query(ContentDraft).filter(ContentDraft.session_id == session_id).first()
        if draft:
            export_data["content"] = {
                "body_text": draft.body_text,
                "framework_choice": draft.framework_choice,
                "created_at": draft.created_at.isoformat(),
                "updated_at": draft.updated_at.isoformat()
            }
        
        # Get platform versions
        platforms = db.query(PlatformVersion).filter(PlatformVersion.session_id == session_id).all()
        export_data["platforms"] = [
            {
                "platform_name": p.platform_name,
                "version": p.version,
                "content": p.content,
                "created_at": p.created_at.isoformat()
            }
            for p in platforms
        ]
        
        # Get iteration feedback
        iterations = db.query(IterationFeedback).filter(IterationFeedback.session_id == session_id).all()
        export_data["iterations"] = [
            {
                "iteration_number": it.iteration_number,
                "feedback_areas": json.loads(it.feedback_areas) if isinstance(it.feedback_areas, str) else it.feedback_areas,
                "feedback_text": it.feedback_text,
                "created_at": it.created_at.isoformat()
            }
            for it in iterations
        ]
        
        logger.info(f"✅ Exported session {session_id}")
        
        return {"success": True, "json_content": json.dumps(export_data, indent=2)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error exporting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/sessions/cleanup/abandoned")
async def cleanup_abandoned_sessions():
    """Delete all abandoned sessions"""
    try:
        db = get_db_session()
        abandoned = db.query(Session).filter(Session.status == 'abandoned').all()
        count = len(abandoned)
        
        for session in abandoned:
            db.delete(session)
        
        db.commit()
        logger.info(f"✅ Cleaned up {count} abandoned sessions")
        
        return {"success": True, "deleted_count": count}
    except Exception as e:
        logger.error(f"❌ Error cleaning up abandoned sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/sessions/cleanup/old")
async def cleanup_old_sessions(request_body: Optional[dict] = None):
    """Delete sessions older than specified days"""
    try:
        days = 30
        if request_body and isinstance(request_body, dict):
            days = request_body.get('days', 30)
        
        db = get_db_session()
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_sessions = db.query(Session).filter(Session.created_at < cutoff_date).all()
        count = len(old_sessions)
        
        for session in old_sessions:
            db.delete(session)
        
        db.commit()
        logger.info(f"✅ Cleaned up {count} sessions older than {days} days")
        
        return {"success": True, "deleted_count": count}
    except Exception as e:
        logger.error(f"❌ Error cleaning up old sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/sessions/backup")
async def backup_all_sessions():
    """Backup all sessions as JSON"""
    try:
        db = get_db_session()
        sessions = db.query(Session).all()
        
        backup_data = {
            "backup_date": datetime.utcnow().isoformat(),
            "total_sessions": len(sessions),
            "sessions": []
        }
        
        for session in sessions:
            session_export = {
                "session": {
                    "id": session.id,
                    "topic": session.topic,
                    "status": session.status,
                    "created_at": session.created_at.isoformat()
                }
            }
            backup_data["sessions"].append(session_export)
        
        logger.info(f"✅ Backed up {len(sessions)} sessions")
        
        return {"success": True, "backup_json": json.dumps(backup_data, indent=2)}
    except Exception as e:
        logger.error(f"❌ Error backing up sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
