from datetime import datetime
from pydantic import BaseModel


class DocumentCategoryBase(BaseModel):
    name: str
    parent_id: int | None = None
    sort_order: int = 0


class DocumentCategoryCreate(DocumentCategoryBase):
    pass


class DocumentCategoryRead(DocumentCategoryBase):
    id: int
    project_id: int
    model_config = {"from_attributes": True}


class DocumentBase(BaseModel):
    name: str
    category_id: int | None = None
    description: str | None = None
    tags: str | None = None


class DocumentCreate(DocumentBase):
    pass


class DocumentRead(DocumentBase):
    id: int
    project_id: int
    file_path: str
    file_type: str | None = None
    file_size: int | None = None
    version: int = 1
    uploaded_by: str | None = None
    created_at: datetime
    model_config = {"from_attributes": True}
