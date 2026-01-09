import asyncio
import csv
import sys
import os

# Add the project root to sys.path to allow imports
sys.path.append(os.getcwd())

from sqlalchemy import select, delete
from app.core.user_db import async_session_factory
from app.models.domain import Machine, Exercise

CSV_PATH = "assets/Documentation pour développement/Dataset Exercices (à cleaner)/exercices_autorises.csv"

def slugify(text: str) -> str:
    return text.strip().upper().replace(" ", "_").replace("-", "_")

async def seed_data():
    async with async_session_factory() as session:
        print("Starting seed process...")
        
        # Check if CSV exists
        if not os.path.exists(CSV_PATH):
            print(f"Error: CSV file not found at {CSV_PATH}")
            return

        # Read CSV
        exercises_to_create = []
        machines_map = {} # name -> machine_type_id

        with open(CSV_PATH, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # 1. Collect Machine Types
                material = row['materiel'].strip()
                if material:
                    machines_map[material] = slugify(material)

                # 2. Collect Exercises
                exercises_to_create.append({
                    "name": row['exercice'].strip(),
                    "muscle_group": row['groupe_musculaire'].strip(),
                    "machine_type_id": slugify(material) if material else None
                })
        
        print(f"Found {len(machines_map)} unique machines and {len(exercises_to_create)} exercises.")

        # --- Upsert Machines ---
        existing_machines = await session.execute(select(Machine))
        existing_machine_ids = {m.machine_type_id for m in existing_machines.scalars().all()}
        
        new_machines = []
        for name, m_id in machines_map.items():
            if m_id not in existing_machine_ids:
                new_machines.append(Machine(name=name, machine_type_id=m_id))
        
        if new_machines:
            session.add_all(new_machines)
            await session.commit()
            print(f"Inserted {len(new_machines)} new machines.")
        else:
            print("No new machines to insert.")

        # --- Upsert Exercises ---
        # For simplicity in this seed, we might skip existing checks based on name to avoid slow lookups 
        # or just delete all and recreate? -> Safer to check existence or use upsert if needed.
        # Given it's a "seed", let's check by name.
        
        existing_exercises = await session.execute(select(Exercise))
        existing_exercise_names = {e.name for e in existing_exercises.scalars().all()}
        
        new_exercises_objects = []
        for ex_data in exercises_to_create:
            if ex_data["name"] not in existing_exercise_names:
                new_exercises_objects.append(Exercise(
                    name=ex_data["name"],
                    muscle_group=ex_data["muscle_group"],
                    machine_type_id=ex_data["machine_type_id"]
                ))
        
        if new_exercises_objects:
            session.add_all(new_exercises_objects)
            await session.commit()
            print(f"Inserted {len(new_exercises_objects)} new exercises.")
        else:
            print("No new exercises to insert.")

        print("Seed completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
