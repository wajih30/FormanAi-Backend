from flask import Blueprint, request, jsonify, session
import logging
from services.chat_service import ChatService
from werkzeug.utils import secure_filename
import os

logger = logging.getLogger(__name__)





chat_bp = Blueprint('chat_bp', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@chat_bp.route('/', methods=['POST'])
def chat():
    try:
        content_type = request.headers.get('Content-Type', 'Unknown')

        if content_type.startswith('multipart/form-data'):
            logger.info("Handling multipart/form-data request")

            files = request.files.getlist('file')
            action = request.form.get('action', '').lower()
            major_name = request.form.get('major_name', None)

            if not action or not major_name:
                logger.error("Missing 'action' or 'major_name' in multipart request")
                return jsonify({
                    "status": "error",
                    "message": "Both 'action' and 'major_name' are required in multipart request."
                }), 400

            
            file_paths = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    file_paths.append(file_path)
                else:
                    logger.error(f"Unsupported file format: {file.filename}")
                    return jsonify({
                        "status": "error",
                        "message": f"Unsupported file format: {file.filename}"
                    }), 400

            logger.info(f"Files saved: {file_paths}")

            
            if "conversation_history" not in session:
                session["conversation_history"] = []
            if "context" not in session:
                session["context"] = {}

            
            chat_service = ChatService(
                conversation_history=session["conversation_history"],
                context=session["context"]
            )

            if action not in ["degree_audit", "advising"]:
                logger.error(f"Invalid action received: {action}")
                return jsonify({
                    "status": "error",
                    "message": "Invalid action. Valid actions: 'degree_audit', 'advising'."
                }), 400

            action_response = chat_service.handle_action(action, major_name, file_paths)

            session["conversation_history"] = chat_service.conversation_history
            session["context"] = chat_service.context
            return jsonify(action_response), 200

        elif content_type == 'application/json':
            logger.info("Handling application/json request")

            data = request.get_json()
            logger.debug(f"Incoming JSON data: {data}")

            action = data.get("action", "").lower()
            major_name = data.get("major_name")
            file_paths = data.get("file_paths", [])
            user_message = data.get("message")

            if "conversation_history" not in session:
                session["conversation_history"] = []
            if "context" not in session:
                session["context"] = {}

            chat_service = ChatService(
                conversation_history=session["conversation_history"],
                context=session["context"]
            )

            if action:
                if action not in ["degree_audit", "advising"]:
                    logger.error(f"Invalid action received: {action}")
                    return jsonify({
                        "status": "error",
                        "message": "Invalid action. Valid actions: 'degree_audit', 'advising'."
                    }), 400

                if not major_name or not file_paths:
                    logger.error("Missing required parameters for action.")
                    return jsonify({
                        "status": "error",
                        "message": "Major name and file paths are required for this action."
                    }), 400

                action_response = chat_service.handle_action(action, major_name, file_paths)

                session["conversation_history"] = chat_service.conversation_history
                session["context"] = chat_service.context
                return jsonify(action_response), 200

            if user_message:
                if not isinstance(user_message, str):
                    logger.error("Invalid 'message' field: not a string.")
                    return jsonify({
                        "status": "error",
                        "message": "The 'message' field must be a string."
                    }), 400

                gpt_response = chat_service.continue_conversation(user_message)

                session["conversation_history"] = chat_service.conversation_history
                session["context"] = chat_service.context
                return jsonify(gpt_response), 200

            logger.error("No valid action or message provided in the JSON request.")
            return jsonify({"status": "error", "message": "No valid action or message provided."}), 400

        else:
            logger.error(f"Unsupported Content-Type: {content_type}")
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json or multipart/form-data"
            }), 400

    except Exception as e:
        logger.error(f"Error during chat interaction: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred'}), 500
