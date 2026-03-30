from pydantic import BaseModel, Field
from datetime import datetime

class JobNoteCreate(BaseModel):
    content: str = Field(..., min_length=1)

class JobNoteUpdate(BaseModel):
    content: str = Field(..., min_length=1)

class JobNoteResponse(BaseModel):
    id: str
    job_id: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
