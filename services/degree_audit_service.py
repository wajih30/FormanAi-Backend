import logging
from models.student_data_handler import StudentDataHandler
from utils.prompt_builder import build_degree_audit_prompt
from transcript_vision_service import TranscriptVisionService
import openai
import os

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('degree_audit_service.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class DegreeAuditService:
    """Handles the degree audit functionality for a student's academic progress."""

    def __init__(self, major_name):
        """Initialize the service for the given major."""
        logger.info(f"Initializing DegreeAuditService for major: {major_name}")
        self.major_name = major_name

    def perform_audit(self, transcript_file=None, manual_course_data=None):
        """
        Perform a degree audit based on the student's transcript or manually provided data.

        Args:
        - transcript_file (file): The uploaded transcript file (PDF or image) for analysis.
        - manual_course_data (dict): Dictionary containing manually entered course information.

        Returns:
        - str: Detailed degree audit analysis.
        """
        logger.info("Starting degree audit process.")
        try:
            if transcript_file:
                transcript_data = self._extract_transcript_data(transcript_file)
                if not transcript_data:
                    return "Failed to extract transcript data. Please try again."
            else:
                transcript_data = manual_course_data if manual_course_data else {}

            # Initialize StudentDataHandler for audit
            student_handler = StudentDataHandler(transcript_data, self._get_major_id(), self.major_name)

            # Retrieve remaining courses and general education status
            remaining_courses = student_handler.get_remaining_courses()
            general_ed_status = student_handler.get_remaining_general_education_courses()

            # Build the degree audit prompt
            logger.info("Building degree audit prompt.")
            prompt = build_degree_audit_prompt(transcript_data, remaining_courses, general_ed_status, self.major_name)

            # Generate OpenAI response
            return self._generate_openai_response(prompt)
        except Exception as e:
            logger.error(f"Error during degree audit: {e}")
            return f"An error occurred: {str(e)}"

    def _extract_transcript_data(self, transcript_file):
        """Extract transcript data using the TranscriptVisionService."""
        logger.info("Extracting transcript data using TranscriptVisionService.")
        try:
            transcript_service = TranscriptVisionService()
            return transcript_service.extract_transcript_data(transcript_file)
        except Exception as e:
            logger.error(f"Failed to extract transcript data: {e}")
            return None

    def _generate_openai_response(self, prompt):
        """Generate a response using OpenAI for the given prompt."""
        try:
            logger.info("Generating OpenAI response for degree audit.")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an academic advisor bot specialized in degree audit analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return f"An error occurred while generating a response: {str(e)}"

    def _get_major_id(self):
        """Retrieve the major ID based on the major name."""
        from config import MAJOR_NAME_MAPPING
        return MAJOR_NAME_MAPPING.get(self.major_name, None)
