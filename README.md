# Predictara Backend Service

AI-Powered Academic Intelligence Platform Backend implementing the complete 10-stage learning intelligence lifecycle:

1. **Learning Evidence**: Captures question-wise response options, time-to-first-click, total duration, and answer-change count, integrated with **Mathpix OCR** for handwritten rough-work steps.
2. **Concept Intelligence Graph**: DAG mapping Class 6 Mathematics concepts, prerequisites, and downstream blocking dependencies.
3. **Cognitive Diagnosis**: Identifies accuracy, confidence, and root-cause mistake categories (Calculation vs Formula vs Prerequisite Gap).
4. **Learning Trajectory / Risk Prediction**: Predicts future academic failure or blockage in upcoming units if gaps are left unaddressed.
5. **Learning Prescription**: Automatically prioritizes foundational prerequisite gaps before advanced modules.
6. **Learning Recovery Path**: Generates structured ordered steps and recommended study times.
7. **Learning Delivery**: Delivers conceptual breakdowns, step-by-step worked solutions, and practice questions.
8. **Learning Impact**: Tracks before-vs-after mastery gains and status progression.
9. **Updated Learner Intelligence**: Generates 3-Tier Reports (Student, Parent, Teacher, Admin) via **Google Gemini Flash**.
10. **Moderator Review Queue**: Enforces PRD Section 5 Teacher review workflow and SLA tracking.

---

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables (.env)
```env
MATHPIX_APP_ID=your_mathpix_app_id
MATHPIX_APP_KEY=your_mathpix_app_key
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Run FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.
