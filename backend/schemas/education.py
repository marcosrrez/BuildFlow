from pydantic import BaseModel
from typing import List

class KnowledgeEntryRead(BaseModel):
    id: str
    title: str
    short_description: str
    full_description: str
    pros: list[str]
    cons: list[str]
    risks: list[str]
    related_terms: list[str]
