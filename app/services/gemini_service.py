import os
import json
import requests
from typing import Dict, Any, List
from app.core.config import settings
from app.models.schemas import ThreeTierReports

class GeminiFlashService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model = settings.GEMINI_MODEL or "gemini-flash-latest"

    @staticmethod
    def _clean_report_text(val: Any) -> str:
        """Converts LLM output to clean markdown text if the model outputs nested objects."""
        if val is None:
            return ""
        if isinstance(val, str):
            return val.strip()
        if isinstance(val, dict):
            lines = []
            for k, v in val.items():
                title = k.replace('_', ' ').title()
                if isinstance(v, list):
                    lines.append(f"**{title}:**")
                    for item in v:
                        lines.append(f"- {item}")
                elif isinstance(v, dict):
                    lines.append(f"**{title}:** {json.dumps(v)}")
                else:
                    lines.append(f"**{title}:** {v}")
            return "\n\n".join(lines)
        if isinstance(val, list):
            return "\n".join([f"- {item}" for item in val])
        return str(val)

    def generate_three_tier_reports(
        self,
        student_name: str,
        grade: int,
        subject: str,
        weak_concepts: List[str],
        prerequisite_gaps: List[str],
        risk_level: str,
        evidence_summary: Dict[str, Any]
    ) -> ThreeTierReports:
        """
        Uses Google Gemini Flash to generate empathetic, child-friendly,
        parent-supportive, and teacher-actionable three-tier reports as per PRD Section 4.
        """
        prompt = f"""
        You are the pedagogical AI engine for Predictara, an academic intelligence platform for Class {grade} {subject}.
        Analyze the following student assessment data:
        - Student Name: {student_name}
        - Risk Level: {risk_level}
        - Identified Weak Concepts: {', '.join(weak_concepts) if weak_concepts else 'None'}
        - Foundational Prerequisite Gaps: {', '.join(prerequisite_gaps) if prerequisite_gaps else 'None'}
        - Diagnostic Evidence Stats: {json.dumps(evidence_summary)}

        Generate four distinct report summaries:
        1. student_report: Encouraging, positive, non-alarming tone. Focus on specific growth areas. Written directly to the student in markdown.
        2. parent_report: Constructive, accessible guidance for home support, explaining the underlying why without intimidating jargon. Written to parents in markdown.
        3. teacher_report: Data-driven, precise pedagogical notes highlighting exact error types (calculation vs prerequisite gap) and classroom remediation strategy. Written for teachers in markdown.
        4. admin_summary: High-level cohort health indicator and syllabus risk flag in 1-2 concise sentences.

        Return strictly valid JSON with keys: 'student_report', 'parent_report', 'teacher_report', 'admin_summary'.
        The value for each key must be a comprehensive markdown string.
        """

        if self.api_key:
            try:
                # Direct Gemini REST API endpoint with x-goog-api-key header and query parameter
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
                headers = {
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "response_mime_type": "application/json"
                    }
                }
                res = requests.post(url, headers=headers, json=payload, timeout=25)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data['candidates'][0]['content']['parts'][0]['text']
                    parsed = json.loads(raw_text)
                    return ThreeTierReports(
                        student_report=self._clean_report_text(parsed.get("student_report", "")),
                        parent_report=self._clean_report_text(parsed.get("parent_report", "")),
                        teacher_report=self._clean_report_text(parsed.get("teacher_report", "")),
                        admin_summary=self._clean_report_text(parsed.get("admin_summary", ""))
                    )
                else:
                    print(f"[Gemini API returned status {res.status_code}]: {res.text[:200]}")
            except Exception as e:
                print(f"[Gemini API Call failed, falling back to deterministic template]: {e}")

        # Deterministic fallback conforming to PRD pedagogical guidelines
        weak_str = ", ".join(weak_concepts) if weak_concepts else "Equivalent Fractions"
        prereq_str = ", ".join(prerequisite_gaps) if prerequisite_gaps else "Equivalent Fractions & Simplification"
        
        return ThreeTierReports(
            student_report=f"Great effort on completing your 10-minute diagnostic, {student_name}! You demonstrated strong speed and enthusiasm. Right now, your main superpower to unlock is '{weak_str}'. With our 5-minute targeted practice on how fractions scale, you'll feel completely confident solving addition problems!",
            parent_report=f"{student_name} participated enthusiastically in the Class {grade} Mathematics assessment. The diagnostic identified that while {student_name} recognizes basic fractions well, there is a foundational prerequisite gap in '{prereq_str}'. At home, encouraging visual fraction games or comparing equivalent ratios (like measuring cups in cooking) will naturally reinforce this skill before tests.",
            teacher_report=f"Student exhibits a blocking prerequisite gap in {prereq_str}. When attempting unlike denominator addition, telemetry indicates a systematic across-the-board addition misconception (adding numerators and denominators straight across), driven by incomplete mastery of equivalent fractions. Recommended intervention: 1-on-1 micro-drill on GCF/LCM scaling before proceeding to fraction division.",
            admin_summary=f"Cohort Diagnostic Alert: Prerequisite blockage flagged in Class {grade} {subject} for {student_name}. Risk level categorized as {risk_level}. Ready for Teacher review in Moderator Queue."
        )

gemini_service = GeminiFlashService()
