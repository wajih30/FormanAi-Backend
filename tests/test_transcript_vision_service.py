import pytest
from unittest.mock import patch, MagicMock
from services.transcript_vision_service import TranscriptVisionService

@pytest.fixture
def vision_service():
    """Fixture to create an instance of TranscriptVisionService."""
    return TranscriptVisionService()

def test_empty_pdf_file(vision_service):
    """Test extraction with an empty PDF file."""
    mock_pdf_file = MagicMock()
    mock_pdf_file.name = "empty_transcript.pdf"
    mock_pdf_file.read.return_value = b""  # Simulate empty PDF content

    result = vision_service.extract_transcript_data(mock_pdf_file)

    assert "error" in result
    assert result["error"] == "Failed to process transcript: Invalid PDF structure"


def test_invalid_file_structure(vision_service):
    """Test handling of an invalid PDF file structure."""
    mock_pdf_file = MagicMock()
    mock_pdf_file.name = "invalid_transcript.pdf"
    mock_pdf_file.read.return_value = b"Invalid PDF content"  # Simulated invalid PDF content

    with patch('services.transcript_vision_service.convert_from_bytes', side_effect=Exception("Invalid PDF structure")):
        result = vision_service.extract_transcript_data(mock_pdf_file)

    assert "error" in result
    assert result["error"] == "Failed to process transcript: Invalid PDF structure"

def test_image_with_no_data(vision_service):
    """Test extraction from an image with no recognizable data."""
    mock_image_file = MagicMock()
    mock_image_file.name = "empty_image.jpg"
    
    with patch('PIL.Image.open', return_value=MagicMock()):
        with patch('openai.Image.create', return_value={'data': {'courses': []}}):
            result = vision_service.extract_transcript_data(mock_image_file)

    assert "completed_courses" in result
    assert len(result["completed_courses"]) == 0
    assert "failed_courses" in result
    assert len(result["failed_courses"]) == 0

def test_large_file_size(vision_service):
    """Test handling of a large file size."""
    mock_large_file = MagicMock()
    mock_large_file.name = "large_transcript.pdf"
    mock_large_file.read.return_value = b"%PDF-1.4..." * 10000  # Simulated large PDF content

    with patch('services.transcript_vision_service.convert_from_bytes', return_value=[MagicMock()]):
        result = vision_service.extract_transcript_data(mock_large_file)

    assert "completed_courses" in result
    assert "failed_courses" in result
    assert result["GPA"] == "N/A"  # Default value check
    assert result["CGPA"] == "N/A"  # Default value check

def test_malformed_gpt_response(vision_service):
    """Test handling of a malformed response from GPT-4 Vision API."""
    mock_image_file = MagicMock()
    mock_image_file.name = "transcript.jpg"

    with patch('PIL.Image.open', return_value=MagicMock()):
        with patch('openai.Image.create', return_value={'data': {}}):  # Malformed response
            result = vision_service.extract_transcript_data(mock_image_file)

    assert "completed_courses" in result
    assert len(result["completed_courses"]) == 0  # No courses extracted
    assert "failed_courses" in result
    assert len(result["failed_courses"]) == 0  # No failed courses extracted
    assert result["GPA"] == "N/A"  # Default value check
    assert result["CGPA"] == "N/A"  # Default value check
