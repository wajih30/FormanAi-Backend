from flask import Blueprint, request, jsonify
from services.degree_audit_service import DegreeAuditService

degree_audit_bp = Blueprint('degree_audit_bp', __name__)

@degree_audit_bp.route('/degree_audit', methods=['POST'])
def degree_audit():
    """
    Endpoint to perform a degree audit and return the student's unmet requirements.
    """
    try:
        data = request.json
        completed_courses = data.get("completed_courses")
        major_id = data.get("major_id")

        if not completed_courses or not major_id:
            return jsonify({"error": "Missing completed courses or major ID"}), 400

        # Initialize DegreeAuditService
        audit_service = DegreeAuditService(major_id)

        # Perform degree audit
        audit_result = audit_service.perform_audit(completed_courses)

        return jsonify({"message": "Degree audit completed", "audit_result": audit_result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
