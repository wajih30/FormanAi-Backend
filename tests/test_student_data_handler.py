import pytest
from app import create_app
from models.student_data_handler import StudentDataHandler

@pytest.fixture
def app():
    # Create a Flask application instance
    app = create_app()
    
    # Set up the app context for the tests
    with app.app_context():
        # You can create tables or seed the database here if needed
        yield app  # This allows the test to run

@pytest.fixture
def student_data_handler():
    # Sample transcript data for testing
    transcript_data = {
        "completed_courses": [
            {"course_code": "CS101", "grade": "A", "semester": "Fall 2022"},
            {"course_code": "MATH101", "grade": "B", "semester": "Fall 2022"},
            {"course_code": "ENG201", "grade": "C", "semester": "Spring 2023"},
            {"course_code": "HIST200", "grade": "A", "semester": "Spring 2023"},
            # No failed courses here
        ],
        "GPA": 3.2,
        "CGPA": 3.0
    }
    major_id = 1
    major_name = "Computer Science"
    return StudentDataHandler(transcript_data, major_id, major_name)

def test_prepare_gpt_input(app, student_data_handler):
    """Test preparing input for GPT."""
    gpt_input = student_data_handler.prepare_gpt_input(for_degree_audit=True)
    
    # Assert that 'failed_courses' is empty
    assert len(gpt_input['failed_courses']) == 0  # Check for failed courses
    
    # You can add more assertions based on your requirements
    assert 'completed_courses' in gpt_input
    assert 'required_courses' in gpt_input
    assert 'formatted_courses' in gpt_input
    assert 'gpa' in gpt_input
    assert 'cgpa' in gpt_input
