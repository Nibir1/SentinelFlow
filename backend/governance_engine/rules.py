import re
from dataclasses import dataclass
from typing import Pattern
from .models import Severity

# File-Level Comment:
# Contains the definitions of governance rules used to audit Power Apps.
# We use compiled Regex patterns for performance efficiency.

@dataclass
class GovernanceRule:
    """
    A dataclass representing a specific check to be performed.
    """
    rule_id: str
    severity: Severity
    description: str
    pattern: Pattern  # Compiled Regex pattern

# Define the library of rules
# In a real enterprise scenario, these might be loaded from a database or config file.
RULES_LIBRARY = [
    # Security Rule: Detect hardcoded client secrets or passwords
    # UPDATED LOGIC:
    # 1. Matches keywords (secret, password, apikey, token)
    # 2. Allows for suffixes (e.g., 'varSecretKey') using [a-zA-Z0-9_]*
    # 3. Matches assignment operators: ':' (JSON), '=' (Code), or ',' (Power Apps Set function)
    GovernanceRule(
        rule_id="SEC-001",
        severity=Severity.CRITICAL,
        description="Potential hardcoded secret or password detected.",
        pattern=re.compile(r'(?i)(secret|password|apikey|token)[a-zA-Z0-9_]*\s*[:=>,]\s*["\'][^"\']+["\']')
    ),
    
    # GDPR/Privacy Rule: Detect explicit use of social security numbers or sensitive PII labels
    GovernanceRule(
        rule_id="PRIV-001",
        severity=Severity.CRITICAL,
        description="Potential PII exposure (SSN/Social Security).",
        pattern=re.compile(r'(?i)(ssn|social\s?security|birth\s?date)')
    ),

    # Governance Rule: Naming Conventions (Hungarian Notation for variables)
    # Checks if variables are created without 'var' or 'loc' prefix, purely as a heuristic.
    # Matches Set(myVariable, ...) where myVariable doesn't start with var/loc/col
    GovernanceRule(
        rule_id="GOV-001",
        severity=Severity.WARNING,
        description="Variable does not follow naming conventions (should start with 'var', 'loc', or 'col').",
        pattern=re.compile(r'Set\(\s*(?!(var|loc|col))[a-zA-Z0-9_]+')
    ),

    # Performance Rule: Detect use of large collection clear commands without filters
    GovernanceRule(
        rule_id="PERF-001",
        severity=Severity.INFO,
        description="Heavy operation detected: Clearing large collections might impact performance.",
        pattern=re.compile(r'ClearCollect\(')
    )
]