import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class SchoolDB(Base):
    __tablename__ = "schools"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    moderator_enabled_default = Column(Boolean, default=True)
    moderator_sla_days = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("UserDB", back_populates="school", cascade="all, delete-orphan")

class UserDB(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    school_id = Column(String(36), ForeignKey("schools.id"), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False) # 'STUDENT', 'TEACHER', 'ADMIN', 'PARENT'
    grade_level = Column(Integer, default=6)
    section = Column(String(10), default="A")
    created_at = Column(DateTime, default=datetime.utcnow)

    school = relationship("SchoolDB", back_populates="users")
    attempts = relationship("AssessmentAttemptDB", back_populates="user", cascade="all, delete-orphan")

class ConceptDB(Base):
    __tablename__ = "concepts"

    id = Column(String(100), primary_key=True) # e.g. 'equivalent_fractions'
    code = Column(String(60), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    grade_level = Column(Integer, default=6)
    subject = Column(String(100), default="Mathematics")
    domain = Column(String(100), default="Number Systems")
    description = Column(Text, nullable=True)
    prerequisites = Column(JSON, default=list) # List of prerequisite concept IDs
    downstream_impact = Column(JSON, default=list) # List of blocked topics
    mastery_threshold = Column(Float, default=0.75)

class QuestionDB(Base):
    __tablename__ = "questions"

    id = Column(String(100), primary_key=True) # e.g. 'q1'
    concept_id = Column(String(100), ForeignKey("concepts.id"), nullable=False)
    concept_name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    difficulty = Column(String(20), default="medium")
    benchmark_seconds = Column(Integer, default=120)
    options = Column(JSON, default=list) # List of option objects with error taxonomies
    solution_steps = Column(JSON, default=list)

class AssessmentAttemptDB(Base):
    __tablename__ = "assessment_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    assessment_id = Column(String(100), default="diag_class6_math_01")
    status = Column(String(50), default="COMPLETED") # 'IN_PROGRESS', 'COMPLETED'
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)
    total_time_spent_seconds = Column(Integer, default=0)

    user = relationship("UserDB", back_populates="attempts")
    evidence = relationship("AttemptEvidenceDB", back_populates="attempt", cascade="all, delete-orphan")
    report = relationship("DiagnosticReportDB", back_populates="attempt", uselist=False, cascade="all, delete-orphan")

class AttemptEvidenceDB(Base):
    __tablename__ = "attempt_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("assessment_attempts.id"), nullable=False)
    question_id = Column(String(100), nullable=False)
    concept_id = Column(String(100), nullable=False)
    selected_option_id = Column(String(100), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent_seconds = Column(Integer, nullable=False)
    answer_changes = Column(Integer, default=0)
    rough_work_image_base64 = Column(Text, nullable=True)
    ocr_raw_transcription = Column(Text, nullable=True)

    attempt = relationship("AssessmentAttemptDB", back_populates="evidence")

class DiagnosticReportDB(Base):
    __tablename__ = "diagnostic_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    attempt_id = Column(String(36), ForeignKey("assessment_attempts.id"), unique=True, nullable=False)
    student_id = Column(String(36), nullable=True)
    student_name = Column(String(255), default="Alex Johnson")
    
    # 10-Stage Pipeline Outputs
    evidence_summary = Column(JSON, default=dict)
    diagnoses_matrix = Column(JSON, default=list)
    weak_concepts = Column(JSON, default=list)
    prerequisite_gaps = Column(JSON, default=list)
    risk_prediction = Column(JSON, default=dict)
    prescription = Column(JSON, default=list)
    recovery_path = Column(JSON, default=list)
    learning_delivery = Column(JSON, default=list)
    learning_impact = Column(JSON, default=list)
    
    # 3-Tier Reports (Generated by Gemini Flash)
    student_report = Column(Text, nullable=True)
    parent_report = Column(Text, nullable=True)
    teacher_report = Column(Text, nullable=True)
    admin_summary = Column(Text, nullable=True)
    
    # Moderator Workflow State (PRD Section 5)
    moderator_status = Column(String(50), default="PENDING_REVIEW") # 'PENDING_REVIEW', 'APPROVED', 'AUTO_DISPATCHED'
    teacher_remarks = Column(Text, nullable=True)
    dispatched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    attempt = relationship("AssessmentAttemptDB", back_populates="report")
