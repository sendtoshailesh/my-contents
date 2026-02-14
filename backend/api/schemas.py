"""
API Schemas - Pydantic Models
Request/response schemas for all API endpoints
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


# ============= Common Models =============

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None


# ============= Session Models =============

class SessionCreate(BaseModel):
    """Create new session request"""
    topic: str = Field(..., min_length=1, max_length=500, description="Topic or subject")
    url: Optional[str] = Field(None, description="Optional URL to extract from")


class SessionResponse(BaseModel):
    """Session response"""
    id: str
    topic: str
    url: Optional[str]
    status: str
    iteration_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SessionList(BaseResponse):
    """List of sessions"""
    sessions: List[SessionResponse]
    total: int


# ============= Outline Models =============

class OutlineSection(BaseModel):
    """Single section of an outline"""
    title: str = Field(..., description="Section title")
    description: Optional[str] = Field(None, description="Section details")
    order: int = Field(..., description="Section order")


class OutlineResponse(BaseModel):
    """Outline response"""
    id: str
    session_id: str
    version: int
    content_angle: str
    target_audience: Optional[str]
    primary_intent: Optional[str]
    sections: List[OutlineSection]
    user_approved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "outline-123",
                "session_id": "session-456",
                "version": 1,
                "content_angle": "AI's role in democratizing education",
                "target_audience": "Educators and administrators",
                "primary_intent": "Inform and inspire",
                "sections": [
                    {
                        "title": "The Current State of Education",
                        "description": "Overview of traditional education models",
                        "order": 1
                    }
                ],
                "user_approved": False,
                "created_at": "2026-02-08T00:00:00"
            }
        }


class OutlineApprove(BaseModel):
    """Approve an outline"""
    approved: bool = True


# ============= Validation Report Models =============

class ValidationDetail(BaseModel):
    """Details of a validated claim"""
    claim: str
    sources: List[Dict[str, Any]]
    credible_count: int
    confidence: float


class ValidationReportResponse(BaseModel):
    """Validation report for an outline"""
    id: str
    outline_id: str
    confidence_score: float
    credible_sources_found: int
    claims_checked: int
    passed_validation: bool
    validation_details: Optional[List[ValidationDetail]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Framework Models =============

class FrameworkInfo(BaseModel):
    """Framework information"""
    id: str
    name: str
    description: Optional[str]
    steps: List[str]
    best_for: Optional[str]


class FrameworkList(BaseResponse):
    """List of available frameworks"""
    frameworks: List[FrameworkInfo]


class FrameworkSelect(BaseModel):
    """Select framework for content generation"""
    framework_id: Optional[str] = Field(None, description="ID of selected framework")
    visual_opt_in: bool = Field(True, description="Include visuals in content")
    visual_preferences: Optional[List[str]] = Field(None, description="Preferred visual types")


# ============= Visual Models =============

class VisualReference(BaseModel):
    """Reference to a visual in content"""
    visual_id: int
    type: str  # flowchart, sequence, architecture, photo, etc.
    location: Optional[str]  # section_1, section_2, appendix, etc.
    description: str
    rationale: Optional[str]
    recommended_tool: Optional[str] = None
    draft_code: Optional[str] = None


class VisualPlan(BaseModel):
    """Visual planning for content"""
    visuals: List[VisualReference]
    total_visuals: int
    mermaid_diagrams: int


class FrameworkStepMapping(BaseModel):
    """Mapping between framework steps and outline sections"""
    framework_step: str
    outline_section: str
    order: int


class FrameworkSelectionResponse(BaseModel):
    """Framework selection response with visual plan"""
    session_id: str
    framework_choice: str
    recommended_framework: Optional[str]
    framework_explanation: Optional[str]
    framework_structure: List[FrameworkStepMapping]
    visual_plan: List[VisualReference]
    total_visuals: int
    opt_out_visuals: bool


# ============= Content Draft Models =============

class CodeSnippet(BaseModel):
    """Code snippet in content"""
    language: str
    code: str
    explanation: Optional[str]
    expected_output: Optional[str]


class ContentDraftResponse(BaseModel):
    """Generated content draft"""
    id: str
    session_id: str
    body_text: str
    framework_choice: Optional[str]
    visual_plan: Optional[VisualPlan]
    code_snippets: Optional[List[CodeSnippet]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= Platform Version Models =============

class PlatformVersionResponse(BaseModel):
    """Platform-specific content version"""
    id: str
    session_id: str
    platform_name: str
    version: int
    content: str
    character_count: int
    created_at: datetime
    updated_at: datetime


class ContentGenerate(BaseModel):
    """Request to generate content"""
    framework_choice: Optional[str] = Field(None, description="Framework ID")
    visual_plan: Optional[List[VisualReference]] = None
    include_code: bool = Field(False, description="Include code snippets")
    
    class Config:
        from_attributes = True


class PlatformVersionList(BaseResponse):
    """List of all platform versions"""
    platforms: List[PlatformVersionResponse]


# ============= Iteration & Feedback Models =============

class FeedbackArea(BaseModel):
    """Feedback area for iteration"""
    name: str  # tone, depth, visuals, technicality, humor, examples, structure
    selected: bool


class IterationRequest(BaseModel):
    """Request for content iteration"""
    feedback_areas: List[FeedbackArea]
    feedback_text: Optional[str] = Field(None, description="Freeform feedback")
    apply_to: str = Field("all", description="all or specific platform name")


class IterationFeedbackResponse(BaseModel):
    """Iteration feedback record"""
    id: str
    session_id: str
    iteration_number: int
    feedback_areas: List[str]
    feedback_text: Optional[str]
    regenerated_content: Optional[Dict[str, Any]]
    affected_components: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Session Completion Models =============

class SessionComplete(BaseModel):
    """Mark session as complete"""
    status: str = "completed"
    final_feedback: Optional[str] = None


class SessionSummary(BaseResponse):
    """Summary of completed session"""
    session_id: str
    topic: str
    total_iterations: int
    outline_version: int
    final_platforms: List[str]
    completion_time_minutes: float
    created_at: datetime
    completed_at: datetime


# ============= Error Models =============

class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============= Settings Models =============

class UserSettings(BaseModel):
    """User configuration settings"""
    default_model: str = "azure-gpt4-turbo"
    enabled_platforms: List[str] = [
        "linkedin",
        "twitter",
        "reddit",
        "medium",
        "substack",
        "instagram"
    ]
    default_visual_preference: bool = True
    max_sessions: int = 10
    auto_cleanup: bool = True


# ============= Health Check =============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    database: str
    secrets: str
    services: Dict[str, str]
