import re
import subprocess
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.core.database import SessionLocal
from app.models.scan import Scan, ScanStatus
from app.models.scan_log import ScanLog
from app.models.vulnerability import Severity, Vulnerability

OPEN_PORT_PATTERN = re.compile(r"^(\d+)/(tcp|udp)\s+open\s+(\S+)", re.MULTILINE)


def extract_host(url: str) -> str:
    candidate = url if "://" in url else f"//{url}"
    parsed = urlparse(candidate, scheme="http")
    return parsed.hostname or url


def run_scan(scan_id: str) -> None:
    db = SessionLocal()
    scan_uuid = uuid.UUID(scan_id)
    try:
        scan = db.query(Scan).filter(Scan.id == scan_uuid).first()
        if not scan:
            return

        scan.status = ScanStatus.RUNNING
        scan.started_at = datetime.now(timezone.utc)
        db.commit()

        host = extract_host(scan.target.url)

        result = subprocess.run(
            ["nmap", "-F", "-T4", host],
            capture_output=True,
            text=True,
            timeout=120,
        )
        raw_output = result.stdout + result.stderr

        db.add(ScanLog(scan_id=scan.id, tool_name="nmap", raw_output=raw_output))
        db.commit()

        for port, proto, service in OPEN_PORT_PATTERN.findall(raw_output):
            db.add(
                Vulnerability(
                    scan_id=scan.id,
                    title=f"Open port {port}/{proto} ({service})",
                    severity=Severity.INFO,
                    affected_endpoint=f"{host}:{port}",
                    description=f"Nmap detected an open {proto} port running {service}.",
                    evidence=raw_output[:2000],
                    source_tool="nmap",
                )
            )
        db.commit()

        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as exc:
        db.rollback()
        scan = db.query(Scan).filter(Scan.id == scan_uuid).first()
        if scan:
            scan.status = ScanStatus.FAILED
            scan.completed_at = datetime.now(timezone.utc)
            db.add(ScanLog(scan_id=scan.id, tool_name="nmap", raw_output=f"ERROR: {exc}"))
            db.commit()
    finally:
        db.close()
