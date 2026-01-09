import google.generativeai as genai
from app.core.config import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# Use a lightweight model for textualization to be fast
MODEL_NAME = "gemini-2.0-flash"
EMBEDDING_MODEL = "models/text-embedding-004"

import asyncio

async def get_text_embedding(text: str) -> list[float] | None:
    """
    Generate an embedding vector for the given text using Gemini.
    """
    try:
        result = await asyncio.to_thread(
            genai.embed_content,
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_query" # Optimized for queries
        )
        return result['embedding']
    except Exception as e:
        print(f"Embedding failed: {e}")
        return None

from app.schemas.template import ProgramTemplate

async def generate_program_narrative(template_data: ProgramTemplate, user_profile_data: dict, context_text: str = "") -> dict:
    """
    Augment the static template with personalized text utilizing the LLM.
    Returns a dictionary of overrides for names, descriptions, and notes.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    
    # Construct a prompt that asks ONLY for the textual fields
    prompt = f"""
    You are an expert fitness coach. 
    Customize the descriptions and titles of the following workout program to match the user's profile.
    
    Use the following EXPERT KNOWLEDGE BASE to inform your tone and advice:
    {context_text}
    
    User Profile:
    - Goal: {user_profile_data.get('goal')}
    - Level: {user_profile_data.get('experience_level')}
    - Stats: {user_profile_data.get('current_stats')}
    
    Program Template:
    - Name: {template_data.name_template}
    - Description: {template_data.description_template}
    - Phases: {[p.model_dump() for p in template_data.phases]}
    
    Task:
    Return a JSON object with the following keys:
    - "program_name": A motivating name for the program.
    - "program_description": A personalized description (2-3 sentences) addressing the user directly ("You will...").
    - "phase_advice": A specific advice string for the first phase.
    
    Output ONLY JSON.
    """
    
    try:
        response = await model.generate_content_async(prompt, generation_config={"response_mime_type": "application/json"})
        # Simple JSON extraction (assuming model obeys mime_type)
        import json
        return json.loads(response.text)
    except Exception as e:
        print(f"LLM Generation failed: {e}")
        # Fallback to template defaults if LLM fails
        return {
            "program_name": template_data.name_template,
            "program_description": template_data.description_template,
            "phase_advice": "Focus on form and consistency."
        }

async def generate_json(prompt: str) -> dict:
    """
    Generic helper to get JSON output from Gemini.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    try:
        response = await model.generate_content_async(prompt, generation_config={"response_mime_type": "application/json"})
        import json
        return json.loads(response.text)
    except Exception as e:
        print(f"LLM JSON Geneartion failed: {e}")
        return {}
