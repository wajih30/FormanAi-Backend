from flask import Blueprint, request, jsonify
from services.degree_audit_service import DegreeAuditService
from utils.normalization import get_major_id_from_name

# Define a Blueprint for the degree audit-related routes
degree_audit_bp = Blueprint('degree_audit_bp', __name__)

@degree_audit_bp.route('/degree_audit', methods=['POST'])
def degree_audit():
    """
    Endpoint to perform a degree audit and return the student's unmet requirements.
    """
    try:
        # Extract data from the incoming request
        data = request.json
        completed_courses = data.get("completed_courses")
        major_name = data.get("major_name")  # Updated to receive major_name, not major_id

        if not completed_courses or not major_name:
            return jsonify({"error": "Both 'completed_courses' and 'major_name' are required."}), 400

        # Convert major name to major ID using the normalization function
        major_id = get_major_id_from_name(major_name)
        if not major_id:
            return jsonify({"error": f"Invalid major name: {major_name}"}), 400

        # Initialize the DegreeAuditService with the resolved major_id
        audit_service = DegreeAuditService(major_id)

        # Perform the degree audit to find unmet requirements
        audit_result = audit_service.perform_audit(completed_courses)

        # Return the audit results in JSON format
        return jsonify({
            "status": "success",
            "message": "Degree audit completed successfully.",
            "audit_result": audit_result
        }), 200

    except ValueError as e:
        # Handle invalid input, such as an unrecognized major name
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        # Handle other unexpected exceptions
        return jsonify({"error": str(e)}), 500
