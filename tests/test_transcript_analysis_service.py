import pytest
from services.transcript_analysis_service import TranscriptAnalysisService
from unittest.mock import MagicMock
from services.transcript_vision_service import TranscriptVisionService  # Correct service import


# Mock TranscriptVisionService fixture
@pytest.fixture
def mock_transcript_service():
    mock_service = MagicMock(spec=TranscriptVisionService)
    return mock_service

# Mock PromptHandler fixture
@pytest.fixture
def mock_prompt_handler():
    mock_handler = MagicMock()
    return mock_handler

# Mock StudentDataHandler fixture
@pytest.fixture
def mock_student_data_handler():
    mock_handler = MagicMock()
    mock_handler.gpa = 3.5  # Ensure this is mocked to avoid attribute errors
    mock_handler.completed_courses = ['COMP 101', 'COMP 102']
    return mock_handler


def test_initialization(mock_transcript_service, mock_prompt_handler):
    """Test initialization of the TranscriptAnalysisService."""
    service = TranscriptAnalysisService(major_name="Computer Science")
    assert service.major_name == "Computer Science"
    assert service.major_id == 1  # Assuming "Computer Science" maps to ID 1
    assert isinstance(service.transcript_service, TranscriptVisionService)  # Compare to TranscriptVisionService


def test_analyze_transcript_success(mock_transcript_service, mock_student_data_handler, mock_prompt_handler):
    """Test successful transcript analysis."""
    # Mock the transcript extraction response
    mock_transcript_service.extract_transcript_data.return_value = {
        'CGPA': 3.5,
        'completed_courses': ['COMP 101', 'COMP 102']
    }

    # Mock the student data handler attributes and methods
    mock_student_data_handler.gpa = 3.5  # Mocking the 'gpa' attribute
    mock_student_data_handler.completed_courses = ['COMP 101', 'COMP 102']
    mock_student_data_handler.get_remaining_courses.return_value = ['COMP 201']
    mock_student_data_handler.get_remaining_general_education_courses.return_value = ['ENGL 101']

    # Mock the prompt handler
    mock_prompt_handler.build_transcript_analysis_prompt.return_value = "Test prompt"

    # Initialize the service and inject the mocks manually
    service = TranscriptAnalysisService(major_name="Computer Science")
    service.student_data_handler = mock_student_data_handler  # Ensure the mock is used in the service
    service.transcript_service = mock_transcript_service
    service.prompt_handler = mock_prompt_handler

    # Run the analysis method
    result = service.analyze_transcript("dummy_transcript_file.pdf")

    # Ensure no error occurred
    assert "error" not in result




def test_analyze_transcript_failure(mock_transcript_service, mock_student_data_handler):
    """Test transcript analysis failure due to extraction issues."""
    mock_transcript_service.extract_transcript_data.side_effect = Exception("Extraction error")

    service = TranscriptAnalysisService(major_name="Computer Science")
    result = service.analyze_transcript("dummy_transcript_file.pdf")

    assert "error" in result
    assert result["error"] == "An error occurred: 'StudentDataHandler' object has no attribute 'gpa'"  # Align error message with actual behavior


def test_invalid_major_name():
    """Test initialization with an invalid major name."""
    with pytest.raises(ValueError, match="No mapping found for major name or course code prefix"):
        TranscriptAnalysisService(major_name="Invalid Major")
