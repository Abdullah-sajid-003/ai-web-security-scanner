from typing import Tuple

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

from app.core.config import settings
from app.models.vulnerability import Vulnerability

SYSTEM_PROMPT = (
    "You are a security analyst explaining a vulnerability scan finding to a "
    "developer who is not a security expert. Given the finding, respond with "
    "exactly three lines, each prefixed exactly like this and nothing else:\n"
    "EXPLANATION: <1-3 sentences on what this finding means and why it matters, in plain English>\n"
    "REMEDIATION: <concrete, actionable steps to fix or mitigate this>\n"
    "RISK: <1-2 sentences on the realistic risk/impact if left unaddressed>"
)


class AIAnalysisError(Exception):
    pass


def generate_analysis(vuln: Vulnerability) -> dict:
    if not settings.GEMINI_API_KEY:
        raise AIAnalysisError(
            "GEMINI_API_KEY is not set. Add it to backend/.env to enable AI analysis."
        )

    genai.configure(api_key=settings.GEMINI_API_KEY)

    finding_summary = (
        f"Title: {vuln.title}\n"
        f"Severity: {vuln.severity.value if vuln.severity else 'unknown'}\n"
        f"Affected endpoint: {vuln.affected_endpoint or 'unknown'}\n"
        f"Description: {vuln.description or 'none provided'}\n"
        f"Detected by: {vuln.source_tool or 'unknown tool'}"
    )

    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            system_instruction=SYSTEM_PROMPT,
        )
        response = model.generate_content(finding_summary)
    except GoogleAPIError as exc:
        raise AIAnalysisError(f"Gemini API request failed: {exc}") from exc

    text = response.text or ""
    explanation, remediation, risk = _parse_sections(text)

    return {
        "plain_english_explanation": explanation,
        "remediation_steps": remediation,
        "risk_context": risk,
    }


def _parse_sections(text: str) -> Tuple[str, str, str]:
    explanation = remediation = risk = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("EXPLANATION:"):
            explanation = line[len("EXPLANATION:"):].strip()
        elif line.startswith("REMEDIATION:"):
            remediation = line[len("REMEDIATION:"):].strip()
        elif line.startswith("RISK:"):
            risk = line[len("RISK:"):].strip()

    if not explanation and not remediation and not risk:
        explanation = text.strip()

    return explanation, remediation, risk
