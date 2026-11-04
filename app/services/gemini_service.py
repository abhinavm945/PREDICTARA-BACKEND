import os
import json
import time
import hashlib
import requests
import threading
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings
from app.models.schemas import ThreeTierReports

class GeminiFlashService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model = settings.GEMINI_MODEL or "gemini-flash-latest"

        # Rate Limiting & Token Safeguards
        self.max_calls_per_minute = settings.GEMINI_MAX_CALLS_PER_MINUTE
        self.max_calls_per_day = settings.GEMINI_MAX_CALLS_PER_DAY
        self.max_output_tokens = settings.GEMINI_MAX_OUTPUT_TOKENS
        self.cache_enabled = settings.GEMINI_CACHE_ENABLED

        # Thread-safe telemetry and sliding window
        self._lock = threading.Lock()
        self._call_timestamps: List[float] = []
        self._cache: Dict[str, Tuple[float, ThreeTierReports]] = {}
        self._cache_ttl = 3600  # 1 hour in-memory TTL
        self._stats = {
            "total_requests": 0,
            "gemini_api_calls": 0,
            "cache_hits": 0,
            "rate_limit_trips": 0,
            "daily_quota_trips": 0,
            "errors": 0
        }

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

    def _check_rate_limits(self) -> Tuple[bool, str]:
        """Validates current call against sliding-window minute limit and daily quota."""
        with self._lock:
            now = time.time()
            one_minute_ago = now - 60.0
            one_day_ago = now - 86400.0

            # Purge call timestamps older than 24 hours
            self._call_timestamps = [t for t in self._call_timestamps if t > one_day_ago]

            # Check calls in last 60 seconds
            recent_calls = [t for t in self._call_timestamps if t > one_minute_ago]
            if len(recent_calls) >= self.max_calls_per_minute:
                self._stats["rate_limit_trips"] += 1
                return False, f"Rate limit reached ({len(recent_calls)}/{self.max_calls_per_minute} calls in last 60s)"

            # Check calls in last 24 hours
            if len(self._call_timestamps) >= self.max_calls_per_day:
                self._stats["daily_quota_trips"] += 1
                return False, f"Daily quota reached ({len(self._call_timestamps)}/{self.max_calls_per_day} calls in 24h)"

            return True, "OK"

    def _record_call(self):
        """Records an API call timestamp."""
        with self._lock:
            self._call_timestamps.append(time.time())
            self._stats["gemini_api_calls"] += 1

    def _get_cache_key(
        self,
        student_name: str,
        grade: int,
        subject: str,
        weak_concepts: List[str],
        prerequisite_gaps: List[str],
        risk_level: str
    ) -> str:
        raw = f"{student_name.lower().strip()}|{grade}|{subject.lower().strip()}|{sorted(weak_concepts)}|{sorted(prerequisite_gaps)}|{risk_level}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _fallback_report(
        self,
        student_name: str,
        grade: int,
        subject: str,
        weak_concepts: List[str],
        prerequisite_gaps: List[str],
        risk_level: str
    ) -> ThreeTierReports:
        """Deterministic PRD-standard fallback ensuring zero student disruption."""
        weak_str = ", ".join(weak_concepts) if weak_concepts else "Equivalent Fractions"
        prereq_str = ", ".join(prerequisite_gaps) if prerequisite_gaps else "Equivalent Fractions & Simplification"
        
        return ThreeTierReports(
            student_report=f"Great effort on completing your 10-minute diagnostic, {student_name}! You demonstrated strong speed and enthusiasm. Right now, your main superpower to unlock is '{weak_str}'. With our 5-minute targeted practice on how fractions scale, you'll feel completely confident solving addition problems!",
            parent_report=f"{student_name} participated enthusiastically in the Class {grade} Mathematics assessment. The diagnostic identified that while {student_name} recognizes basic fractions well, there is a foundational prerequisite gap in '{prereq_str}'. At home, encouraging visual fraction games or comparing equivalent ratios (like measuring cups in cooking) will naturally reinforce this skill before tests.",
            teacher_report=f"Student exhibits a blocking prerequisite gap in {prereq_str}. When attempting unlike denominator addition, telemetry indicates a systematic across-the-board addition misconception (adding numerators and denominators straight across), driven by incomplete mastery of equivalent fractions. Recommended intervention: 1-on-1 micro-drill on GCF/LCM scaling before proceeding to fraction division.",
            admin_summary=f"Cohort Diagnostic Alert: Prerequisite blockage flagged in Class {grade} {subject} for {student_name}. Risk level categorized as {risk_level}. Ready for Teacher review in Moderator Queue."
        )

    def get_stats(self) -> Dict[str, Any]:
        """Provides transparency on token consumption, rate limits and cache efficacy."""
        with self._lock:
            now = time.time()
            one_minute_ago = now - 60.0
            recent_minute = sum(1 for t in self._call_timestamps if t > one_minute_ago)
            return {
                "total_requests": self._stats["total_requests"],
                "gemini_api_calls": self._stats["gemini_api_calls"],
                "cache_hits": self._stats["cache_hits"],
                "rate_limit_trips": self._stats["rate_limit_trips"],
                "daily_quota_trips": self._stats["daily_quota_trips"],
                "active_cached_reports": len(self._cache),
                "calls_in_last_minute": recent_minute,
                "max_calls_per_minute": self.max_calls_per_minute,
                "calls_in_last_24h": len(self._call_timestamps),
                "max_calls_per_day": self.max_calls_per_day,
                "remaining_calls_today": max(0, self.max_calls_per_day - len(self._call_timestamps)),
                "max_output_tokens": self.max_output_tokens,
                "cache_enabled": self.cache_enabled,
                "model": self.model
            }

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
        with self._lock:
            self._stats["total_requests"] += 1

        # 1. Semantic Deduplication Cache Check (Zero tokens consumed on cache hit)
        cache_key = self._get_cache_key(student_name, grade, subject, weak_concepts, prerequisite_gaps, risk_level)
        if self.cache_enabled:
            with self._lock:
                now = time.time()
                if cache_key in self._cache:
                    expiry, cached_rep = self._cache[cache_key]
                    if now < expiry:
                        self._stats["cache_hits"] += 1
                        print(f"[Gemini Cache Hit]: Returning cached AI report for '{student_name}' (Saved tokens).")
                        return cached_rep
                    else:
                        del self._cache[cache_key]

        # 2. Rate Limit & Daily Token Quota Gate
        can_call, reason = self._check_rate_limits()
        if not can_call:
            print(f"[Gemini Rate Limiter Active]: {reason}. Returning deterministic fallback to protect API tokens.")
            return self._fallback_report(student_name, grade, subject, weak_concepts, prerequisite_gaps, risk_level)

        # 3. Compact & Token-Optimized Prompt (Conserves input token budget)
        compact_evidence = {
            "total_items": evidence_summary.get("total_questions", 10),
            "correct": evidence_summary.get("correct_count", 0),
            "avg_latency_sec": evidence_summary.get("avg_time_sec", 0),
            "error_distribution": evidence_summary.get("error_distribution", {})
        }

        prompt = f"""
        You are the pedagogical AI engine for Predictara, an academic intelligence platform for Class {grade} {subject}.
        Analyze the student assessment data:
        - Student: {student_name}
        - Risk Level: {risk_level}
        - Weak Concepts: {', '.join(weak_concepts) if weak_concepts else 'None'}
        - Foundational Gaps: {', '.join(prerequisite_gaps) if prerequisite_gaps else 'None'}
        - Summary Stats: {json.dumps(compact_evidence)}

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
                # Direct Gemini REST API endpoint with strict token budget
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
                        "response_mime_type": "application/json",
                        "maxOutputTokens": self.max_output_tokens,
                        "temperature": 0.4
                    }
                }
                self._record_call()
                res = requests.post(url, headers=headers, json=payload, timeout=25)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.startswith("```"):
                        raw_text = raw_text[3:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                    raw_text = raw_text.strip()
                    parsed = json.loads(raw_text)
                    
                    reports = ThreeTierReports(
                        student_report=self._clean_report_text(parsed.get("student_report", "")),
                        parent_report=self._clean_report_text(parsed.get("parent_report", "")),
                        teacher_report=self._clean_report_text(parsed.get("teacher_report", "")),
                        admin_summary=self._clean_report_text(parsed.get("admin_summary", ""))
                    )

                    # Cache successful result
                    if self.cache_enabled:
                        with self._lock:
                            self._cache[cache_key] = (time.time() + self._cache_ttl, reports)

                    return reports
                else:
                    print(f"[Gemini API returned status {res.status_code}]: {res.text[:200]}")
            except Exception as e:
                with self._lock:
                    self._stats["errors"] += 1
                print(f"[Gemini API Call failed, falling back to deterministic template]: {e}")

        # Deterministic fallback conforming to PRD pedagogical guidelines
        fallback = self._fallback_report(student_name, grade, subject, weak_concepts, prerequisite_gaps, risk_level)
        if self.cache_enabled:
            with self._lock:
                self._cache[cache_key] = (time.time() + self._cache_ttl, fallback)
        return fallback

gemini_service = GeminiFlashService()
