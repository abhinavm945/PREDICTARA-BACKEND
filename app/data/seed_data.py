from typing import Dict, List
from app.models.schemas import Concept, Question, QuestionOption, ErrorCategory, LearningDeliveryModule, WorkedExample

# Class 6 Mathematics Knowledge Graph (PRD Section 3.1 & 4)
CONCEPTS_DB: Dict[str, Concept] = {
    "basic_fractions": Concept(
        id="basic_fractions",
        code="MATH_G6_FRAC_BASICS",
        name="Understanding Fractions & Representation",
        grade_level=6,
        subject="Mathematics",
        domain="Fractions & Decimals",
        description="Identifying numerators, denominators, proper/improper fractions, and visual representations.",
        prerequisites=[],
        downstream_impact=["equivalent_fractions", "fraction_addition"],
        mastery_threshold=0.70
    ),
    "equivalent_fractions": Concept(
        id="equivalent_fractions",
        code="MATH_G6_FRAC_EQUIV",
        name="Equivalent Fractions & Simplification",
        grade_level=6,
        subject="Mathematics",
        domain="Fractions & Decimals",
        description="Scaling numerators and denominators by common factors and reduction to lowest terms.",
        prerequisites=["basic_fractions"],
        downstream_impact=["fraction_addition", "fraction_multiplication"],
        mastery_threshold=0.75
    ),
    "fraction_addition": Concept(
        id="fraction_addition",
        code="MATH_G6_FRAC_UNLIKE_ADD",
        name="Adding & Subtracting Unlike Fractions",
        grade_level=6,
        subject="Mathematics",
        domain="Fractions & Decimals",
        description="Computing Least Common Multiple (LCM) of denominators to add/subtract fractions.",
        prerequisites=["equivalent_fractions"],
        downstream_impact=["fraction_multiplication", "word_problems_fractions"],
        mastery_threshold=0.75
    ),
    "fraction_multiplication": Concept(
        id="fraction_multiplication",
        code="MATH_G6_FRAC_MULT",
        name="Multiplying Fractions & Reciprocals",
        grade_level=6,
        subject="Mathematics",
        domain="Fractions & Decimals",
        description="Direct multiplication of numerators and denominators, finding reciprocals for division.",
        prerequisites=["fraction_addition", "equivalent_fractions"],
        downstream_impact=["word_problems_fractions", "algebra_linear_equations"],
        mastery_threshold=0.80
    ),
    "word_problems_fractions": Concept(
        id="word_problems_fractions",
        code="MATH_G6_FRAC_APPLIED",
        name="Applied Multi-Step Fraction Word Problems",
        grade_level=6,
        subject="Mathematics",
        domain="Applied Problem Solving",
        description="Translating real-world word problems into fractional arithmetic operations.",
        prerequisites=["fraction_addition", "fraction_multiplication"],
        downstream_impact=["algebra_linear_equations"],
        mastery_threshold=0.80
    ),
}

# Questions with Engineered Distractors and Error Taxonomies
QUESTIONS_DB: Dict[str, Question] = {
    "q1": Question(
        id="q1",
        concept_id="basic_fractions",
        concept_name="Understanding Fractions & Representation",
        title="Question 1: Visual Fractional Share",
        prompt="A pizza is sliced into 8 equal slices. Alex eats 3 slices. What fraction of the pizza remains?",
        options=[
            QuestionOption(id="q1_a", key="A", text="3 / 8", is_correct=False, error_category=ErrorCategory.MISCONCEPTION_REPRESENTATION, error_code="ERR_CONFUSED_EATEN_WITH_REMAINING", rationale="Selected the fraction eaten rather than remaining."),
            QuestionOption(id="q1_b", key="B", text="5 / 8", is_correct=True, rationale="Correct: 8 - 3 = 5 slices remain out of 8."),
            QuestionOption(id="q1_c", key="C", text="8 / 3", is_correct=False, error_category=ErrorCategory.MISCONCEPTION_REPRESENTATION, error_code="ERR_INVERTED_NUM_DENOM", rationale="Inverted the numerator and denominator."),
            QuestionOption(id="q1_d", key="D", text="5 / 3", is_correct=False, error_category=ErrorCategory.CALCULATION_ARITHMETIC, error_code="ERR_ARITHMETIC_DENOMINATOR_SLIP", rationale="Used remaining slices as numerator and eaten slices as denominator.")
        ],
        difficulty="easy",
        benchmark_seconds=60,
        solution_steps=["Whole pizza has 8 slices.", "Alex ate 3 slices, so remaining is 8 - 3 = 5.", "Remaining fraction = 5 / 8."]
    ),
    "q2": Question(
        id="q2",
        concept_id="equivalent_fractions",
        concept_name="Equivalent Fractions & Simplification",
        title="Question 2: Simplifying Fractions to Lowest Terms",
        prompt="Which fraction is equivalent to 12 / 16 in its simplest form?",
        options=[
            QuestionOption(id="q2_a", key="A", text="6 / 8", is_correct=False, error_category=ErrorCategory.PREREQUISITE_CONCEPT_GAP, error_code="ERR_INCOMPLETE_SIMPLIFICATION", rationale="Divided by 2 once, but did not reduce to lowest terms (GCF is 4)."),
            QuestionOption(id="q2_b", key="B", text="3 / 4", is_correct=True, rationale="Correct: Dividing both 12 and 16 by 4 gives 3/4."),
            QuestionOption(id="q2_c", key="C", text="2 / 3", is_correct=False, error_category=ErrorCategory.CALCULATION_ARITHMETIC, error_code="ERR_ARITHMETIC_DIVISION", rationale="Arithmetic miscalculation during simplification."),
            QuestionOption(id="q2_d", key="D", text="4 / 5", is_correct=False, error_category=ErrorCategory.IMPULSIVE_GUESS, error_code="ERR_RANDOM_HEURISTIC", rationale="Selected adjacent ratio without factor factorization.")
        ],
        difficulty="easy",
        benchmark_seconds=75,
        solution_steps=["Find GCF of 12 and 16: Factors of 12 (1,2,3,4,6,12), Factors of 16 (1,2,4,8,16). GCF = 4.", "12 / 4 = 3, 16 / 4 = 4.", "Simplest form is 3 / 4."]
    ),
    "q3": Question(
        id="q3",
        concept_id="equivalent_fractions",
        concept_name="Equivalent Fractions & Simplification",
        title="Question 3: Missing Numerator Equivalence",
        prompt="Find the missing numerator: 2 / 5 = ? / 20",
        options=[
            QuestionOption(id="q3_a", key="A", text="8", is_correct=True, rationale="Correct: 20 ÷ 5 = 4 multiplier; 2 × 4 = 8."),
            QuestionOption(id="q3_b", key="B", text="4", is_correct=False, error_category=ErrorCategory.FORMULA_CONFUSION, error_code="ERR_MULTIPLIER_CONFUSION", rationale="Wrote down the scale factor (4) instead of multiplying the numerator."),
            QuestionOption(id="q3_c", key="C", text="10", is_correct=False, error_category=ErrorCategory.CALCULATION_ARITHMETIC, error_code="ERR_ADDITION_INSTEAD_OF_MULTIPLICATION", rationale="Added 5 instead of scaling multiplicatively."),
            QuestionOption(id="q3_d", key="D", text="12", is_correct=False, error_category=ErrorCategory.IMPULSIVE_GUESS, error_code="ERR_UNFOUNDED_ESTIMATION", rationale="Arithmetic slip or guessing.")
        ],
        difficulty="medium",
        benchmark_seconds=90,
        solution_steps=["Compare denominators: 20 / 5 = 4.", "Multiply numerator by the same factor: 2 × 4 = 8.", "Result = 8."]
    ),
    "q4": Question(
        id="q4",
        concept_id="fraction_addition",
        concept_name="Adding & Subtracting Unlike Fractions",
        title="Question 4: Unlike Denominator Addition",
        prompt="What is the sum: 1 / 4 + 2 / 3 ?",
        options=[
            QuestionOption(id="q4_a", key="A", text="3 / 7", is_correct=False, error_category=ErrorCategory.PREREQUISITE_CONCEPT_GAP, error_code="ERR_ACROSS_THE_BOARD_ADDITION", rationale="Added numerators together (1+2=3) and denominators together (4+3=7). Classic foundational gap!"),
            QuestionOption(id="q4_b", key="B", text="11 / 12", is_correct=True, rationale="Correct: LCD is 12. 3/12 + 8/12 = 11/12."),
            QuestionOption(id="q4_c", key="C", text="3 / 12", is_correct=False, error_category=ErrorCategory.CALCULATION_ARITHMETIC, error_code="ERR_UNSCALED_NUMERATOR", rationale="Found LCD 12 but added original numerators (1+2=3)."),
            QuestionOption(id="q4_d", key="D", text="8 / 12", is_correct=False, error_category=ErrorCategory.FORMULA_CONFUSION, error_code="ERR_DROPPED_FIRST_TERM", rationale="Converted 2/3 to 8/12 but neglected adding 1/4.")
        ],
        difficulty="medium",
        benchmark_seconds=120,
        solution_steps=["Find LCD of 4 and 3: LCM(4, 3) = 12.", "Convert 1/4: 1/4 × (3/3) = 3/12.", "Convert 2/3: 2/3 × (4/4) = 8/12.", "Add: 3/12 + 8/12 = 11/12."]
    ),
    "q5": Question(
        id="q5",
        concept_id="fraction_addition",
        concept_name="Adding & Subtracting Unlike Fractions",
        title="Question 5: Unlike Denominator Subtraction",
        prompt="Calculate: 5 / 6 - 1 / 3",
        options=[
            QuestionOption(id="q5_a", key="A", text="4 / 3", is_correct=False, error_category=ErrorCategory.PREREQUISITE_CONCEPT_GAP, error_code="ERR_DIRECT_SUBTRACTION_SLIP", rationale="Subtracted numerators (5-1=4) and denominators (6-3=3)."),
            QuestionOption(id="q5_b", key="B", text="1 / 2", is_correct=True, rationale="Correct: Convert 1/3 to 2/6. 5/6 - 2/6 = 3/6 = 1/2."),
            QuestionOption(id="q5_c", key="C", text="3 / 6", is_correct=False, error_category=ErrorCategory.PREREQUISITE_CONCEPT_GAP, error_code="ERR_INCOMPLETE_SIMPLIFICATION", rationale="Calculated 3/6 correctly but missed simplifying to lowest terms 1/2."),
            QuestionOption(id="q5_d", key="D", text="4 / 6", is_correct=False, error_category=ErrorCategory.CALCULATION_ARITHMETIC, error_code="ERR_ARITHMETIC_BORROW", rationale="Arithmetic miscalculation in conversion.")
        ],
        difficulty="hard",
        benchmark_seconds=120,
        solution_steps=["Common denominator between 6 and 3 is 6.", "1/3 = 2/6.", "5/6 - 2/6 = 3/6.", "Simplify 3/6 = 1/2."]
    )
}

# Delivery remediation modules mapped to concepts
LEARNING_MODULES_DB: Dict[str, LearningDeliveryModule] = {
    "equivalent_fractions": LearningDeliveryModule(
        concept_id="equivalent_fractions",
        concept_name="Equivalent Fractions & Simplification",
        micro_explanation="Equivalent fractions represent identical portions of the same whole. The Golden Rule of Fractions: You can multiply or divide the numerator and denominator by the exact same non-zero number without altering the fraction's actual value.",
        worked_examples=[
            WorkedExample(
                problem="Find the equivalent fraction with denominator 24: 3 / 8 = ? / 24",
                step_by_step=[
                    "Step 1: Determine the multiplier for the denominator: 24 ÷ 8 = 3.",
                    "Step 2: Multiply the numerator by the same multiplier 3: 3 × 3 = 9.",
                    "Step 3: Conclude that 3 / 8 = 9 / 24."
                ],
                solution="9 / 24"
            ),
            WorkedExample(
                problem="Simplify 14 / 35 into its simplest form.",
                step_by_step=[
                    "Step 1: Identify the Greatest Common Factor (GCF) of 14 and 35. Factors of 14: 1, 2, 7, 14. Factors of 35: 1, 5, 7, 35. GCF = 7.",
                    "Step 2: Divide both top and bottom by 7: 14 ÷ 7 = 2 and 35 ÷ 7 = 5.",
                    "Step 3: Result is 2 / 5."
                ],
                solution="2 / 5"
            )
        ],
        practice_questions=[
            Question(
                id="prac_eq_1",
                concept_id="equivalent_fractions",
                concept_name="Equivalent Fractions & Simplification",
                title="Practice 1: Simplification",
                prompt="Simplify 18 / 24 to lowest terms:",
                options=[
                    QuestionOption(id="pe1_a", key="A", text="3 / 4", is_correct=True, rationale="Correct: 18 ÷ 6 = 3, 24 ÷ 6 = 4."),
                    QuestionOption(id="pe1_b", key="B", text="9 / 12", is_correct=False, error_category=ErrorCategory.PREREQUISITE_CONCEPT_GAP, rationale="Not in lowest terms."),
                    QuestionOption(id="pe1_c", key="C", text="6 / 8", is_correct=False, error_category=ErrorCategory.PREREQUISITE_CONCEPT_GAP, rationale="Not in lowest terms."),
                    QuestionOption(id="pe1_d", key="D", text="2 / 3", is_correct=False, error_category=ErrorCategory.CALCULATION_ARITHMETIC, rationale="Incorrect division.")
                ]
            )
        ]
    ),
    "fraction_addition": LearningDeliveryModule(
        concept_id="fraction_addition",
        concept_name="Adding & Subtracting Unlike Fractions",
        micro_explanation="You cannot combine fractions with different denominators directly because the slice sizes differ! First convert both fractions to equivalent fractions with their Least Common Denominator (LCD), then add or subtract only the numerators.",
        worked_examples=[
            WorkedExample(
                problem="Add 2 / 5 + 1 / 2",
                step_by_step=[
                    "Step 1: The Least Common Denominator (LCD) of 5 and 2 is 10.",
                    "Step 2: Convert 2/5 to tenths: 2/5 × (2/2) = 4/10.",
                    "Step 3: Convert 1/2 to tenths: 1/2 × (5/5) = 5/10.",
                    "Step 4: Add numerators: 4/10 + 5/10 = 9/10."
                ],
                solution="9 / 10"
            )
        ],
        practice_questions=[
            Question(
                id="prac_add_1",
                concept_id="fraction_addition",
                concept_name="Adding & Subtracting Unlike Fractions",
                title="Practice 1: Unlike Denominator Addition",
                prompt="Evaluate: 1 / 3 + 1 / 6",
                options=[
                    QuestionOption(id="pa1_a", key="A", text="1 / 2", is_correct=True, rationale="Correct: 2/6 + 1/6 = 3/6 = 1/2."),
                    QuestionOption(id="pa1_b", key="B", text="2 / 9", is_correct=False, error_category=ErrorCategory.PREREQUISITE_CONCEPT_GAP, rationale="Added straight across (1+1)/(3+6)."),
                    QuestionOption(id="pa1_c", key="C", text="3 / 6", is_correct=False, error_category=ErrorCategory.PREREQUISITE_CONCEPT_GAP, rationale="Valid sum but not reduced."),
                    QuestionOption(id="pa1_d", key="D", text="2 / 6", is_correct=False, error_category=ErrorCategory.CALCULATION_ARITHMETIC, rationale="Arithmetic slip.")
                ]
            )
        ]
    )
}
