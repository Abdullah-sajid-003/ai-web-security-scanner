import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.ai_analysis import AIAnalysis
from app.models.scan import Scan
from app.models.target import Target
from app.models.user import User
from app.models.vulnerability import Vulnerability
from app.schemas.ai_analysis import AIAnalysisResponse
from app.services.ai_analysis import AIAnalysisError, generate_analysis

router = APIRouter()


def _get_owned_vulnerability(vuln_id: uuid.UUID, db: Session, current_user: User) -> Vulnerability:
    vuln = (
        db.query(Vulnerability)
        .join(Scan, Vulnerability.scan_id == Scan.id)
        .join(Target, Scan.target_id == Target.id)
        .filter(Vulnerability.id == vuln_id, Target.owner_id == current_user.id)
        .first()
    )
    if not vuln:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vulnerability not found")
    return vuln


@router.post("/vulnerabilities/{vuln_id}/analyze", response_model=AIAnalysisResponse)
def analyze_vulnerability(
    vuln_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vuln = _get_owned_vulnerability(vuln_id, db, current_user)

    try:
        result = generate_analysis(vuln)
    except AIAnalysisError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    existing = db.query(AIAnalysis).filter(AIAnalysis.vulnerability_id == vuln.id).first()
    if existing:
        existing.plain_english_explanation = result["plain_english_explanation"]
        existing.remediation_steps = result["remediation_steps"]
        existing.risk_context = result["risk_context"]
        analysis = existing
    else:
        analysis = AIAnalysis(vulnerability_id=vuln.id, **result)
        db.add(analysis)

    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/vulnerabilities/{vuln_id}/analysis", response_model=AIAnalysisResponse)
def get_analysis(
    vuln_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vuln = _get_owned_vulnerability(vuln_id, db, current_user)
    analysis = db.query(AIAnalysis).filter(AIAnalysis.vulnerability_id == vuln.id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No analysis yet for this vulnerability")
    return analysis
