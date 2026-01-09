from uuid import UUID
import json
from datetime import datetime

from app.models.domain import Program, Session
from app.services.knowledge import KnowledgeService
from app.services.rag import KnowledgeRetriever
from app.core.llm import generate_json
from app.schemas.profile import PhysicsStats

class ProgramGenerator:
    """
    Service responsible for the 'Smart' generation of workout programs.
    
    Implements the 'Architect & Librarian' pattern:
    1. Architect (LLM): Designs the high-level skeleton and semantic queries.
    2. Librarian (RAG): Resolves queries to concrete Database Entities.
    """
    def __init__(self, knowledge_service: KnowledgeService, retriever: KnowledgeRetriever):
        self.knowledge_service = knowledge_service
        self.retriever = retriever

    async def generate_program_structure(self, profile_data: dict) -> dict:
        """
        Step 1: The Architect.
        Generates the skeleton of the program based on profile and guidelines.
        """
        # 1. Fetch Context
        guidelines = self.knowledge_service.get_construction_guidelines()
        
        # 2. Build Prompt
        prompt = f"""
        You are an expert Strength & Conditioning Coach.
        Your task is to design a complete workout program for a specific user.
        
        ### USER PROFILE
        - Goal: {profile_data.get('goal')}
        - Experience: {profile_data.get('experience_level')}
        - Stats: {profile_data.get('current_stats')}
        - Valid Equipment: Gym (All machines allowed)
        
        ### EXPERT GUIDELINES (Use these rules!)
        {guidelines[:3000]}... (truncated for context window efficiency)
        
        ### INSTRUCTIONS
        Create a JSON structure representation of the program.
        For each exercise, do NOT invent a name. Instead, provide a 'search_query' that describes the biomechanical movement perfectly so a librarian can find it (e.g., "Compound Leg Exercise Quad Focus").
        
        Structure required:
        {{
            "program_name": "Name of program",
            "goal": "...",
            "description": "...",
            "sessions": [
                {{
                    "name": "Session 1: ...",
                    "description": "...",
                    "exercises": [
                        {{
                            "search_query": "Semantic query to find the best exercise",
                            "muscle_target": "Target muscle",
                            "sets": 3,
                            "reps": "8-12",
                            "rest": 90,
                            "notes": "Technique cues"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        return await generate_json(prompt)

    async def realize_program(self, skeleton: dict) -> list[Session]:
        """
        Step 2: The Librarian.
        Converts the skeleton queries into real DB Session objects with linked Exercise IDs.
        """
        sessions = []
        
        for i, session_plan in enumerate(skeleton.get("sessions", [])):
            exercises_plan = []
            
            for ex_plan in session_plan.get("exercises", []):
                query = ex_plan.get("search_query")
                
                # RAG Search
                candidates = await self.retriever.search(query, limit=1, source_type="exercise")
                
                exercise_id = None
                exercise_name = query # Fallback if not found
                
                if candidates:
                    best_match = candidates[0]
                    exercise_id = str(best_match.source_id)
                    exercise_name = best_match.metadata_info.get("name", query)
                    # print(f"Mapped '{query}' -> '{exercise_name}'")
                
                exercises_plan.append({
                    "exercise_id": exercise_id,
                    "exercise_name": exercise_name,
                    "target_sets": ex_plan.get("sets"),
                    "target_reps": ex_plan.get("reps"),
                    "rest_seconds": ex_plan.get("rest"),
                    "notes": ex_plan.get("notes")
                })
                
            sessions.append(Session(
                name=session_plan.get("name"),
                order_index=i+1,
                exercises_plan=exercises_plan
            ))
            
        return sessions
