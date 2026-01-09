import asyncio
from typing import Optional, List
from uuid import UUID
from app.services.iot import IoTService
from app.services.rag import KnowledgeRetriever
from app.repositories.dictionary import DictionaryRepository
from app.repositories.session import SessionRepository
from app.models.domain import Exercise
from app.core.llm import generate_json

class AdaptationService:
    def __init__(self, 
                 iot_service: IoTService, 
                 dictionary_repo: DictionaryRepository, 
                 retriever: KnowledgeRetriever,
                 session_repo: SessionRepository):
        self.iot_service = iot_service
        self.dict_repo = dictionary_repo
        self.retriever = retriever
        self.session_repo = session_repo
        
        self.WAIT_THRESHOLD_MINUTES = 5

    async def check_exercise_availability(self, exercise_id: UUID, user_profile: dict) -> dict:
        """
        Checks availability. If busy, asks AI for the best smart swap.
        """
        # 1. Get Exercise Details and Wait Time Concurrently? 
        # Actually better to check existence first, then wait time.
        exercise = await self.dict_repo.get_exercise_by_id(exercise_id)
        if not exercise:
            return {"status": "error", "message": "Exercise not found"}
        
        wait_time = 0
        if exercise.machine_type_id:
            wait_time = await self.iot_service.get_estimated_wait_time(exercise.machine_type_id)
            
        if wait_time <= self.WAIT_THRESHOLD_MINUTES:
            return {
                "status": "available",
                "wait_time": wait_time,
                "dataset_source": "IoT Simulator",
                "recommendation": "Keep current exercise"
            }
            
        # 3. Busy -> Smart Swap Flow
        # Use asyncio.gather to fetch candidates and user stats in parallel
        candidates_task = self._find_candidates(exercise)
        user_id = UUID(user_profile.get("id"))
        stats_task = self.session_repo.get_recent_best_set(user_id, exercise.id)
        
        candidates, stats = await asyncio.gather(candidates_task, stats_task)
        stats_str = f"Best: {stats['weight_kg']}kg x {stats['reps']} reps" if stats else "No previous history"
        
        # Filter by Availability (Parallel IoT Checks)
        available_candidates = await self._filter_available_candidates(candidates)

        if not available_candidates:
            return {
                "status": "busy",
                "wait_time": wait_time,
                "dataset_source": "IoT + RAG",
                "recommendation": "All alternatives are busy too!",
                "alternatives": []
            }

        # D. Ask LLM to Pick
        best_pick = await self._ask_llm_for_swap(
            user_profile=user_profile,
            original_exercise=exercise,
            candidates=available_candidates,
            stats_context=stats_str
        )
        
        if best_pick.get("id"):
            # Format to match AlternativeExercise schema
            formatted_pick = {
                "type": "ai_recommendation",
                "exercise": best_pick["name"],
                "id": str(best_pick["id"]),
                "wait_time": best_pick.get("wait_time", 0),
                "reason": best_pick.get("reason", "Best match")
            }
            return {
                "status": "busy",
                "wait_time": wait_time,
                "dataset_source": "Gemini AI + IoT",
                "recommendation": best_pick.get("reason", "Swap advised"),
                "alternatives": [formatted_pick]
            }
        
        return {
            "status": "busy",
            "wait_time": wait_time,
            "dataset_source": "Gemini AI + IoT",
            "recommendation": "No suitable alternatives found.",
            "alternatives": []
        }

    async def _find_candidates(self, original_exercise: Exercise) -> List[dict]:
        """
        Unfiltered list of potential swaps. Parallelizes DB and RAG fetch.
        """
        async def fetch_db_alts():
            db_res = []
            if original_exercise.alternatives:
                for alt_id in original_exercise.alternatives:
                    alt_ex = await self.dict_repo.get_exercise_by_id(alt_id)
                    if alt_ex:
                        db_res.append({"name": alt_ex.name, "id": str(alt_ex.id), "source": "DB"})
            return db_res

        async def fetch_rag_alts():
            rag_res = []
            query = f"Alternative to {original_exercise.name} targeting {original_exercise.muscle_group}"
            rag_hits = await self.retriever.search(query, limit=3, source_type="exercise")
            for hit in rag_hits:
                if str(hit.source_id) == str(original_exercise.id): continue
                rag_res.append({
                    "name": hit.metadata_info.get("name"), 
                    "id": str(hit.source_id), 
                    "source": "RAG"
                })
            return rag_res

        db_alts, rag_alts = await asyncio.gather(fetch_db_alts(), fetch_rag_alts())
        # Dedup by ID (prefer DB)
        seen_ids = set()
        unique_results = []
        for c in db_alts + rag_alts:
            if c["id"] not in seen_ids:
                seen_ids.add(c["id"])
                unique_results.append(c)
        return unique_results

    async def _filter_available_candidates(self, candidates: List[dict]) -> List[dict]:
        """
        Check IoT availability for all candidates in parallel.
        """
        async def check_one(cand):
            cw = 0
            if cand.get("id"):
                c_ex = await self.dict_repo.get_exercise_by_id(UUID(cand["id"]))
                if c_ex and c_ex.machine_type_id:
                    cw = await self.iot_service.get_estimated_wait_time(c_ex.machine_type_id)
            cand["wait_time"] = cw
            return cand if cw <= self.WAIT_THRESHOLD_MINUTES else None

        results = await asyncio.gather(*[check_one(c) for c in candidates])
        return [r for r in results if r is not None]

    async def _ask_llm_for_swap(self, user_profile: dict, original_exercise: Exercise, candidates: List[dict], stats_context: str) -> dict:
        """
        Uses Gemini to select the best option.
        """
        prompt = f"""
        Act as an expert gym coach.
        The user wants to do '{original_exercise.name}' ({original_exercise.muscle_group}) but the machine is BUSY.
        
        User Profile:
        - Level: {user_profile.get('onboarding_data', {}).get('experience_level', 'Intermediate')}
        - Goal: {user_profile.get('onboarding_data', {}).get('goal', 'General Fitness')}
        - History on '{original_exercise.name}': {stats_context}
        
        Available Alternatives (I have checked these are free):
        {[c['name'] for c in candidates]}
        
        Task:
        Select the SINGLE BEST alternative from the list above that matches the user's level and goal.
        Explain WHY in 1 short sentence (e.g. "Good compound movement match" or "Better for hypertrophy").
        
        Output JSON:
        {{
            "name": "Exact Name from list",
            "reason": "Explanation..."
        }}
        """
        
        response = await generate_json(prompt)
        
        # Match back to candidate object to get ID
        chosen_name = response.get("name", "")
        for cand in candidates:
             if cand["name"] == chosen_name:
                 cand["reason"] = response.get("reason", "AI Selected")
                 return cand
        
        # Fallback: Just return first available
        if candidates:
            candidates[0]["reason"] = "AI Fallback"
            return candidates[0]
            
        return {"name": "No Swap Found", "id": None, "reason": "None"}
