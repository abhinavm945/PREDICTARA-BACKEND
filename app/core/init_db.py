from app.core.database import SessionLocal
from app.models.db_models import ConceptDB, QuestionDB, SchoolDB, UserDB
from app.data.seed_data import CONCEPTS_DB, QUESTIONS_DB

def seed_database():
    """Seeds initial Class 6 Math concepts, questions, and default school/demo user."""
    db = SessionLocal()
    try:
        # Seed default school
        school = db.query(SchoolDB).filter_by(code="DEMO_SCH_01").first()
        if not school:
            school = SchoolDB(
                id="sch_demo_01",
                name="Predictara Model School",
                code="DEMO_SCH_01",
                moderator_enabled_default=True,
                moderator_sla_days=3
            )
            db.add(school)
            db.commit()

        # Seed demo student
        user = db.query(UserDB).filter_by(email="alex.johnson@predictara.edu").first()
        if not user:
            user = UserDB(
                id="usr_student_01",
                school_id=school.id,
                email="alex.johnson@predictara.edu",
                full_name="Alex Johnson",
                role="STUDENT",
                grade_level=6,
                section="A"
            )
            db.add(user)
            db.commit()

        # Seed concepts
        for cid, c in CONCEPTS_DB.items():
            existing = db.query(ConceptDB).filter_by(id=cid).first()
            if not existing:
                c_record = ConceptDB(
                    id=c.id,
                    code=c.code,
                    name=c.name,
                    grade_level=c.grade_level,
                    subject=c.subject,
                    domain=c.domain,
                    description=c.description,
                    prerequisites=c.prerequisites,
                    downstream_impact=c.downstream_impact,
                    mastery_threshold=c.mastery_threshold
                )
                db.add(c_record)
        db.commit()

        # Seed questions
        for qid, q in QUESTIONS_DB.items():
            existing = db.query(QuestionDB).filter_by(id=qid).first()
            if not existing:
                q_record = QuestionDB(
                    id=q.id,
                    concept_id=q.concept_id,
                    concept_name=q.concept_name,
                    title=q.title,
                    prompt=q.prompt,
                    difficulty=q.difficulty,
                    benchmark_seconds=q.benchmark_seconds,
                    options=[opt.dict() for opt in q.options],
                    solution_steps=q.solution_steps
                )
                db.add(q_record)
        db.commit()
    finally:
        db.close()
