from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

class CommentResponse(CommentBase):
    id: int
    post_id: int
    user_id: int
    author_nickname: str
    created_at: datetime
    updated_at: datetime