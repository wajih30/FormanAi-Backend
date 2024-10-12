from flask import Blueprint, request, jsonify
from utils.prompt_builder import build_manual_query_prompt
from services.openai_services import generate_chatgpt_response

chat_bp = Blueprint('chat_routes', __name__)

@chat_bp.route('/chat-with-bot', methods=['POST'])
def chat_with_bot():
    """
    Route to handle manual user queries related to academic advising and course requirements.
    """
    try:
        major_name = request.json.get('major_name')  # User's major
        query_intent = request.json.get('query_intent')  # User's question or intent
        course_code = request.json.get('course_code')  # Optional course code if asking about specific courses

        if not major_name or not query_intent:
            return jsonify({"error": "Major and query intent are required."}), 400

        # Build the manual query prompt
        query_prompt = build_manual_query_prompt(query_intent, major_name, course_code)

        # Generate the response using GPT-4
        response = generate_chatgpt_response(query_prompt)

        return jsonify({
            "query_response": response
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
