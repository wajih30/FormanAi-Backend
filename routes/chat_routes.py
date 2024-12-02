from flask import Blueprint, request, jsonify, session
import logging
from services.chat_service import ChatService

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create Blueprint for chat routes
chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/', methods=['POST'])
def chat():
    try:
        if not request.is_json:
            content_type = request.headers.get('Content-Type', 'Unknown')
            logger.error(f"Invalid Content-Type: {content_type}")
            return jsonify({'status': 'error', 'message': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        logger.debug(f"Incoming request data: {data}")

        action = data.get("action", "").lower()
        major_name = data.get("major_name")
        file_paths = data.get("file_paths", [])
        user_message = data.get("message")

        # Initialize or retrieve session context and history
        if "conversation_history" not in session:
            session["conversation_history"] = []
        if "context" not in session:
            session["context"] = {}

        # Initialize ChatService with session data
        chat_service = ChatService(
            conversation_history=session["conversation_history"],
            context=session["context"]
        )

        # Handle specific actions like "degree_audit" or "advising"
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

            # Update session with the latest context and history
            session["conversation_history"] = chat_service.conversation_history
            session["context"] = chat_service.context
            return jsonify(action_response), 200

        # Handle general user messages for chat
        if user_message:
            if not isinstance(user_message, str):
                logger.error("Invalid 'message' field: not a string.")
                return jsonify({
                    "status": "error",
                    "message": "The 'message' field must be a string."
                }), 400

            gpt_response = chat_service.continue_conversation(user_message)

            # Update session with the latest context and history
            session["conversation_history"] = chat_service.conversation_history
            session["context"] = chat_service.context
            return jsonify(gpt_response), 200

        logger.error("No valid action or message provided in the request.")
        return jsonify({"status": "error", "message": "No valid action or message provided."}), 400

    except Exception as e:
        logger.error(f"Error during chat interaction: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': 'An unexpected error occurred'}), 500
