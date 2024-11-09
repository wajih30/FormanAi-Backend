import pytest
from app import create_app  # Import your Flask app creation function
from models.general_education_handler import GeneralEducationHandler

@pytest.fixture
def general_education_handler():
    """Fixture to create a GeneralEducationHandler instance for Applied Psychology."""
    major_name = "Applied Psychology"  # Assuming this is the correct major name
    handler = GeneralEducationHandler(major_name)
    return handler

@pytest.fixture
def app_context():
    """Fixture to provide an application context for the test."""
    app = create_app()  # Replace this with your app creation function
    with app.app_context():
        yield

def test_query_general_education_courses(app_context, general_education_handler):
    """Test querying of general education courses from the database."""
    courses = general_education_handler.query_general_education_courses()  # Correct method name
    assert isinstance(courses, list)
