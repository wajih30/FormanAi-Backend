import pytest
from unittest.mock import patch, MagicMock
from models.course_handler import CourseHandler
from config import MAJOR_TABLE_MAPPING, PREFIX_MAJOR_MAPPING

@pytest.fixture
def mock_db_session():
    """Fixture to mock the database session."""
    with patch('db.db.session') as mock_session:
        yield mock_session

@pytest.fixture
def course_handler():
    """Fixture to create an instance of CourseHandler for the main category."""
    return CourseHandler(major_name="Computer Science")

@pytest.fixture
def course_handler_with_subcategory():
    """Fixture to create an instance of CourseHandler for a sub-category."""
    return CourseHandler(major_name="Sociology and Culture", sub_category="Sociology and Culture")

def test_initialization(course_handler):
    """Test initialization of CourseHandler."""
    assert course_handler.major_name == "Computer Science"
    assert course_handler.major_id == 1  # Assuming ID 1 is for Computer Science
    assert course_handler.mapping is not None

def test_get_major_id_with_name():
    """Test get_major_id method with major name."""
    handler = CourseHandler(major_name="Biology")
    major_id = handler.get_major_id(major_name="Biology")
    assert major_id == 2  # Assuming ID 2 is for Biology

def test_get_major_id_with_prefix():
    """Test get_major_id method with course code prefix."""
    handler = CourseHandler(course_code_prefix="CSCS")
    major_id = handler.get_major_id(course_code_prefix="CSCS")
    assert major_id == 1  # Assuming ID 1 is for Computer Science

def test_query_core_courses(course_handler, mock_db_session):
    """Test querying core courses."""
    mock_db_session.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [("CS101",), ("CS102",)]
    core_courses = course_handler.query_core_courses()
    assert len(core_courses) == 2  # Check if two core courses are returned

def test_query_elective_courses(course_handler, mock_db_session):
    """Test querying elective courses."""
    mock_db_session.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [("CS201",), ("CS202",)]
    elective_courses = course_handler.query_elective_courses()
    assert len(elective_courses) == 2  # Check if two elective courses are returned

def test_query_supporting_courses(course_handler, mock_db_session):
    """Test querying supporting courses."""
    course_handler.mapping = {"supporting": "supporting_courses_table"}
    mock_db_session.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [("CS301",)]
    supporting_courses = course_handler.query_supporting_courses()
    assert len(supporting_courses) == 1  # Check if one supporting course is returned

def test_get_major_requirements(course_handler):
    """Test retrieving major requirements."""
    requirements = course_handler.get_major_requirements()
    assert requirements is not None  # Check if requirements are retrieved

def test_sub_category_initialization(course_handler_with_subcategory):
    """Test initialization of CourseHandler with a sub-category."""
    assert course_handler_with_subcategory.major_name == "Sociology and Culture"
    assert course_handler_with_subcategory.sub_category == "Sociology and Culture"

def test_get_major_requirements_for_sub_category(course_handler_with_subcategory):
    """Test retrieving major requirements for a sub-category."""
    requirements = course_handler_with_subcategory.get_major_requirements()
    assert requirements is not None  # Check if requirements are retrieved
    # Add additional assertions specific to the Sociology and Culture sub-category if needed

# Additional tests for error scenarios and edge cases can be added as needed.
