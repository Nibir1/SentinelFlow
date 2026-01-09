import azure.functions as func
import logging
import json
from pydantic import ValidationError

# Import our Core Logic from Phase 1
from governance_engine import AuditRequest, GovernanceAuditor

# File-Level Comment:
# The Azure Function Entry Point (V2 Model).
# Acts as the REST API layer that Power Apps Custom Connectors will interact with.
# It handles HTTP parsing, validation, and serialization, delegating logic to 'governance_engine'.

# Initialize the Function App
# app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="audit", methods=["POST"])
def audit_app(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP Trigger: Governance Auditor.
    
    Accepts:
        JSON Payload matching 'AuditRequest' schema (app_name, app_definition_json).
    Returns:
        JSON Payload matching 'AuditResponse' schema (score, findings, compliance).
    """
    logging.info('SentinelFlow: Received audit request.')

    try:
        # 1. Parse Request Body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON format"}),
                status_code=400,
                mimetype="application/json"
            )

        # 2. Validate Input using Pydantic
        # This acts as a firewall against malformed data coming from Power Apps
        try:
            audit_request = AuditRequest(**req_body)
        except ValidationError as e:
            logging.warning(f"Validation Error: {e.json()}")
            return func.HttpResponse(
                json.dumps({"error": "Schema Validation Failed", "details": e.errors()}),
                status_code=400,
                mimetype="application/json"
            )

        # 3. Invoke Core Business Logic (The "Brain")
        auditor = GovernanceAuditor()
        audit_result = auditor.evaluate_app(audit_request)

        # 4. Serialize and Return Response
        # We use mode='json' to ensure Pydantic serializes Enums and Datetimes correctly
        response_json = audit_result.model_dump_json()

        logging.info(f"Audit completed for app: {audit_request.app_name}. Score: {audit_result.governance_score}")

        return func.HttpResponse(
            response_json,
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        # Catch-all for unexpected server errors
        logging.error(f"Internal Server Error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Internal Server Error"}),
            status_code=500,
            mimetype="application/json"
        )