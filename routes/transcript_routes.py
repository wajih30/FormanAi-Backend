from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from models.student_data_handler import StudentDataHandler
from services.transcript_vision_service import TranscriptVisionService

# Create a Blueprint for transcript routes
transcript_bp = Blueprint('transcript_bp', __name__)

# App-specific configurations
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure logger for this blueprint
logger = logging.getLogger('transcript_bp')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('transcript_bp.log')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    is_allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    logger.debug(f"Checking if file '{filename}' is allowed: {is_allowed}")
    return is_allowed


def save_uploaded_file(file):
    """Save the uploaded file and return its secure path."""
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    logger.info(f"File saved to {file_path}")
    return file_path


@transcript_bp.route('/upload', methods=['POST'])
def upload_transcript():
    """
    Upload and process the student's transcript. Handles multiple image files or a single PDF.
    """
    logger.info("Received request to upload transcript.")
    try:
        # Get uploaded files and form data
        files = request.files.getlist('file')
        major_name = request.form.get('major_name')

        if not files or not all(file.filename for file in files):
            logger.error("No files uploaded.")
            return jsonify({'status': 'error', 'message': 'No files uploaded.'}), 400

        if not major_name:
            logger.error("No major name provided.")
            return jsonify({'status': 'error', 'message': 'No major name provided.'}), 400

        # Validate and save files
        saved_file_paths = []
        for file in files:
            if not allowed_file(file.filename):
                logger.error(f"Unsupported file format: {file.filename}")
                return jsonify({'status': 'error', 'message': f"Unsupported file format: {file.filename}"}), 400
            saved_file_paths.append(save_uploaded_file(file))

        logger.info(f"All files successfully saved: {saved_file_paths}")

        # Initialize TranscriptVisionService to extract raw GPT output
        logger.info("Initializing TranscriptVisionService.")
        transcript_service = TranscriptVisionService()
        raw_transcript_data = transcript_service.extract_transcript_text(saved_file_paths)

        if not raw_transcript_data or "error" in raw_transcript_data:
            logger.error("Failed to extract transcript data.")
            return jsonify({'status': 'error', 'message': 'Failed to process transcript data.'}), 500

        logger.info("Transcript data successfully extracted from GPT.")
        logger.debug(f"Raw GPT Output: {raw_transcript_data}")

        # Initialize StudentDataHandler with the raw GPT output
        logger.info("Initializing StudentDataHandler.")
        student_handler = StudentDataHandler(
            file_paths=saved_file_paths,
            major_name=major_name,
            transcript_service=transcript_service,
            raw_transcript_data=raw_transcript_data  # Pass the extracted data
        )
        gpt_input = student_handler.prepare_gpt_input()

        logger.info("Data prepared by StudentDataHandler.")
        return jsonify({
            'status': 'success',
            'message': 'Transcript processed successfully.',
            'data': gpt_input
        }), 200

    except Exception as e:
        logger.exception("An error occurred while processing the transcript.")
        return jsonify({'status': 'error', 'message': 'An error occurred while processing the transcript.'}), 500
