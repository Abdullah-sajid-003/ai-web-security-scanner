import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class AIAnalysis(Base):
    __tablename__ = "ai_analyses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vulnerability_id = Column(UUID(as_uuid=True), ForeignKey("vulnerabilities.id"), nullable=False, unique=True)
    plain_english_explanation = Column(Text, nullable=True)
    remediation_steps = Column(Text, nullable=True)
    risk_context = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    vulnerability = relationship("Vulnerability", back_populates="ai_analysis")
