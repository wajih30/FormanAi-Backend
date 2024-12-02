from flask import Blueprint, request, jsonify
import logging
from services.advising_service import AdvisingService
from werkzeug.utils import secure_filename
import os

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a Blueprint for advising routes
advising_bp = Blueprint('advising_bp', __name__)

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

@advising_bp.route('/', methods=['POST'])
def advising():
    """
    Handle advising requests based on the user's uploaded transcript and major.
    """
    try:
        # Check if files are present in the request
        if 'file' not in request.files:
            logger.error("No files uploaded.")
            return jsonify({
                'status': 'error',
                'message': 'No files uploaded.'
            }), 400

        # Collect uploaded files
        files = request.files.getlist('file')
        major_name = request.form.get('major_name')
        sub_major = request.form.get('sub_major', None)

        # Validate required fields
        if not major_name:
            logger.error("Major name is required.")
            return jsonify({
                'status': 'error',
                'message': 'Major name is required.'
            }), 400

        # Save uploaded files
        file_paths = save_uploaded_files(files)
        logger.info(f"Uploaded files saved at: {file_paths}")

        # Initialize AdvisingService
        logger.info(f"Initializing AdvisingService with major_name={major_name}, sub_major={sub_major}, file_paths={file_paths}.")
        advising_service = AdvisingService(file_paths=file_paths, major_name=major_name, sub_major=sub_major)

        # Process the advising request
        logger.info("Processing advising request...")
        result = advising_service.process_advising_request()

        # Check and handle the result
        if result.get('status') == 'error':
            logger.error(f"Advising service error: {result.get('message')}")
            return jsonify(result), 400

        logger.info("Advising request processed successfully.")
        return jsonify(result), 200

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return jsonify({
            'status': 'error',
            'message': str(ve)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error during advising request: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred during advising request processing.'
        }), 500
