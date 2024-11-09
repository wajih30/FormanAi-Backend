import pytest
import os
from flask import Flask
from models.student_data_handler import StudentDataHandler
from utils.prompt_builder import PromptHandler
from db import db  # Make sure you import the database connection

# Create a fixture for the Flask app
@pytest.fixture
def app():
    # Create and configure the app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] =   os.getenv('DATABASE_URL')  # Update with your DB URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        yield app  # This will provide the app context to the tests

# Mock data for testing
mock_transcript_data = {
    'completed_courses': [
        {'course_code': 'CS101', 'grade': 'A', 'semester': 'Fall 2022'},
        {'course_code': 'MATH101', 'grade': 'B', 'semester': 'Spring 2023'},
        {'course_code': 'HIST200', 'grade': 'C', 'semester': 'Spring 2023'},
        {'course_code': 'CS102', 'grade': 'F', 'semester': 'Fall 2023'},
    ],
    'GPA': 3.2,
    'CGPA': 3.0
}

mock_major_id = 1
mock_major_name = "Computer Science"

# Create a mock StudentDataHandler
@pytest.fixture
def student_data_handler(app):
    with app.app_context():  # Ensure app context is active
        return StudentDataHandler(mock_transcript_data, mock_major_id, mock_major_name)

# Test the PromptHandler
def test_prompt_handler(student_data_handler):
    prompt_handler = PromptHandler(student_data_handler)

    # Test build_degree_audit_prompt
    degree_audit_prompt = prompt_handler.build_degree_audit_prompt()
    assert "Conduct a degree audit for the following student:" in degree_audit_prompt
    assert "Completed Courses" in degree_audit_prompt
    assert "Required Core Courses" in degree_audit_prompt
    assert "Remaining General Education Counts" in degree_audit_prompt

    # Test build_advising_prompt
    advising_prompt = prompt_handler.build_advising_prompt()
    assert "Analyze the following student's performance and provide course recommendations:" in advising_prompt
    assert "Current GPA" in advising_prompt
    assert "Recommendations:" in advising_prompt
