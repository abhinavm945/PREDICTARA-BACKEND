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

from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import AssessmentAttemptDB, AttemptEvidenceDB, DiagnosticReportDB

@router.post("/pipeline/evaluate", response_model=PipelineResponse)
def evaluate_assessment(submission: AssessmentSubmission, db: Session = Depends(get_db)):
    """
    Executes the full 10-stage intelligence pipeline AND persists
    evidence, cognitive diagnostics, and 3-tier reports to the database.
    """
    try:
        pipeline_res = pipeline_engine.process_assessment(submission)

        # Persist Assessment Attempt
        attempt = AssessmentAttemptDB(
            user_id="usr_student_01",
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
