from typing import List
from .models import AuditRequest, AuditResponse, Finding, Severity
from .rules import RULES_LIBRARY

# File-Level Comment:
# The core logic engine. It takes an AuditRequest, runs it against the RULES_LIBRARY,
# and generates an AuditResponse.

class GovernanceAuditor:
    """
    Service class responsible for auditing App definitions.
    """

    def evaluate_app(self, request: AuditRequest) -> AuditResponse:
        """
        Main entry point for auditing an app.
        
        Args:
            request (AuditRequest): The input payload containing app definition.
            
        Returns:
            AuditResponse: The detailed governance report.
        """
        findings: List[Finding] = []
        source_code = request.app_definition_json

        # 1. Iterate through all defined rules
        for rule in RULES_LIBRARY:
            # Find all matches in the source code
            matches = rule.pattern.finditer(source_code)
            
            for match in matches:
                # Extract the matching text for context (truncated to 50 chars)
                matched_text = match.group(0)[:50]
                
                findings.append(Finding(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=f"{rule.description} Found pattern: '{matched_text}...'",
                    location=f"Index: {match.start()}"
                ))

        # 2. Calculate Governance Score
        # Start at 100. Deduct 20 for Critical, 10 for Warning, 2 for Info.
        score = 100
        for f in findings:
            if f.severity == Severity.CRITICAL:
                score -= 20
            elif f.severity == Severity.WARNING:
                score -= 10
            elif f.severity == Severity.INFO:
                score -= 2
        
        # Ensure score doesn't drop below 0
        score = max(0, score)

        # 3. Determine Compliance (Pass/Fail)
        # Fail if score < 70 OR if any Critical issues exist
        has_critical = any(f.severity == Severity.CRITICAL for f in findings)
        is_compliant = (score >= 70) and (not has_critical)

        # 4. Return structured response
        return AuditResponse(
            app_name=request.app_name,
            governance_score=score,
            findings=findings,
            is_compliant=is_compliant
        )