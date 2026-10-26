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
                        pages=ch.get("pages", 20),
                        class_level=6,
                        subject="Mathematics"
                    )
                    db.add(ch_db)
                db.commit()

            # Additional multi-grade chapters
            additional_chapters = [
                # Grade 7 Mathematics
                {"id": "CH01_INT7", "number": 1, "name": "Integers", "prefix": "INT7", "domain": "Number Systems & Arithmetic", "pages": 24, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH02_FRC7", "number": 2, "name": "Fractions and Decimals", "prefix": "FRC7", "domain": "Fractions & Rational Numbers", "pages": 26, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH03_DAT7", "number": 3, "name": "Data Handling", "prefix": "DAT7", "domain": "Statistics & Data Handling", "pages": 22, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH04_EQU7", "number": 4, "name": "Simple Equations", "prefix": "EQU7", "domain": "Algebra & Linear Equations", "pages": 20, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH05_LIN7", "number": 5, "name": "Lines and Angles", "prefix": "LIN7", "domain": "Geometry", "pages": 20, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH06_TRI7", "number": 6, "name": "The Triangle and its Properties", "prefix": "TRI7", "domain": "Geometry & Triangles", "pages": 24, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH07_CMP7", "number": 7, "name": "Comparing Quantities", "prefix": "CMP7", "domain": "Ratio, Proportions & Percentages", "pages": 22, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH08_RAT7", "number": 8, "name": "Rational Numbers", "prefix": "RAT7", "domain": "Rational Numbers", "pages": 20, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH09_PER7", "number": 9, "name": "Perimeter and Area", "prefix": "PER7", "domain": "Mensuration & Geometry", "pages": 24, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH10_ALG7", "number": 10, "name": "Algebraic Expressions", "prefix": "ALG7", "domain": "Algebraic Expressions", "pages": 22, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH11_EXP7", "number": 11, "name": "Exponents and Powers", "prefix": "EXP7", "domain": "Number Theory & Powers", "pages": 18, "class_level": 7, "subject": "Mathematics"},
                {"id": "CH12_SYM7", "number": 12, "name": "Symmetry", "prefix": "SYM7", "domain": "Transformational Geometry", "pages": 16, "class_level": 7, "subject": "Mathematics"},
                # Grade 8 Mathematics
                {"id": "CH01_RAT8", "number": 1, "name": "Rational Numbers", "prefix": "RAT8", "domain": "Number Systems", "pages": 20, "class_level": 8, "subject": "Mathematics"},
                {"id": "CH02_LEQ8", "number": 2, "name": "Linear Equations in One Variable", "prefix": "LEQ8", "domain": "Algebra", "pages": 22, "class_level": 8, "subject": "Mathematics"},
                {"id": "CH03_QUA8", "number": 3, "name": "Understanding Quadrilaterals", "prefix": "QUA8", "domain": "Geometry", "pages": 24, "class_level": 8, "subject": "Mathematics"},
                {"id": "CH04_DAT8", "number": 4, "name": "Data Handling", "prefix": "DAT8", "domain": "Statistics", "pages": 20, "class_level": 8, "subject": "Mathematics"},
                {"id": "CH05_SQR8", "number": 5, "name": "Squares and Square Roots", "prefix": "SQR8", "domain": "Number Theory", "pages": 22, "class_level": 8, "subject": "Mathematics"},
                {"id": "CH06_CUB8", "number": 6, "name": "Cubes and Cube Roots", "prefix": "CUB8", "domain": "Number Theory", "pages": 18, "class_level": 8, "subject": "Mathematics"},
                {"id": "CH07_CMP8", "number": 7, "name": "Comparing Quantities", "prefix": "CMP8", "domain": "Commercial Mathematics", "pages": 24, "class_level": 8, "subject": "Mathematics"},
                {"id": "CH08_ALG8", "number": 8, "name": "Algebraic Expressions and Identities", "prefix": "ALG8", "domain": "Algebra", "pages": 26, "class_level": 8, "subject": "Mathematics"},
                {"id": "CH09_MEN8", "number": 9, "name": "Mensuration", "prefix": "MEN8", "domain": "Mensuration", "pages": 26, "class_level": 8, "subject": "Mathematics"},
                {"id": "CH10_EXP8", "number": 10, "name": "Exponents and Powers", "prefix": "EXP8", "domain": "Number Systems", "pages": 18, "class_level": 8, "subject": "Mathematics"},
                # Grade 5 Foundations
                {"id": "CH01_NUM5", "number": 1, "name": "The Fish Tale (Large Numbers)", "prefix": "NUM5", "domain": "Number Sense", "pages": 18, "class_level": 5, "subject": "Mathematics"},
                {"id": "CH02_SHP5", "number": 2, "name": "Shapes and Angles", "prefix": "SHP5", "domain": "Geometry Foundations", "pages": 20, "class_level": 5, "subject": "Mathematics"},
                {"id": "CH03_SQR5", "number": 3, "name": "How Many Squares? (Area Intuition)", "prefix": "SQR5", "domain": "Measurement", "pages": 16, "class_level": 5, "subject": "Mathematics"},
                {"id": "CH04_FRC5", "number": 4, "name": "Parts and Wholes (Fraction Foundations)", "prefix": "FRC5", "domain": "Fractions", "pages": 22, "class_level": 5, "subject": "Mathematics"},
                {"id": "CH05_SYM5", "number": 5, "name": "Does it Look the Same? (Symmetry)", "prefix": "SYM5", "domain": "Transformational Geometry", "pages": 18, "class_level": 5, "subject": "Mathematics"},
                {"id": "CH06_FAC5", "number": 6, "name": "Be My Multiple, I'll be Your Factor", "prefix": "FAC5", "domain": "Number Theory Foundations", "pages": 20, "class_level": 5, "subject": "Mathematics"},
                # Grade 6 Science (Curiosity)
                {"id": "CH01_SCI6", "number": 1, "name": "The Wonderful World of Science", "prefix": "SCI6", "domain": "Scientific Enquiry", "pages": 16, "class_level": 6, "subject": "Science"},
                {"id": "CH02_DIV6", "number": 2, "name": "Diversity in the Living World", "prefix": "DIV6", "domain": "Biology & Living World", "pages": 22, "class_level": 6, "subject": "Science"},
                {"id": "CH03_NUT6", "number": 3, "name": "Mindful Eating: A Path to a Healthy Body", "prefix": "NUT6", "domain": "Nutrition & Physiology", "pages": 20, "class_level": 6, "subject": "Science"},
                {"id": "CH04_MAG6", "number": 4, "name": "Exploring Magnets", "prefix": "MAG6", "domain": "Physics & Magnetism", "pages": 18, "class_level": 6, "subject": "Science"},
                {"id": "CH05_MOT6", "number": 5, "name": "Measurement of Length and Motion", "prefix": "MOT6", "domain": "Physics & Kinematics", "pages": 22, "class_level": 6, "subject": "Science"},
                {"id": "CH06_MAT6", "number": 6, "name": "Materials Around Us", "prefix": "MAT6", "domain": "Chemistry & Material Properties", "pages": 20, "class_level": 6, "subject": "Science"},
                {"id": "CH07_TMP6", "number": 7, "name": "Temperature and its Measurement", "prefix": "TMP6", "domain": "Thermodynamics", "pages": 16, "class_level": 6, "subject": "Science"},
                {"id": "CH08_WTR6", "number": 8, "name": "A Journey through States of Water", "prefix": "WTR6", "domain": "Physical Chemistry", "pages": 18, "class_level": 6, "subject": "Science"},
                {"id": "CH09_SEP6", "number": 9, "name": "Methods of Separation in Everyday Life", "prefix": "SEP6", "domain": "Separation Sciences", "pages": 20, "class_level": 6, "subject": "Science"},
                {"id": "CH10_LIV6", "number": 10, "name": "Living Creatures: Exploring their Characteristics", "prefix": "LIV6", "domain": "Zoology & Ecology", "pages": 22, "class_level": 6, "subject": "Science"},
                {"id": "CH11_NAT6", "number": 11, "name": "Nature's Treasures", "prefix": "NAT6", "domain": "Environmental Science", "pages": 18, "class_level": 6, "subject": "Science"},
                {"id": "CH12_AST6", "number": 12, "name": "Beyond Earth", "prefix": "AST6", "domain": "Astronomy & Space Science", "pages": 20, "class_level": 6, "subject": "Science"},
            ]
            for ach in additional_chapters:
                if not db.query(ChapterDB).filter_by(id=ach["id"]).first():
                    ch_obj = ChapterDB(**ach)
                    db.add(ch_obj)
                    # Starter concept
                    cid = f"{ach['prefix']}-01"
                    if not db.query(CurriculumRecordDB).filter_by(id=cid).first():
                        db.add(CurriculumRecordDB(
                            id=cid,
                            record_type="concept",
                            chapter_id=ach["id"],
                            prefix=ach["prefix"],
                            name=f"Introduction to {ach['name']}",
                            description=f"Core conceptual foundations and NCERT competency definitions for {ach['name']} (Class {ach['class_level']} {ach['subject']}).",
                            domain=ach["domain"],
                            class_level=ach["class_level"],
                            subject=ach["subject"],
                            status="verified",
                            verified_by="NCERT Curriculum Framework"
                        ))
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
