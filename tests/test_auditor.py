import sys
import os
import pytest

# Add the backend directory to sys.path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from governance_engine import GovernanceAuditor, AuditRequest

# File-Level Comment:
# Unit tests for the Governance Logic.
# Ensures that rules correctly identify security risks and that scoring logic works as expected.
# Run with: pytest tests/

def test_clean_app_score():
    """
    Scenario: An app with no violations should have a perfect score (100) and be compliant.
    """
    auditor = GovernanceAuditor()
    clean_json = """
    Set(varUserName, User().FullName);
    """
    
    request = AuditRequest(app_name="CleanApp", app_definition_json=clean_json)
    response = auditor.evaluate_app(request)
    
    assert response.governance_score == 100
    assert response.is_compliant is True
    assert len(response.findings) == 0

def test_hardcoded_secret_detection():
    """
    Scenario: An app with a hardcoded secret should fail compliance and trigger a Critical finding.
    """
    auditor = GovernanceAuditor()
    # Bad pattern: Secret = "12345"
    bad_json = """
    Set(varConfig, { ClientId: "123", Secret: "super_secret_value" });
    """
    
    request = AuditRequest(app_name="RiskyApp", app_definition_json=bad_json)
    response = auditor.evaluate_app(request)
    
    # Check that score dropped (100 - 20 = 80)
    assert response.governance_score <= 80
    # Must be non-compliant because of Critical severity
    assert response.is_compliant is False
    
    # Verify specific finding
    critical_errors = [f for f in response.findings if f.severity == "Critical"]
    assert len(critical_errors) > 0
    assert "SEC-001" in critical_errors[0].rule_id

def test_naming_convention_warning():
    """
    Scenario: Variables not using Hungarian notation (var/loc/col) should trigger a Warning.
    """
    auditor = GovernanceAuditor()
    # Bad pattern: Set(myVariable, ...) instead of Set(varMyVariable, ...)
    sloppy_json = """
    Set(myVariable, "test");
    """
    
    request = AuditRequest(app_name="SloppyApp", app_definition_json=sloppy_json)
    response = auditor.evaluate_app(request)
    
    # Check finding exists
    warnings = [f for f in response.findings if f.rule_id == "GOV-001"]
    assert len(warnings) > 0
    assert response.governance_score < 100