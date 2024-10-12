import logging
import openai
import os
from transcript_vision_service import TranscriptVisionService
from models.course_handler import CourseHandler
from models.student_data_handler import StudentDataHandler
from utils.prompt_builder import PromptHandler  # Import the centralized PromptHandler
from utils.normalization import get_major_id_from_name  # Use helper for major name to ID
from config import MAJOR_NAME_MAPPING

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('transcript_analysis_service.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TranscriptAnalysisService:
    """Handles transcript data extraction and academic analysis."""

    def __init__(self, major_name, sub_major=None):
        """Initialize the service for a given major and optional sub-major."""
        logger.info(f"Initializing TranscriptAnalysisService for major: {major_name}, sub-major: {sub_major}")
        
        self.major_name = major_name
        self.sub_major = sub_major
        self.major_id = get_major_id_from_name(major_name)  # Map major name to ID

        if not self.major_id:
            logger.error(f"Invalid major name: {major_name}")
            raise ValueError(f"Invalid major name: {major_name}")

        self.transcript_service = TranscriptVisionService()
        self.course_handler = CourseHandler(self.major_id, sub_major)
        self.prompt_handler = PromptHandler(major_name, sub_major)  # Pass major name and sub-major

    def analyze_transcript(self, transcript_file):
        """Analyze the provided transcript and recommend courses."""
        logger.info(f"Starting transcript analysis for major: {self.major_name}")

        try:
            # Step 1: Extract transcript data using the Vision service
            transcript_data = self.transcript_service.extract_transcript_data(transcript_file)
            logger.info(f"Extracted transcript data: {transcript_data}")
        except Exception as e:
            logger.error(f"Failed to extract transcript data: {e}")
            return {"error": "Failed to extract transcript data."}

        try:
            # Step 2: Process the transcript data through the StudentDataHandler
            student_handler = StudentDataHandler(transcript_data, self.major_id, self.major_name)
            completed_courses = student_handler.completed_courses
            gpa = student_handler.gpa

            logger.info(f"Completed courses: {completed_courses}, GPA: {gpa}")

            # Step 3: Get remaining courses (core, elective, general education)
            remaining_courses = student_handler.get_remaining_courses()
            gen_ed_status = student_handler.get_remaining_general_education_courses()

            logger.info(f"Remaining courses: {remaining_courses}")
            logger.info(f"General education status: {gen_ed_status}")

            # Step 4: Use PromptHandler to build a detailed analysis prompt
            logger.info("Building transcript analysis prompt using PromptHandler.")
            prompt = self.prompt_handler.build_transcript_analysis_prompt(
                transcript_data, 
                remaining_courses, 
                gen_ed_status, 
                gpa, 
                transcript_data.get("CGPA", "N/A")
            )

            # Step 5: Send the prompt to OpenAI and get the response
            return self._generate_openai_response(prompt)
        except Exception as e:
            logger.error(f"Error during transcript analysis: {e}")
            return {"error": f"An error occurred: {str(e)}"}

    def _generate_openai_response(self, prompt):
        """Generate a response using OpenAI for the given prompt."""
        try:
            logger.info("Generating OpenAI response for transcript analysis.")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an academic advisor bot specialized in degree analysis and course recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return {"error": f"An error occurred while generating a response: {str(e)}"}
