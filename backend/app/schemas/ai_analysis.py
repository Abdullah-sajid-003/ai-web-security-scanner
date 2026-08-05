import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AIAnalysisResponse(BaseModel):
    id: uuid.UUID
    vulnerability_id: uuid.UUID
    plain_english_explanation: Optional[str] = None
    remediation_steps: Optional[str] = None
    risk_context: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
