from flask import Flask, request, jsonify, send_from_directory
import openai
import os
from db import db
from dotenv import load_dotenv
from models.course_handler import CourseHandler
from models.student_data_handler import StudentDataHandler
from models.general_education_handler import GeneralEducationHandler
from utils.prompt_builder import PromptHandler
from utils.normalization import get_major_id_from_name

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home():
    return "Welcome to the Academic Chatbot!"

@app.route('/test_db')
def test_db():
    try:
        result = db.session.execute("SELECT 1").fetchone()
        return "Database connection successful!" if result else "Failed to connect to the database."
    except Exception as e:
        return f"Error: {e}"

@app.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    try:
        transcript_data = request.json.get("transcript_data")
        major_name = request.json.get("major_name")

        if not transcript_data or not major_name:
            return jsonify({"error": "Missing required fields"}), 400

        major_id = get_major_id_from_name(major_name)
        if major_id is None:
            return jsonify({"error": "Invalid major name"}), 400

        student_data_handler = StudentDataHandler(transcript_data, major_id, major_name)
        completed_courses = student_data_handler.completed_courses
        gpa = student_data_handler.gpa

        return jsonify({
            "status": "success",
            "completed_courses": completed_courses,
            "gpa": gpa
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/degree_audit', methods=['POST'])
def degree_audit():
    try:
        major_name = request.json.get("major_name")
        completed_courses = request.json.get("completed_courses")

        if not major_name or not completed_courses:
            return jsonify({"error": "Missing required fields"}), 400

        major_id = get_major_id_from_name(major_name)
        if major_id is None:
            return jsonify({"error": "Invalid major name"}), 400

        course_handler = CourseHandler(major_id)
        gen_ed_handler = GeneralEducationHandler(major_id)

        missing_core = course_handler.get_missing_core_courses(completed_courses)
        missing_electives = course_handler.get_missing_elective_courses(completed_courses)
        gen_ed_status = gen_ed_handler.get_remaining_requirements(completed_courses)

        transcript_data = {"Semester 1": completed_courses}
        course_tables = {
            "core": missing_core,
            "elective": missing_electives,
            "general education": gen_ed_status
        }

        prompt_handler = PromptHandler(major_id=major_id)
        audit_prompt = prompt_handler.build_degree_audit_prompt(transcript_data, course_tables)

        return jsonify({
            "status": "success",
            "missing_core_courses": missing_core,
            "missing_electives": missing_electives,
            "general_education_status": gen_ed_status,
            "degree_audit_prompt": audit_prompt
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/advising', methods=['POST'])
def advising():
    try:
        major_name = request.json.get("major_name")
        transcript_data = request.json.get("transcript_data")
        remaining_courses = request.json.get("remaining_courses")
        gen_ed_status = request.json.get("gen_ed_status")
        gpa = request.json.get("gpa")
        cgpa = request.json.get("cgpa")

        if not transcript_data or not remaining_courses or not gen_ed_status:
            return jsonify({"error": "Missing required fields"}), 400

        major_id = get_major_id_from_name(major_name)
        if major_id is None:
            return jsonify({"error": "Invalid major name"}), 400

        prompt_handler = PromptHandler(major_id=major_id)
        advising_prompt = prompt_handler.build_transcript_analysis_prompt(
            transcript_data=transcript_data,
            remaining_courses=remaining_courses,
            gen_ed_status=gen_ed_status,
            gpa=gpa,
            cgpa=cgpa
        )

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=advising_prompt,
            max_tokens=150
        )

        return jsonify({
            "status": "success",
            "advising_response": response.choices[0].text.strip()
        })
    except openai.error.OpenAIError as e:
        return jsonify({"error": f"OpenAI API Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/manual_query', methods=['POST'])
def manual_query():
    try:
        query_data = request.json.get("query_data")
        major_name = request.json.get("major_name")
        course_code = request.json.get("course_code")

        if not query_data or not major_name:
            return jsonify({"error": "Missing required fields"}), 400

        major_id = get_major_id_from_name(major_name)
        if major_id is None:
            return jsonify({"error": "Invalid major name"}), 400

        prompt_handler = PromptHandler(major_id=major_id)
        prompt = prompt_handler.build_manual_query_prompt(query_data, course_code)

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200
        )

        return jsonify({
            "status": "success",
            "manual_query_response": response.choices[0].text.strip()
        })
    except openai.error.OpenAIError as e:
        return jsonify({"error": f"OpenAI API Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created before the app runs
    app.run(debug=True)
