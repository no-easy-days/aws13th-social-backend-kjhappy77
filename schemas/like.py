from pydantic import BaseModel
from datetime import datetime

class LikeCreate(BaseModel):
    post_id: int

class LikeResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime

class LikeStatus(BaseModel):
    is_liked: bool
    total_likes: int