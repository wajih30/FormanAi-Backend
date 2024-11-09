import logging
import openai
import os
from models.student_data_handler import StudentDataHandler
from utils.prompt_builder import PromptHandler  # Use PromptHandler to build degree audit prompts
from services.transcript_vision_service import TranscriptVisionService
from config import MAJOR_NAME_MAPPING

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('degree_audit_service.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levellevel)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class DegreeAuditService:
    """Handles the degree audit functionality for a student's academic progress."""

    def __init__(self, major_name, sub_major=None):
        """Initialize the service for the given major and optional sub-major."""
        logger.info(f"Initializing DegreeAuditService for major: {major_name}")
        self.major_name = major_name
        self.sub_major = sub_major
        self.major_id = self._get_major_id()

        if not self.major_id:
            logger.error(f"Invalid major name: {major_name}")
            raise ValueError(f"Invalid major name: {major_name}")

        # Initialize PromptHandler to build prompts
        self.prompt_handler = PromptHandler(major_name, sub_major)

    def perform_audit(self, transcript_file=None, manual_course_data=None):
        """
        Perform a degree audit based on the student's transcript or manually provided data.

        Args:
            transcript_file (file, optional): The uploaded transcript file (PDF or image).
            manual_course_data (dict, optional): Dictionary containing manually entered course information.

        Returns:
            str: Detailed degree audit analysis or error message.
        """
        logger.info("Starting degree audit process.")
        try:
            if transcript_file:
                transcript_data = self._extract_transcript_data(transcript_file)
                if not transcript_data:
                    return "Failed to extract transcript data. Please try again."
            else:
                transcript_data = manual_course_data or {}

            # Initialize StudentDataHandler for audit
            student_handler = StudentDataHandler(transcript_data, self.major_id, self.major_name)

            # Retrieve remaining courses and general education status
            remaining_courses = student_handler.get_remaining_courses()
            general_ed_status = student_handler.get_remaining_general_education_courses()

            # Build the degree audit prompt using the PromptHandler
            logger.info("Building degree audit prompt.")
            prompt = self.prompt_handler.build_degree_audit_prompt(
                transcript_data, remaining_courses, general_ed_status
            )

            # Generate and return OpenAI response
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
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an academic advisor bot specialized in degree audit analysis."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return f"An error occurred while generating a response: {str(e)}"

    def _get_major_id(self):
        """Retrieve the major ID based on the major name."""
        major_data = MAJOR_NAME_MAPPING.get(self.major_name)

        # Handle sub-major cases like 'Applied Psychology' or 'Sociology and Cult'
        if isinstance(major_data, dict):
            if self.major_name in major_data.get("sub_categories", {}):
                return major_data["id"]
            logger.error(f"Invalid sub-major: {self.major_name}")
            raise ValueError(f"Invalid sub-major: {self.major_name}")

        return major_data or None
