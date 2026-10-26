from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class ErrorCategory(str, Enum):
    CALCULATION_ARITHMETIC = "CALCULATION_ARITHMETIC"
    FORMULA_CONFUSION = "FORMULA_CONFUSION"
    PREREQUISITE_CONCEPT_GAP = "PREREQUISITE_CONCEPT_GAP"
    MISCONCEPTION_REPRESENTATION = "MISCONCEPTION_REPRESENTATION"
    IMPULSIVE_GUESS = "IMPULSIVE_GUESS"

class QuestionOption(BaseModel):
    id: str
    key: str # 'A', 'B', 'C', 'D'
    text: str
    is_correct: bool = False
    error_category: Optional[ErrorCategory] = None
    error_code: Optional[str] = None
    rationale: Optional[str] = None

class Question(BaseModel):
    id: str
    concept_id: str
    concept_name: str
    title: str
    prompt: str
    options: List[QuestionOption]
    difficulty: str = "medium"
    benchmark_seconds: int = 120
    solution_steps: List[str] = []

class Concept(BaseModel):
    id: str
    code: str
    name: str
    grade_level: int = 6
    subject: str = "Mathematics"
    domain: str = "Number Systems"
    description: str
    prerequisites: List[str] = []
    downstream_impact: List[str] = []
    mastery_threshold: float = 0.75

# Step 1: Learning Evidence
class QuestionTelemetry(BaseModel):
    question_id: str
    concept_id: str
    selected_option_id: str
    is_correct: bool
    time_spent_seconds: int
    answer_changes: int = 0
    option_switch_sequence: List[Dict[str, Any]] = []
    rough_work_image_base64: Optional[str] = None # For Mathpix OCR

class AssessmentSubmission(BaseModel):
    student_id: str
    student_name: str = "Alex Johnson"
    grade_level: int = 6
    subject: str = "Mathematics - Fractions"
    assessment_id: str = "diag_class6_math_01"
    evidence_list: List[QuestionTelemetry]
    moderator_override: Optional[bool] = None

# Step 2 & 3: Concept Intelligence & Cognitive Diagnosis
class ConceptMasteryScore(BaseModel):
    concept_id: str
    concept_name: str
    score: float # 0.0 to 1.0
    status: str # 'mastered' | 'developing' | 'weak'
    confidence: float # 0.0 to 1.0
    accuracy: float
    avg_time_seconds: int
    answer_changes: int
    detected_error_category: Optional[ErrorCategory] = None
    prerequisite_gap: bool = False
    reason: str

# Step 4: Learning Trajectory / Risk Prediction
class RiskPrediction(BaseModel):
    overall_risk_level: str # 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
    risk_score: float # 0.0 to 1.0
    blocked_future_topics: List[str]
    longitudinal_trajectory_note: str

# Step 5 & 6: Learning Prescription & Recovery Path
class PrescriptionItem(BaseModel):
    step_number: int
    concept_id: str
    concept_name: str
    priority: str # 'HIGH' | 'MEDIUM' | 'LOW'
    is_prerequisite_gap: bool
    pedagogical_focus: str
    recommended_duration_mins: int

# Step 7: Learning Delivery Material
class WorkedExample(BaseModel):
    problem: str
    step_by_step: List[str]
    solution: str

class LearningDeliveryModule(BaseModel):
    concept_id: str
    concept_name: str
    micro_explanation: str
    worked_examples: List[WorkedExample]
    practice_questions: List[Question]

# Step 8: Learning Impact
class ImpactEvaluation(BaseModel):
    concept_id: str
    concept_name: str
    mastery_before: float
    mastery_after: float
    delta: float
    status_progression: str # e.g. "weak -> developing" or "developing -> mastered"

# Step 9: Updated Intelligence & Three-Tier Reports
class ThreeTierReports(BaseModel):
    student_report: str
    parent_report: str
    teacher_report: str
    admin_summary: str

# Master Pipeline Output Response
class PipelineResponse(BaseModel):
    student_id: str
    student_name: str
    assessment_id: str
    
    # 1. Learning Evidence Summary
    evidence_summary: Dict[str, Any]
    
    # 2. Concept Intelligence Graph Data
    concept_graph: Dict[str, Any]
    
    # 3. Cognitive Diagnosis
    diagnoses: List[ConceptMasteryScore]
    weak_concepts: List[str]
    prerequisite_gaps: List[str]
    
    # 4. Learning Trajectory / Risk Prediction
    risk_prediction: RiskPrediction
    
    # 5. Learning Prescription
    prescription: List[PrescriptionItem]
    
    # 6. Learning Recovery Path
    recovery_path: List[Dict[str, Any]]
    
    # 7. Learning Delivery
    learning_delivery: List[LearningDeliveryModule]
    
    # 8. Learning Impact (Simulation or Post-test)
    learning_impact: List[ImpactEvaluation]
    
    # 9. Updated Learner Intelligence & Reports
    reports: ThreeTierReports
    
    # Moderator Workflow (PRD Section 5)
    moderator_status: str # 'PENDING_REVIEW' | 'AUTO_DISPATCHED' | 'APPROVED'
    moderator_sla_days: int

# User & Authentication Schemas
class LoginRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = "STUDENT"

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: Optional[str] = "STUDENT"
    grade_level: Optional[int] = 6
    school_id: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    grade_level: int
    section: Optional[str] = "A"
    school_id: Optional[str] = None
    target_goal: Optional[str] = None
    token: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    user_id: str
    full_name: Optional[str] = None
    grade_level: Optional[int] = None
    subject: Optional[str] = None
    target_goal: Optional[str] = None
    role: Optional[str] = None

class RoleUpdateRequest(BaseModel):
    role: str # 'STUDENT', 'TEACHER', 'PARENT', 'ADMIN'


class ModeratorApprovalRequest(BaseModel):
    teacher_remarks: Optional[str] = None

class ModeratorSettingsRequest(BaseModel):
    moderator_enabled: bool

class ModeratorQueueItem(BaseModel):
    id: str
    attempt_id: str
    student_id: Optional[str] = None
    student_name: str
    grade: str
    subject: str
    submitted_at: str
    sla_remaining: str
    status: str
    ai_summary: str
    detected_gap: str
    teacher_remarks: Optional[str] = ""
    dispatched_at: Optional[str] = None

# -------------------------------------------------------------
# Teacher Verification & Curriculum Modification Schemas
# -------------------------------------------------------------
class RecordUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    evidence_or_trigger: Optional[str] = None
    intervention_or_followup: Optional[str] = None
    source_or_target: Optional[str] = None
    relation: Optional[str] = None
    status: Optional[str] = None
    verified_by: Optional[str] = None
    verification_notes: Optional[str] = None

class RecordVerifyRequest(BaseModel):
    status: str = "verified" # 'verified' | 'needs_revision' | 'draft'
    verified_by: str = "Teacher SME"
    verification_notes: Optional[str] = ""

class CustomQuestionCreateRequest(BaseModel):
    concept_id: str
    chapter_id: Optional[str] = None
    title: str
    prompt: str
    options: List[QuestionOption]
    difficulty: Optional[str] = "medium"
    scoring_cautions: Optional[str] = None
    author: Optional[str] = "Teacher SME"

class ConceptCreateRequest(BaseModel):
    id: Optional[str] = None
    chapter_id: str
    name: str
    description: str
    domain: Optional[str] = None
    class_level: Optional[int] = 6
    subject: Optional[str] = "Mathematics"
    prerequisites: Optional[List[str]] = []
    author: Optional[str] = "Teacher SME"

class ChapterCreateRequest(BaseModel):
    id: Optional[str] = None
    number: int
    name: str
    prefix: str
    domain: str
    pages: Optional[int] = 20
    class_level: int = 6
    subject: str = "Mathematics"

class EdgeCreateRequest(BaseModel):
    source_id: str
    target_id: str
    relation: str = "prerequisite_for"
    description: Optional[str] = None
    author: Optional[str] = "Teacher SME"


