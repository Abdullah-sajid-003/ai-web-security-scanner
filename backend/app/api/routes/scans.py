import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.queue import scan_queue
from app.models.scan import Scan, ScanStatus
from app.models.target import Target
from app.models.user import User
from app.schemas.scan import ScanDetailResponse, ScanResponse
from app.services.scanner import run_scan

router = APIRouter()


@router.post(
    "/targets/{target_id}/scans",
    response_model=ScanResponse,
    status_code=status.HTTP_201_CREATED,
)
def launch_scan(
    target_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = (
        db.query(Target)
        .filter(Target.id == target_id, Target.owner_id == current_user.id)
        .first()
    )
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    scan = Scan(target_id=target.id, status=ScanStatus.QUEUED)
    db.add(scan)
    db.commit()
    db.refresh(scan)

    scan_queue.enqueue(run_scan, str(scan.id), job_timeout=180)

    return scan


@router.get("/scans", response_model=List[ScanResponse])
def list_scans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Scan)
        .join(Target, Scan.target_id == Target.id)
        .filter(Target.owner_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )


@router.get("/scans/{scan_id}", response_model=ScanDetailResponse)
def get_scan(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scan = (
        db.query(Scan)
        .join(Target, Scan.target_id == Target.id)
        .filter(Scan.id == scan_id, Target.owner_id == current_user.id)
        .first()
    )
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan
