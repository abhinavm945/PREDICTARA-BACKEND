from app.core.database import SessionLocal
from app.models.db_models import ConceptDB, QuestionDB, SchoolDB, UserDB
from app.data.seed_data import CONCEPTS_DB, QUESTIONS_DB
from sqlalchemy import text

def seed_database():
    """Seeds initial Class 6 Math concepts, questions, and default school/demo user."""
    db = SessionLocal()
    try:
        # Safe schema migration for user columns
        try:
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS target_goal VARCHAR(255);"))
            db.commit()
        except Exception:
            db.rollback()

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

        # Seed ChapterDB and CurriculumRecordDB from class6_knowledge_graph.json
        import json
        from pathlib import Path
        from app.models.db_models import ChapterDB, CurriculumRecordDB
        
        kg_path = Path(__file__).resolve().parent.parent / "data" / "class6_knowledge_graph.json"
        if kg_path.exists():
            with open(kg_path, "r", encoding="utf-8") as f:
                kg_data = json.load(f)
                
            # 1. Seed Chapters
            if db.query(ChapterDB).count() == 0:
                for ch in kg_data.get("chapters", []):
                    ch_db = ChapterDB(
                        id=ch.get("id"),
                        number=ch.get("number"),
                        name=ch.get("name"),
                        prefix=ch.get("prefix"),
                        domain=ch.get("domain"),
                        pages=ch.get("pages", 20)
                    )
                    db.add(ch_db)
                db.commit()

            # 2. Seed Curriculum Records (all 511+ records)
            if db.query(CurriculumRecordDB).count() == 0:
                records_by_type = kg_data.get("records_by_type", {})
                for r_type, r_list in records_by_type.items():
                    for item in r_list:
                        item_id = item.get("id")
                        if not item_id:
                            continue
                        
                        prefix = ""
                        if "-" in item_id:
                            prefix = item_id.split("-")[0]
                        elif "_" in item_id:
                            prefix = item_id.split("_")[0]
                            
                        curr_rec = CurriculumRecordDB(
                            id=item_id,
                            record_type=r_type,
                            prefix=prefix,
                            name=item.get("name") or item_id,
                            description=item.get("description"),
                            source_or_target=item.get("source_or_target"),
                            relation=item.get("relation"),
                            evidence_or_trigger=item.get("evidence_or_trigger"),
                            intervention_or_followup=item.get("intervention_or_followup"),
                            domain=item.get("domain"),
                            class_level=item.get("class_level", 6),
                            subject=item.get("subject", "Mathematics"),
                            status=item.get("status", "draft"),
                            verified_by=item.get("verified_by"),
                            verification_notes=item.get("verification_notes")
                        )
                        db.add(curr_rec)
                db.commit()
    finally:
        db.close()
