from uuid import UUID
from datetime import datetime
from typing import List

from fastapi import HTTPException

from app.repositories.program import ProgramRepository
from app.repositories.profile import ProfileRepository
from app.models.domain import Program, Session


from app.repositories.dictionary import DictionaryRepository
from app.services.program_generator import ProgramGenerator

class ProgramService:
    def __init__(self, 
                 program_repo: ProgramRepository, 
                 profile_repo: ProfileRepository, 
                 dictionary_repo: DictionaryRepository,
                 program_generator: ProgramGenerator):
        self.program_repo = program_repo
        self.profile_repo = profile_repo
        self.dictionary_repo = dictionary_repo
        self.program_generator = program_generator

    async def generate_program(self, user_id: UUID, method: str = "template") -> Program:
        # 1. Get User Profile
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(status_code=400, detail="User profile not found. Complete onboarding first.")

        # 2. Archive existing active program
        await self.program_repo.archive_current_programs(user_id)

        # 3. GENERATION LOGIC
        if method == "smart":
            # --- FULL AI (RAG) ---
            print("🤖 Using SMART (RAG) Generation Mode")
            
            # A. Architect Phase
            skeleton = await self.program_generator.generate_program_structure({
                "goal": profile.onboarding_data.get("goal"),
                "experience_level": profile.onboarding_data.get("experience_level"),
                "current_stats": profile.current_stats
            })
            
            # B. Librarian Phase
            sessions = await self.program_generator.realize_program(skeleton)
            
            program_name = skeleton.get("program_name", "AI Customized Program")
            
            # Create Program Object
            new_program = Program(
                user_id=user_id,
                name=program_name,
                goal=profile.onboarding_data.get("goal"),
                status="active",
                start_date=datetime.now()
            )
            
            return await self.program_repo.create_program(new_program, sessions)
            
        else:
            # --- HYBRID (TEMPLATE) ---
            print("📜 Using CLASSIC (Template) Generation Mode")
            # A. Select Template
            goal = profile.onboarding_data.get("goal", "general_fitness")
        exp_level = profile.onboarding_data.get("experience_level", "beginner")
        
        from app.services.templates import get_template
        template = get_template(goal, exp_level)
        
        # B. Get Knowledge Context
        from app.services.knowledge import KnowledgeService
        knowledge_service = KnowledgeService()
        expert_context = knowledge_service.get_construction_guidelines()
        expert_context += "\n" + knowledge_service.get_muscle_group_info([])
        
        # C. LLM Enrichment (Textualization)
        from app.core.llm import generate_program_narrative
        narrative = await generate_program_narrative(template, {
            "goal": goal,
            "experience_level": exp_level,
            "current_stats": profile.current_stats
        }, context_text=expert_context)

        # D. Construct Objects
        program_name = narrative.get("program_name", template.name_template)
        
        # Create Program Object
        new_program = Program(
            user_id=user_id,
            name=program_name,
            goal=goal,
            status="active",
            start_date=datetime.now()
        )

        # Create Sessions from Template
        sessions = []
        for i, sess_tmpl in enumerate(template.sessions):
            exercises_plan = []
            for ex in sess_tmpl.exercises:
                exercise_obj = await self.dictionary_repo.get_exercise_by_name(ex.default_exercise)
                exercise_id = exercise_obj.id if exercise_obj else None
                
                exercises_plan.append({
                    "exercise_id": str(exercise_id) if exercise_id else None,
                    "exercise_name": ex.default_exercise,
                    "target_sets": ex.sets,
                    "target_reps": ex.reps,
                    "rest_seconds": ex.rest,
                    "notes": ex.notes
                })

            s = Session(
                name=sess_tmpl.name_template,
                order_index=i + 1,
                exercises_plan=exercises_plan
            )
            sessions.append(s)

        created_program = await self.program_repo.create_program(new_program, sessions)
        return created_program
    
    async def get_current_program(self, user_id: UUID) -> Program:
        program = await self.program_repo.get_active_program(user_id)
        if not program:
            raise HTTPException(status_code=404, detail="No active program found.")
        return program
