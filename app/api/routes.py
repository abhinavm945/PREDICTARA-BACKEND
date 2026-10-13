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

@router.post("/pipeline/evaluate", response_model=PipelineResponse)
def evaluate_assessment(submission: AssessmentSubmission):
    """
    Executes the full 10-stage intelligence pipeline:
    Learning Evidence -> Concept Intelligence Graph -> Cognitive Diagnosis ->
    Learning Trajectory / Risk Prediction -> Learning Prescription ->
    Learning Recovery Path -> Learning Delivery -> Learning Impact ->
    Updated Learner Intelligence (Gemini Flash) -> Moderator Review Queue
    """
    try:
        return pipeline_engine.process_assessment(submission)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
