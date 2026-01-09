from typing import List, Optional
from sqlalchemy import select, text
from app.models.domain import KnowledgeItem
from app.core.llm import get_text_embedding
from app.repositories.dictionary import DictionaryRepository # Maybe useful later?

class KnowledgeRetriever:
    def __init__(self, session):
        self.session = session

    async def search(self, query: str, limit: int = 5, source_type: Optional[str] = None) -> List[KnowledgeItem]:
        """
        Semantic search in the Knowledge Base.
        """
        # 1. Embed the query
        query_vector = await get_text_embedding(query)
        if not query_vector:
            print("Failed to embed query.")
            return []

        # 2. Build SQL Query (Cosine Similarity)
        stmt = select(KnowledgeItem).order_by(
            KnowledgeItem.embedding.cosine_distance(query_vector)
        ).limit(limit)
        
        if source_type:
            stmt = stmt.where(KnowledgeItem.source_type == source_type)

        result = await self.session.execute(stmt)
        return result.scalars().all()
