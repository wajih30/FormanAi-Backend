import logging
import re
from utils.transcript_extraction import extract_course_data_from_text
from utils.normalization import normalize_course_code

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('student_data_handler.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class StudentDataHandler:
    """
    Manages student data extracted from transcripts.
    """

    def __init__(self, transcript_data, major_id, major_name, sub_major=None):
        """
        Initialize the StudentDataHandler.

        Args:
            transcript_data (str): Raw transcript data.
            major_id (int): The major ID.
            major_name (str): The major name.
            sub_major (str, optional): Sub-major if applicable.
        """
        self.transcript_data = transcript_data
        self.major_id = major_id
        self.major_name = major_name
        self.sub_major = sub_major

        # Extract completed courses and GPA
        self.completed_courses = self.extract_completed_courses()
        self.gpa = self.extract_gpa_from_transcript()

        logger.info(f"Initialized StudentDataHandler for Major: {major_name} (ID: {major_id})")

    def extract_completed_courses(self):
        """
        Extract completed courses from the raw transcript data.

        Returns:
            list: List of normalized completed course codes.
        """
        try:
            extracted_data = extract_course_data_from_text(self.transcript_data)
            completed_courses = [
                normalize_course_code(course['course_code'])
                for semester, courses in extracted_data.items()
                for course in courses
            ]

            logger.info(f"Extracted completed courses: {completed_courses}")
            return completed_courses

        except Exception as e:
            logger.error(f"Error extracting completed courses: {e}")
            return []

    def extract_gpa_from_transcript(self):
        """
        Extract the GPA from the transcript data.

        Returns:
            float: Extracted GPA or 0.0 if not found.
        """
        try:
            gpa = self._find_gpa_in_transcript(self.transcript_data)
            logger.info(f"Extracted GPA: {gpa}")
            return gpa

        except Exception as e:
            logger.error(f"Error extracting GPA: {e}")
            return 0.0

    def _find_gpa_in_transcript(self, raw_text):
        """
        Find the GPA in the transcript using a regex pattern.

        Args:
            raw_text (str): Raw transcript text.

        Returns:
            float: GPA if found, else 0.0.
        """
        try:
            gpa_pattern = r"\bGPA\s*:\s*([0-4]\.\d{1,2})\b"
            match = re.search(gpa_pattern, raw_text)

            if match:
                gpa = float(match.group(1))
                logger.info(f"GPA found: {gpa}")
                return gpa

            logger.warning("No GPA found in the transcript.")
            return 0.0

        except Exception as e:
            logger.error(f"Error finding GPA in transcript: {e}")
            return 0.0

    def get_remaining_courses(self, required_courses):
        """
        Calculate the remaining courses that need to be completed.

        Args:
            required_courses (list): List of required course codes.

        Returns:
            list: List of remaining course codes.
        """
        try:
            remaining_courses = [
                course for course in required_courses
                if course not in self.completed_courses
            ]

            logger.info(f"Remaining courses: {remaining_courses}")
            return remaining_courses

        except Exception as e:
            logger.error(f"Error calculating remaining courses: {e}")
            return []

    def get_remaining_general_education_courses(self, gen_ed_requirements):
        """
        Calculate remaining general education courses.

        Args:
            gen_ed_requirements (dict): General education course requirements.

        Returns:
            dict: Remaining general education courses by category.
        """
        try:
            remaining_gen_ed = {}
            for category, courses in gen_ed_requirements.items():
                remaining = [
                    course for course in courses
                    if course not in self.completed_courses
                ]
                if remaining:
                    remaining_gen_ed[category] = remaining

            logger.info(f"Remaining general education courses: {remaining_gen_ed}")
            return remaining_gen_ed

        except Exception as e:
            logger.error(f"Error calculating remaining general education courses: {e}")
            return {}
