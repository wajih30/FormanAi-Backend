from flask import Blueprint, request, jsonify
from utils.prompt_builder import PromptHandler
from services.openai_services import generate_chatgpt_response

# Define a blueprint for chat-related routes
chat_bp = Blueprint('chat_routes', __name__)

@chat_bp.route('/chat-with-bot', methods=['POST'])
def chat_with_bot():
    """
    Route to handle manual user queries related to academic advising and course requirements.
    """
    try:
        # Extract JSON data from the incoming request
        data = request.json
        major_name = data.get('major_name')  # User's major
        query_intent = data.get('query_intent')  # User's question or intent
        course_code = data.get('course_code', None)  # Optional course code, if provided

        if not major_name or not query_intent:
            return jsonify({"error": "Both 'major_name' and 'query_intent' are required."}), 400

        # Initialize PromptHandler with the provided major name
        prompt_handler = PromptHandler(major_name)

        # Build the manual query prompt using PromptHandler
        query_prompt = prompt_handler.build_manual_query_prompt(query_intent)

        # Generate the response using GPT-4
        response = generate_chatgpt_response(query_prompt)

        # Return the response as JSON
        return jsonify({
            "status": "success",
            "query_response": response
        })

    except ValueError as e:
        # Handle cases where invalid major names are provided
        return jsonify({"error": f"Invalid major: {str(e)}"}), 400

    except Exception as e:
        # Handle other unexpected errors gracefully
        return jsonify({"error": str(e)}), 500
