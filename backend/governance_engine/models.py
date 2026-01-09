from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

# File-Level Comment:
# Defines the Pydantic models for the SentinelFlow Governance Engine.
# These models ensure that data passing between Power Apps and Azure Functions
# is strictly typed and validated, preventing runtime errors.

class Severity(str, Enum):
    """
    Enum representing the severity level of a governance finding.
    """
    CRITICAL = "Critical"  # Security risks (e.g., hardcoded secrets)
    WARNING = "Warning"    # Best practice violations (e.g., poor naming)
    INFO = "Info"          # General optimizations

class Finding(BaseModel):
    """
    Represents a single governance violation found during the audit.
    """
    rule_id: str = Field(..., description="Unique identifier for the broken rule")
    severity: Severity = Field(..., description="Severity level of the finding")
    message: str = Field(..., description="Human-readable explanation of the issue")
    location: Optional[str] = Field(None, description="Where in the code/JSON the issue was found")

class AuditRequest(BaseModel):
    """
    The input payload expected from Power Apps.
    """
    app_name: str = Field(..., description="Name of the Power App being scanned")
    app_definition_json: str = Field(..., description="The raw JSON content or code snippet of the Power App")

class AuditResponse(BaseModel):
    """
    The output payload returned to Power Apps.
    """
    app_name: str
    audit_date: datetime = Field(default_factory=datetime.utcnow)
    governance_score: int = Field(..., ge=0, le=100, description="Calculated health score (0-100)")
    findings: List[Finding] = Field(default_factory=list)
    is_compliant: bool = Field(..., description="True if score > threshold and no Critical issues")