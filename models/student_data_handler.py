import logging
import re
from utils.transcript_extraction import extract_course_data_from_text

# Set up logging
logger = logging.getLogger(__name__)

class StudentDataHandler:
    def __init__(self, transcript_data, major_id, major_name, sub_major=None):
        self.transcript_data = transcript_data
        self.major_id = major_id
        self.major_name = major_name
        self.sub_major = sub_major

        # Extract completed courses and initialize student profile
        self.completed_courses = self.extract_completed_courses()
        self.gpa = self.extract_gpa_from_transcript()

        logger.info(f"Initialized StudentDataHandler for Major: {major_name} (ID: {major_id})")

    def extract_completed_courses(self):
        """
        Extract completed courses from the raw transcript data.
        """
        # Assuming transcript_data is the raw text extracted from a transcript image or PDF
        extracted_data = extract_course_data_from_text(self.transcript_data)
        completed_courses = []

        for semester, courses in extracted_data.items():
            for course in courses:
                completed_courses.append(course['course_code'])

        logger.info(f"Extracted completed courses: {completed_courses}")
        return completed_courses

    def extract_gpa_from_transcript(self):
        """
        Extract the GPA directly from the transcript data.
        """
        # Using the method to find GPA from the raw transcript
        gpa = self._find_gpa_in_transcript(self.transcript_data)
        logger.info(f"Extracted GPA: {gpa}")
        return gpa

    def _find_gpa_in_transcript(self, raw_text):
        """
        Find GPA in the transcript using a regex pattern.
        """
        gpa_pattern = r"GPA\s*:\s*([0-4]\.[0-9]{1,2})"
        match = re.search(gpa_pattern, raw_text)
        if match:
            logger.info(f"GPA found: {match.group(1)}")
            return float(match.group(1))
        logger.warning("No GPA found in the transcript.")
        return 0.0
