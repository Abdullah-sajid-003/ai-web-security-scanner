import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class TargetCreate(BaseModel):
    name: str
    url: str

    @field_validator("url")
    @classmethod
    def url_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        return v


class TargetResponse(BaseModel):
    id: uuid.UUID
    name: str
    url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
