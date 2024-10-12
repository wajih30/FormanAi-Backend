from flask import Flask, request, jsonify, send_from_directory
import os
import logging
from dotenv import load_dotenv

from db import db
from models.course_handler import CourseHandler
from utils.prompt_builder import PromptHandler
from services.openai_services import generate_chatgpt_response  # Updated import

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

@app.route('/')
def home():
    return "Welcome to the Academic Chatbot!"

@app.route('/test_db')
def test_db():
    try:
        result = db.session.execute("SELECT 1").fetchone()
        return "Database connection successful!" if result else "Failed to connect to the database."
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return f"Error: {e}", 500

@app.route('/manual_query', methods=['POST'])
def manual_query():
    try:
        query_data = request.json.get("query_data")
        major_name = request.json.get("major_name")

        if not query_data or not major_name:
            return jsonify({"error": "Missing query data or major name"}), 400

        # Use PromptHandler to build the prompt
        prompt_handler = PromptHandler(major_name=major_name)
        prompt = prompt_handler.build_manual_query_prompt(query_data)

        # Use OpenAI to generate a response
        reply = generate_chatgpt_response(prompt)

        return jsonify({"status": "success", "manual_query_response": reply})

    except Exception as e:
        logger.error(f"Error in manual_query: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    try:
        transcript_data = request.json.get("transcript_data")
        major_name = request.json.get("major_name")

        if not transcript_data or not major_name:
            return jsonify({"error": "Missing required fields"}), 400

        prompt_handler = PromptHandler(major_name=major_name)
        completed_courses = prompt_handler.course_handler.get_courses("completed")

        return jsonify({"status": "success", "completed_courses": completed_courses})

    except Exception as e:
        logger.error(f"Error in upload_transcript: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/degree_audit', methods=['POST'])
def degree_audit():
    try:
        major_name = request.json.get("major_name")
        completed_courses = request.json.get("completed_courses")

        if not major_name or not completed_courses:
            return jsonify({"error": "Missing required fields"}), 400

        prompt_handler = PromptHandler(major_name=major_name)
        core_courses = prompt_handler.course_handler.get_courses("core")
        missing_core = [c for c in core_courses if c not in completed_courses]

        return jsonify({"status": "success", "missing_core_courses": missing_core})

    except Exception as e:
        logger.error(f"Error in degree_audit: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/advising', methods=['POST'])
def advising():
    try:
        major_name = request.json.get("major_name")
        gpa = request.json.get("gpa")
        cgpa = request.json.get("cgpa")

        if not major_name:
            return jsonify({"error": "Missing major name"}), 400

        # Prepare advising prompt
        advising_prompt = f"Advise on next steps for a student in {major_name} with GPA {gpa} and CGPA {cgpa}."

        # Use OpenAI to generate a response
        response = generate_chatgpt_response(advising_prompt)

        return jsonify({"status": "success", "advising_response": response})

    except Exception as e:
        logger.error(f"Error in advising: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)  # Run the Flask app in debug mode
