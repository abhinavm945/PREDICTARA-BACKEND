from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models.schemas import AssessmentSubmission, PipelineResponse, Question
from app.data.seed_data import QUESTIONS_DB, CONCEPTS_DB
from app.services.pipeline_engine import pipeline_engine
from app.services.mathpix_service import mathpix_service
from pydantic import BaseModel

router = APIRouter()

class OCRRequest(BaseModel):
    image_base64: str

@router.get("/questions", response_model=List[Question])
def get_assessment_questions():
    """Retrieve OBQ assessment questions for Class 6 Mathematics."""
    return list(QUESTIONS_DB.values())

@router.get("/concepts")
def get_concepts():
    """Retrieve the Class 6 Mathematics concept DAG."""
    return CONCEPTS_DB

@router.post("/ocr/mathpix")
def process_rough_work_ocr(payload: OCRRequest):
    """Direct endpoint to extract handwritten math steps via Mathpix."""
    result = mathpix_service.process_image(payload.image_base64)
    return result

import hashlib
import uuid
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import UserDB, AssessmentAttemptDB, AttemptEvidenceDB, DiagnosticReportDB
from app.models.schemas import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
    ProfileUpdateRequest
)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("/auth/login", response_model=UserResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """Logs in an existing user or creates a student account if first time."""
    email = payload.email.strip().lower()
    user = db.query(UserDB).filter_by(email=email).first()

    if not user:
        clean_name = email.split("@")[0].replace(".", " ").title()
        user = UserDB(
            id=f"usr_{uuid.uuid4().hex[:12]}",
            email=email,
            full_name=clean_name if clean_name else "Learner",
            role=payload.role or "STUDENT",
            password_hash=hash_password(payload.password),
            grade_level=6,
            section="A"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = f"prd_sess_{user.id}_{uuid.uuid4().hex[:16]}"
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        grade_level=user.grade_level,
        section=user.section,
        school_id=user.school_id,
        target_goal=user.target_goal,
        token=token
    )

@router.post("/auth/register", response_model=UserResponse)
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Registers a new user account in PostgreSQL."""
    email = payload.email.strip().lower()
    user = db.query(UserDB).filter_by(email=email).first()

    if not user:
        user = UserDB(
            id=f"usr_{uuid.uuid4().hex[:12]}",
            email=email,
            full_name=payload.full_name.strip(),
            role=payload.role or "STUDENT",
            password_hash=hash_password(payload.password),
            grade_level=payload.grade_level or 6,
            school_id=payload.school_id,
            section="A"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = f"prd_sess_{user.id}_{uuid.uuid4().hex[:16]}"
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        grade_level=user.grade_level,
        section=user.section,
        school_id=user.school_id,
        target_goal=user.target_goal,
        token=token
    )

@router.get("/auth/me/{user_id}", response_model=UserResponse)
def get_current_user(user_id: str, db: Session = Depends(get_db)):
    """Fetches user details by user ID from PostgreSQL."""
    user = db.query(UserDB).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        grade_level=user.grade_level,
        section=user.section,
        school_id=user.school_id,
        target_goal=user.target_goal,
        token=f"prd_sess_{user.id}"
    )

@router.put("/user/profile", response_model=UserResponse)
def update_user_profile(payload: ProfileUpdateRequest, db: Session = Depends(get_db)):
    """Persists user profile updates (name, grade, target learning goal) to PostgreSQL."""
    user = db.query(UserDB).filter_by(id=payload.user_id).first()
    if not user:
        # If user ID doesn't exist, search by demo user or create
        user = db.query(UserDB).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    if payload.full_name:
        user.full_name = payload.full_name.strip()
    if payload.grade_level is not None:
        user.grade_level = payload.grade_level
    if payload.target_goal:
        user.target_goal = payload.target_goal.strip()

    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        grade_level=user.grade_level,
        section=user.section,
        school_id=user.school_id,
        target_goal=user.target_goal,
        token=f"prd_sess_{user.id}"
    )

@router.get("/user/{user_id}/history")
def get_user_history(user_id: str, db: Session = Depends(get_db)):
    """Retrieves all past assessment attempts and diagnostic reports for this user."""
    attempts = db.query(AssessmentAttemptDB).filter_by(user_id=user_id).order_by(AssessmentAttemptDB.started_at.desc()).all()
    history = []
    for att in attempts:
        rep = att.report
        history.append({
            "attempt_id": att.id,
            "status": att.status,
            "started_at": att.started_at,
            "total_time_spent_seconds": att.total_time_spent_seconds,
            "weak_concepts": rep.weak_concepts if rep else [],
            "prerequisite_gaps": rep.prerequisite_gaps if rep else [],
            "moderator_status": rep.moderator_status if rep else "COMPLETED"
        })
    return {"user_id": user_id, "attempts": history}

@router.post("/pipeline/evaluate", response_model=PipelineResponse)
def evaluate_assessment(submission: AssessmentSubmission, db: Session = Depends(get_db)):
    """
    Executes the full 10-stage intelligence pipeline AND persists
    evidence, cognitive diagnostics, and 3-tier reports to the database.
    """
    try:
        pipeline_res = pipeline_engine.process_assessment(submission)

        # Match or fallback user
        target_user = db.query(UserDB).filter_by(id=submission.student_id).first()
        if not target_user:
            target_user = db.query(UserDB).filter_by(email="alex.johnson@predictara.edu").first()

        # Persist Assessment Attempt
        attempt = AssessmentAttemptDB(
            user_id=target_user.id if target_user else "usr_student_01",
            assessment_id=submission.assessment_id,
            status="COMPLETED",
            total_time_spent_seconds=sum(e.time_spent_seconds for e in submission.evidence_list)
        )
        db.add(attempt)
        db.commit()

        # Persist Question Evidence
        for e in submission.evidence_list:
            ev_record = AttemptEvidenceDB(
                attempt_id=attempt.id,
                question_id=e.question_id,
                concept_id=e.concept_id,
                selected_option_id=e.selected_option_id,
                is_correct=e.is_correct,
                time_spent_seconds=e.time_spent_seconds,
                answer_changes=e.answer_changes,
                rough_work_image_base64=e.rough_work_image_base64
            )
            db.add(ev_record)

        # Persist Diagnostic Report
        report_record = DiagnosticReportDB(
            attempt_id=attempt.id,
            student_id=submission.student_id,
            student_name=submission.student_name,
            evidence_summary=pipeline_res.evidence_summary,
            diagnoses_matrix=[d.dict() for d in pipeline_res.diagnoses],
            weak_concepts=pipeline_res.weak_concepts,
            prerequisite_gaps=pipeline_res.prerequisite_gaps,
            risk_prediction=pipeline_res.risk_prediction.dict(),
            prescription=[p.dict() for p in pipeline_res.prescription],
            recovery_path=pipeline_res.recovery_path,
            learning_delivery=[ld.dict() for ld in pipeline_res.learning_delivery],
            learning_impact=[li.dict() for li in pipeline_res.learning_impact],
            student_report=pipeline_res.reports.student_report,
            parent_report=pipeline_res.reports.parent_report,
            teacher_report=pipeline_res.reports.teacher_report,
            admin_summary=pipeline_res.reports.admin_summary,
            moderator_status=pipeline_res.moderator_status
        )
        db.add(report_record)
        db.commit()

        return pipeline_res
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
