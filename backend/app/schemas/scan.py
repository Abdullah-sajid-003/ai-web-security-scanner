import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.scan import ScanStatus
from app.models.vulnerability import Severity


class ScanResponse(BaseModel):
    id: uuid.UUID
    target_id: uuid.UUID
    status: ScanStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VulnerabilityResponse(BaseModel):
    id: uuid.UUID
    title: str
    severity: Severity
    affected_endpoint: Optional[str] = None
    description: Optional[str] = None
    source_tool: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScanDetailResponse(ScanResponse):
    vulnerabilities: List[VulnerabilityResponse] = []
