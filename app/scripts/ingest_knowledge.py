import asyncio
import os
import sys
import glob

# Add project root to sys.path
sys.path.append(os.getcwd())

from sqlalchemy import select, delete
from app.core.user_db import async_session_factory
from app.models.domain import Exercise, KnowledgeItem
from app.core.config import settings

import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
EMBEDDING_MODEL = "models/text-embedding-004"

ASSETS_DIR = "assets/Documentation pour développement"

async def get_embedding(text: str):
    try:
        result = await asyncio.to_thread(
            genai.embed_content,
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"Error embedding text '{text[:50]}...': {e}")
        return None

async def ingest_exercises(session):
    print("--- 1. Ingesting Exercises ---")
    stmt = select(Exercise)
    result = await session.execute(stmt)
    exercises = result.scalars().all()
    
    count = 0
    BATCH_SIZE = 15
    total_ex = len(exercises)
    
    print(f"Total exercises to ingest: {total_ex}")
    
    # Prepare all items first (descriptions)
    ex_items = []
    for ex in exercises:
        desc = f"Exercise: {ex.name}. Muscle: {ex.muscle_group}. Description: {ex.description or ''}"
        ex_items.append((ex, desc))
        
    for i in range(0, total_ex, BATCH_SIZE):
        batch = ex_items[i:i+BATCH_SIZE]
        print(f"  Embedding exercises batch {i//BATCH_SIZE + 1}/{(total_ex + BATCH_SIZE - 1)//BATCH_SIZE}...")
        
        # Parallel calls
        tasks = [get_embedding(desc) for _, desc in batch]
        embeddings = await asyncio.gather(*tasks)
        
        for (ex, desc), embedding in zip(batch, embeddings):
            if embedding:
                item = KnowledgeItem(
                    source_type="exercise",
                    source_id=ex.id,
                    content_text=desc,
                    embedding=embedding,
                    metadata_info={"name": ex.name, "muscle": ex.muscle_group}
                )
                session.add(item)
                count += 1
        
        await session.commit()
    
    print(f"✅ Ingested {count} exercises.")

async def ingest_documents(session):
    print("--- 2. Ingesting Documentation ---")
    # Recursive search for markdown files
    files = glob.glob(os.path.join(ASSETS_DIR, "**/*.md"), recursive=True)
    
    
    count = 0
    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"Processing {filename}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Context-Aware Chunking via Headers
        # We split by headers but keep context in the text
        lines = content.split('\n')
        
        current_h1 = ""
        current_h2 = ""
        current_chunk_lines = []
        
        def flush_chunk():
            nonlocal count
            text = "\n".join(current_chunk_lines).strip()
            if len(text) > 30: # Min size filter
                # Prepend context
                context_str = f"Document: {filename}\n"
                if current_h1: context_str += f"Section: {current_h1}\n"
                if current_h2: context_str += f"Subsection: {current_h2}\n"
                
                full_text = context_str + "Content: " + text
                
                # Async call inside loop - technically slow but okay for script
                # Ideally we gather tasks
                # embedding = await get_embedding(full_text) # Done later in batch or just await here
                
                return (full_text, {"filename": filename, "h1": current_h1, "h2": current_h2})
            return None

        items_to_embed = []
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('# '):
                # New H1
                if current_chunk_lines:
                    if c := flush_chunk(): items_to_embed.append(c)
                    current_chunk_lines = []
                current_h1 = line_stripped[2:]
                current_h2 = "" # Reset H2
            elif line_stripped.startswith('## '):
                # New H2
                if current_chunk_lines:
                    if c := flush_chunk(): items_to_embed.append(c)
                    current_chunk_lines = []
                current_h2 = line_stripped[3:]
            elif line_stripped.startswith('### '):
                 # Treat H3 as just text or new chunk? Let's just create a new chunk for granularity
                 if current_chunk_lines:
                    if c := flush_chunk(): items_to_embed.append(c)
                    current_chunk_lines = []
                 current_chunk_lines.append(line)
            else:
                current_chunk_lines.append(line)
        
        # Flush last
        if current_chunk_lines:
             if c := flush_chunk(): items_to_embed.append(c)
             
        # Optimized Batch Processing
        BATCH_SIZE = 10
        total_items = len(items_to_embed)
        
        for i in range(0, total_items, BATCH_SIZE):
            batch = items_to_embed[i:i+BATCH_SIZE]
            print(f"  Embedding batch {i//BATCH_SIZE + 1}/{(total_items + BATCH_SIZE - 1)//BATCH_SIZE}...")
            
            tasks = [get_embedding(text) for text, _ in batch]
            embeddings = await asyncio.gather(*tasks)
            
            for (text, meta), embedding in zip(batch, embeddings):
                if embedding:
                    item = KnowledgeItem(
                        source_type="doc_chunk",
                        content_text=text,
                        embedding=embedding,
                        metadata_info=meta
                    )
                    session.add(item)
                    count += 1
            
            # Commit after each file to save progress
            await session.commit()
            
    print(f"✅ Ingested {count} doc chunks.")

async def clear_knowledge(session):
    print("🧹 Clearing existing knowledge items...")
    await session.execute(delete(KnowledgeItem))
    await session.commit()

async def main():
    async with async_session_factory() as session:
        await clear_knowledge(session)
        await ingest_exercises(session)
        await ingest_documents(session)

if __name__ == "__main__":
    asyncio.run(main())
