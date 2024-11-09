from flask import Flask, request, jsonify
import os
import logging
from dotenv import load_dotenv
from db import db

from models.student_data_handler import StudentDataHandler  # Ensure StudentDataHandler is correctly imported
from services.openai_services import generate_chatgpt_response  # Updated import
from utils.prompt_builder import PromptHandler  # Corrected import

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def create_app():
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

            # Create an instance of StudentDataHandler
            student_data_handler = StudentDataHandler(transcript_data=request.json.get("transcript_data"), major_id=1, major_name=major_name)
            prompt_handler = PromptHandler(student_data_handler)  # Use the correct class name

            # Use PromptHandler to build the prompt
            prompt = prompt_handler.build_advising_prompt()

            # Use OpenAI to generate a response
            reply = generate_chatgpt_response(prompt)

            return jsonify({"status": "success", "manual_query_response": reply})

        except Exception as e:
            logger.error(f"Error in manual_query: {str(e)}")
            return jsonify({"error": str(e)}), 500

    # Other routes...

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)  # Run the Flask app in debug mode
