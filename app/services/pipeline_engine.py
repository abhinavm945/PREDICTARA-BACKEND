from typing import List, Dict, Any
from app.models.schemas import (
    AssessmentSubmission,
    PipelineResponse,
    ConceptMasteryScore,
    RiskPrediction,
    PrescriptionItem,
    ImpactEvaluation,
    ErrorCategory
)
from app.data.seed_data import CONCEPTS_DB, QUESTIONS_DB, LEARNING_MODULES_DB
from app.services.mathpix_service import mathpix_service
from app.services.gemini_service import gemini_service
from app.core.config import settings

class IntelligencePipelineEngine:
    """
    Executes the complete 10-stage cognitive intelligence lifecycle:
    1. Learning Evidence (Telemetry + Mathpix OCR)
    2. Concept Intelligence Graph (DAG Evaluation)
    3. Cognitive Diagnosis (Mastery, Gap Detection, Error Taxonomy)
    4. Learning Trajectory / Risk Prediction (Downstream blockages)
    5. Learning Prescription (Pedagogical focus)
    6. Learning Recovery Path (Ordered prerequisites)
    7. Learning Delivery (Micro-explanations + Worked examples)
    8. Learning Impact (Pre-to-post mastery simulation/evaluation)
    9. Updated Learner Intelligence (3-tier reports via Gemini Flash)
    10. Moderator Review Queue (PRD Section 5)
    """

    def process_assessment(self, submission: AssessmentSubmission) -> PipelineResponse:
        evidence_list = submission.evidence_list

        # ---------------------------------------------------------
        # STAGE 1: Learning Evidence Processing
        # ---------------------------------------------------------
        evidence_by_concept: Dict[str, List[Any]] = {}
        error_distribution: Dict[str, int] = {}
        ocr_results: List[Dict[str, Any]] = []

        total_questions = len(evidence_list)
        total_time = 0
        total_changes = 0
        correct_count = 0

        for item in evidence_list:
            total_time += item.time_spent_seconds
            total_changes += item.answer_changes
            if item.is_correct:
                correct_count += 1

            if item.concept_id not in evidence_by_concept:
                evidence_by_concept[item.concept_id] = []
            evidence_by_concept[item.concept_id].append(item)

            # Check if Mathpix OCR is attached for rough work
            if item.rough_work_image_base64:
                ocr_out = mathpix_service.process_image(item.rough_work_image_base64)
                ocr_results.append({
                    "question_id": item.question_id,
                    "ocr": ocr_out
                })

            # Map engineered error taxonomy from question option
            q = QUESTIONS_DB.get(item.question_id)
            if q and not item.is_correct:
                selected_opt = next((opt for opt in q.options if opt.id == item.selected_option_id), None)
                if selected_opt and selected_opt.error_category:
                    cat = selected_opt.error_category.value
                    error_distribution[cat] = error_distribution.get(cat, 0) + 1

        evidence_summary = {
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "accuracy": round(correct_count / max(total_questions, 1), 2),
            "avg_time_per_question": round(total_time / max(total_questions, 1)),
            "total_answer_revisions": total_changes,
            "ocr_processed_steps": len(ocr_results),
            "error_distribution": error_distribution
        }

        # ---------------------------------------------------------
        # STAGE 2 & 3: Concept Intelligence Graph & Cognitive Diagnosis
        # ---------------------------------------------------------
        diagnoses: List[ConceptMasteryScore] = []
        weak_concepts: List[str] = []
        prerequisite_gaps: List[str] = []

        for cid, concept in CONCEPTS_DB.items():
            c_evidence = evidence_by_concept.get(cid, [])
            if not c_evidence:
                continue

            c_total = len(c_evidence)
            c_correct = sum(1 for e in c_evidence if e.is_correct)
            c_accuracy = c_correct / max(c_total, 1)
            c_time = sum(e.time_spent_seconds for e in c_evidence) // max(c_total, 1)
            c_changes = sum(e.answer_changes for e in c_evidence)

            # Heuristic cognitive scoring formula
            time_factor = 0.15 if c_time < 60 else (0.05 if c_time > 100 else 0.10)
            stability_factor = max(0.0, 0.15 - (c_changes * 0.05))
            score = round((c_accuracy * 0.70) + (time_factor * c_accuracy) + (stability_factor * c_accuracy), 2)
            score = max(0.10, min(score, 0.98))

            status = "mastered" if score >= concept.mastery_threshold else ("developing" if score >= 0.50 else "weak")
            confidence = min(0.95, round(0.65 + (c_total * 0.10), 2))

            # Prerequisite gap logic: Is this weak concept a prerequisite for other topics in the graph?
            is_prereq_gap = False
            reason = "Adequate conceptual grasp demonstrated."
            detected_err = None

            if status == "weak":
                weak_concepts.append(concept.name)
                # Check downstream graph dependencies
                if concept.downstream_impact:
                    is_prereq_gap = True
                    prerequisite_gaps.append(concept.name)
                    reason = f"CRITICAL PREREQUISITE GAP: Incomplete mastery blocks {', '.join(concept.downstream_impact)}."
                else:
                    reason = f"Weakness identified in {concept.name}. Requires targeted remediation."
                detected_err = ErrorCategory.PREREQUISITE_CONCEPT_GAP
            elif status == "developing":
                reason = f"Developing concept. Reinforcing fundamentals will build full fluency in {concept.name}."

            diagnoses.append(ConceptMasteryScore(
                concept_id=cid,
                concept_name=concept.name,
                score=score,
                status=status,
                confidence=confidence,
                accuracy=round(c_accuracy, 2),
                avg_time_seconds=c_time,
                answer_changes=c_changes,
                detected_error_category=detected_err,
                prerequisite_gap=is_prereq_gap,
                reason=reason
            ))

        # ---------------------------------------------------------
        # STAGE 4: Learning Trajectory / Risk Prediction
        # ---------------------------------------------------------
        blocked_topics = []
        for d in diagnoses:
            if d.prerequisite_gap:
                c = CONCEPTS_DB.get(d.concept_id)
                if c:
                    blocked_topics.extend(c.downstream_impact)
        blocked_topics = list(set(blocked_topics))

        risk_score = min(1.0, round((len(prerequisite_gaps) * 0.4) + (len(weak_concepts) * 0.2), 2))
        risk_level = "CRITICAL" if risk_score >= 0.7 else ("HIGH" if risk_score >= 0.4 else "LOW")
        trajectory_note = (
            f"If unaddressed, gaps in {', '.join(prerequisite_gaps or weak_concepts or ['core topics'])} "
            f"will predictably impede progression in {', '.join(blocked_topics or ['upcoming units'])}."
        )

        risk_prediction = RiskPrediction(
            overall_risk_level=risk_level,
            risk_score=risk_score,
            blocked_future_topics=blocked_topics,
            longitudinal_trajectory_note=trajectory_note
        )

        # ---------------------------------------------------------
        # STAGE 5: Learning Prescription
        # ---------------------------------------------------------
        prescription: List[PrescriptionItem] = []
        step_idx = 1
        # Order: Prerequisite gaps first, then weak concepts
        sorted_diagnoses = sorted(
            diagnoses,
            key=lambda x: (not x.prerequisite_gap, x.status != "weak", x.score)
        )

        for d in sorted_diagnoses:
            if d.status != "mastered":
                prescription.append(PrescriptionItem(
                    step_number=step_idx,
                    concept_id=d.concept_id,
                    concept_name=d.concept_name,
                    priority="HIGH" if d.prerequisite_gap or d.status == "weak" else "MEDIUM",
                    is_prerequisite_gap=d.prerequisite_gap,
                    pedagogical_focus=f"Targeted review of {d.concept_name} with worked examples and active micro-practice.",
                    recommended_duration_mins=10 if d.prerequisite_gap else 5
                ))
                step_idx += 1

        # ---------------------------------------------------------
        # STAGE 6: Learning Recovery Path
        # ---------------------------------------------------------
        recovery_path = [
            {
                "order": p.step_number,
                "concept_id": p.concept_id,
                "concept_name": p.concept_name,
                "stage": "Prerequisite Foundation" if p.is_prerequisite_gap else "Core Practice",
                "estimated_minutes": p.recommended_duration_mins
            }
            for p in prescription
        ]

        # ---------------------------------------------------------
        # STAGE 7: Learning Delivery
        # ---------------------------------------------------------
        learning_delivery = []
        for p in prescription:
            module = LEARNING_MODULES_DB.get(p.concept_id)
            if module:
                learning_delivery.append(module)

        # ---------------------------------------------------------
        # STAGE 8: Learning Impact (Simulated or Pre-to-Post Evaluation)
        # ---------------------------------------------------------
        learning_impact = []
        for d in diagnoses:
            boost = 0.35 if d.status == "weak" else 0.18
            post_score = min(0.92, round(d.score + boost, 2))
            new_status = "mastered" if post_score >= 0.75 else "developing"
            learning_impact.append(ImpactEvaluation(
                concept_id=d.concept_id,
                concept_name=d.concept_name,
                mastery_before=d.score,
                mastery_after=post_score,
                delta=round(post_score - d.score, 2),
                status_progression=f"{d.status} -> {new_status}"
            ))

        # ---------------------------------------------------------
        # STAGE 9: Updated Learner Intelligence & 3-Tier Reports (Gemini Flash)
        # ---------------------------------------------------------
        reports = gemini_service.generate_three_tier_reports(
            student_name=submission.student_name,
            grade=submission.grade_level,
            subject=submission.subject,
            weak_concepts=weak_concepts,
            prerequisite_gaps=prerequisite_gaps,
            risk_level=risk_level,
            evidence_summary=evidence_summary
        )

        # ---------------------------------------------------------
        # STAGE 10: Moderator Workflow (PRD Section 5)
        # ---------------------------------------------------------
        moderator_enabled = submission.moderator_override if submission.moderator_override is not None else settings.DEFAULT_MODERATOR_ENABLED
        mod_status = "PENDING_REVIEW" if moderator_enabled else "AUTO_DISPATCHED"

        # Concept graph visualization payload
        concept_graph_payload = {
            "nodes": [
                {"id": c.id, "name": c.name, "prerequisites": c.prerequisites, "downstream": c.downstream_impact}
                for c in CONCEPTS_DB.values()
            ]
        }

        return PipelineResponse(
            student_id=submission.student_id,
            student_name=submission.student_name,
            assessment_id=submission.assessment_id,
            evidence_summary=evidence_summary,
            concept_graph=concept_graph_payload,
            diagnoses=diagnoses,
            weak_concepts=weak_concepts,
            prerequisite_gaps=prerequisite_gaps,
            risk_prediction=risk_prediction,
            prescription=prescription,
            recovery_path=recovery_path,
            learning_delivery=learning_delivery,
            learning_impact=learning_impact,
            reports=reports,
            moderator_status=mod_status,
            moderator_sla_days=settings.MODERATOR_SLA_DAYS
        )

pipeline_engine = IntelligencePipelineEngine()
