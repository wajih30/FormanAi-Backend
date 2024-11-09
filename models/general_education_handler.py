import os
import logging
from dotenv import load_dotenv
from sqlalchemy import text
from db import db
from config import GENERAL_ED_REQUIREMENTS, MAJOR_NAME_MAPPING

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_path = os.path.join(os.path.dirname(__file__), 'general_education_handler.log')
handler = logging.FileHandler(log_path)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class GeneralEducationHandler:
    """Handles general education requirements for a given major."""

    def __init__(self, major_name=None, major_id=None):
        """Initialize with either major name or major ID."""
        if major_name:
            self.major_id = MAJOR_NAME_MAPPING.get(major_name)
            if self.major_id is None:
                raise ValueError(f"No mapping found for major name: {major_name}")
        elif major_id:
            self.major_id = major_id
        else:
            raise ValueError("Either major name or major ID must be provided.")

        self.general_ed_requirements = GENERAL_ED_REQUIREMENTS.get(self.major_id, {})
        logger.info(f"Initialized GeneralEducationHandler for major ID: {self.major_id}")

    def get_general_education_requirements(self):
        """Retrieve general education requirements."""
        requirements = {
            key: value for key, value in self.general_ed_requirements.items()
            if key in [
                'compulsory', 'required_compulsory', 'religious options', 'religious',
                'required_religious', 'humanities', 'humanities_options', 
                'social_sciences', 'social_sciences_options', 
                'science_lab', 'science_lab_options', 
                'mathematics', 'math_options', 
                'cs_require', 'additional_courses_option'
            ]
        }
        logger.info(f"General education requirements retrieved: {requirements}")
        return requirements

    def query_general_education_courses(self):
        """Query all general education courses from the database."""
        table_name = "bio_general_education"
        query = text(f"SELECT * FROM {table_name}")

        logger.info(f"Executing query on general education table: {table_name}")
        with db.session() as session:
            result = session.execute(query).fetchall()
            logger.info(f"Retrieved data from {table_name}: {result}")

        return result

    def fetch_required_courses_count(self):
        """Fetch required number of courses from each category."""
        required_counts = {
            "compulsory": self.general_ed_requirements.get("required_compulsory", 0),
            "religious": self.general_ed_requirements.get("required_religious", 0),
            "humanities": self.general_ed_requirements.get("humanities", 0),
            "social_sciences": self.general_ed_requirements.get("social_sciences", 0),
            "science_lab": self.general_ed_requirements.get("science_lab", 0),
            "mathematics": self.general_ed_requirements.get("mathematics", 0),
            "cs_require": self.general_ed_requirements.get("cs_require", 0),
            "additional_courses": self.general_ed_requirements.get("additional_courses_option", 0)
        }
        logger.info(f"Required counts retrieved: {required_counts}")
        return required_counts
