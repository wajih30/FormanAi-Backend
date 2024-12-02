from flask import Blueprint, request, jsonify
import logging
import os
from werkzeug.utils import secure_filename
from services.degree_audit_service import DegreeAuditService

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a Blueprint for degree audit routes
degree_audit_bp = Blueprint("degree_audit_bp", __name__)

# Define allowed file extensions and upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_files(files):
    """Save uploaded files and return their secure paths."""
    file_paths = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            file_paths.append(file_path)
        else:
            logger.error(f"Unsupported file format: {file.filename}")
            raise ValueError(f"Unsupported file format: {file.filename}")
    return file_paths

@degree_audit_bp.route("/", methods=["POST"])
def degree_audit_route():
    """
    Handle degree audit requests with support for multiple file inputs for images
    or a single file input for PDFs, sent as multipart/form-data.
    """
    try:
        # Check if files are present in the request
        if "file" not in request.files:
            logger.error("No files uploaded.")
            return jsonify({
                "status": "error",
                "message": "No files uploaded."
            }), 400

        # Collect uploaded files
        files = request.files.getlist("file")
        major_name = request.form.get("major_name")

        # Validate required fields
        if not major_name:
            logger.error("Major name is required.")
            return jsonify({
                "status": "error",
                "message": "Major name is required."
            }), 400

        # Save uploaded files
        file_paths = save_uploaded_files(files)
        logger.info(f"Uploaded files saved at: {file_paths}")

        # Initialize DegreeAuditService
        logger.info(f"Initializing DegreeAuditService with major_name={major_name}, file_paths={file_paths}.")
        degree_audit_service = DegreeAuditService(file_paths=file_paths, major_name=major_name)

        # Process the degree audit
        logger.info("Processing degree audit request...")
        result = degree_audit_service.perform_audit()

        # Check and handle the result
        if result.get("status") == "error":
            logger.error(f"Degree audit service error: {result.get('message')}")
            return jsonify(result), 400

        logger.info("Degree audit request processed successfully.")
        return jsonify(result), 200

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error during degree audit request: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred during degree audit processing."
        }), 500
