from typing import Dict
from app.schemas.template import ProgramTemplate, PhaseTemplate, SessionTemplate, ExerciseTemplate


MUSCLE_GAIN_BEGINNER = ProgramTemplate(
    name_template="Fondations Hypertrophie",
    description_template="Un programme complet pour initier la prise de masse musculaire en travaillant tout le corps à chaque séance.",
    goal="muscle_gain",
    level="beginner",
    phases=[
        PhaseTemplate(
            name="Adaptation Anatomique",
            weeks=4,
            focus="Endurance de force & Technique",
            progression="Augmenter les répétitions avant d'augmenter la charge sur les semaines 1-4."
        )
    ],
    default_days_per_week=3,
    sessions=[
        SessionTemplate(
            name_template="Full Body A",
            description_template="Séance global mettant l'accent sur les mouvements de poussée.",
            duration_minutes=60,
            exercises=[
                ExerciseTemplate(
                    muscle_group="quadriceps", pattern="Squat", default_exercise="Dumbbell Goblet Squat",
                    sets=3, reps=12, rest=90, rpe_target=7, notes="Gardez le dos droit et descendez aussi bas que possible."
                ),
                ExerciseTemplate(
                    muscle_group="pectoraux", pattern="Push Horizontal", default_exercise="Bodyweight Kneeling Push Up",
                    sets=3, reps=10, rest=90, rpe_target=8, notes="Corps gainé, coudes à 45 degrés."
                ),
                ExerciseTemplate(
                    muscle_group="dos", pattern="Pull Vertical", default_exercise="Cable Wide Grip Lat Pulldown",
                    sets=3, reps=12, rest=90, rpe_target=7, notes="Tirez vers le haut de la poitrine, pas derrière la nuque."
                ),
                ExerciseTemplate(
                    muscle_group="abdominaux", pattern="Core", default_exercise="Bodyweight Kneeling Plank",
                    sets=3, reps=0, duration=45, rest=60, rpe_target=8, notes="Contractez fort les fessiers et les abdos."
                )
            ]
        ),
        SessionTemplate(
            name_template="Full Body B",
            description_template="Séance global mettant l'accent sur les mouvements de tirage.",
            duration_minutes=60,
            exercises=[
                ExerciseTemplate(
                    muscle_group="ischio-jambiers", pattern="Hinge", default_exercise="Barbell Romanian Deadlift",
                    sets=3, reps=12, rest=90, rpe_target=7, notes="Poussez les hanches vers l'arrière, gardez le dos plat."
                ),
                ExerciseTemplate(
                    muscle_group="épaules", pattern="Push Vertical", default_exercise="Double Dumbbell Overhead Press",
                    sets=3, reps=10, rest=90, rpe_target=8, notes="Ne cambrez pas le dos excessivement."
                ),
                ExerciseTemplate(
                    muscle_group="dos", pattern="Pull Horizontal", default_exercise="Double Dumbbell Prone Row",
                    sets=3, reps=12, rest=90, rpe_target=7, notes="Tirez les haltères vers les hanches."
                ),
                ExerciseTemplate(
                    muscle_group="fessiers", pattern="Lunge", default_exercise="Bodyweight Walking Lunge",
                    sets=3, reps=12, rest=90, rpe_target=7, notes="Genou arrière frôle le sol."
                )
            ]
        )
    ]
)

PROGRAM_TEMPLATES: Dict[str, ProgramTemplate] = {
    "muscle_gain_beginner": MUSCLE_GAIN_BEGINNER
}

def get_template(goal: str, level: str) -> ProgramTemplate:
    key = f"{goal}_{level}"
    return PROGRAM_TEMPLATES.get(key, PROGRAM_TEMPLATES["muscle_gain_beginner"])
