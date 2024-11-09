import logging
from sqlalchemy import text
from db import db
from utils.normalization import normalize_course_code
from config import MAJOR_TABLE_MAPPING, PREFIX_MAJOR_MAPPING, MAJOR_REQUIREMENTS

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CourseHandler:
    def __init__(self, major_name=None, course_code_prefix=None, sub_category=None):
        """Initialize the CourseHandler using either the major name or course code prefix."""
        self.major_name = major_name  # Store the major name
        self.major_id = self.get_major_id(major_name, course_code_prefix)
        if self.major_id is None:
            logger.error(f"No mapping found for major name or course code prefix.")
            raise ValueError(f"No mapping found for major name or course code prefix.")

        self.sub_category = sub_category
        self.mapping = self._get_major_table_mapping()
        logger.info(f"Initialized CourseHandler for major ID: {self.major_id} with sub-category: {self.sub_category}")

    def get_major_id(self, major_name=None, course_code_prefix=None):
        """Retrieve the major ID based on the major name or prefix."""
        if major_name:
            # Check for main categories
            for major_id, mapping in MAJOR_TABLE_MAPPING.items():
                if mapping.get("main_category") == major_name:
                    return major_id
                
                # Check for sub-categories
                if "sub_categories" in mapping:
                    for sub_category, sub_mapping in mapping["sub_categories"].items():
                        if sub_category == major_name:
                            return major_id  # Return the main ID for the sub-category
        
        if course_code_prefix:
            return PREFIX_MAJOR_MAPPING.get(course_code_prefix)
        
        logger.error(f"No mapping found for major name: {major_name} or course code prefix: {course_code_prefix}")
        return None

    def _get_major_table_mapping(self):
        """Retrieve the mapping for the major."""
        major_mapping = MAJOR_TABLE_MAPPING.get(self.major_id)
        if not major_mapping:
            logger.error(f"No mapping found for major ID: {self.major_id}")
            raise ValueError(f"No mapping found for major ID: {self.major_id}")

        if self.sub_category and "sub_categories" in major_mapping:
            sub_mapping = major_mapping["sub_categories"].get(self.sub_category)
            if not sub_mapping:
                logger.error(f"No mapping found for sub-category: {self.sub_category}")
                raise ValueError(f"No mapping found for sub-category: {self.sub_category}")
            return sub_mapping
        
        return major_mapping

    def query_core_courses(self, sub_category=None):
        """Query core courses for the major."""
        core_table = self._get_table("core", sub_category)
        return self._execute_query(core_table)

    def query_elective_courses(self, sub_category=None):
        """Query elective courses for the major."""
        elective_table = self._get_table("elective", sub_category)
        return self._execute_query(elective_table)

    def query_supporting_courses(self):
        """Query supporting courses for the major."""
        supporting_table = self.mapping.get("supporting")
        if not supporting_table:
            logger.info(f"No supporting courses found for major ID: {self.major_id}")
            return []  # Return an empty list if no supporting table exists

        return self._execute_query(supporting_table)

    def query_prerequisites(self):
        """Query prerequisites for the major."""
        prerequisites_table = self.mapping.get("prerequisites")
        if not prerequisites_table:
            logger.info(f"No prerequisite table found for major ID: {self.major_id}")
            return []  # Return an empty list if no prerequisites exist

        return self._execute_query(prerequisites_table)

    def _get_table(self, table_type, sub_category=None):
        """Helper method to get the correct table based on type and optional sub-category."""
        if sub_category and "sub_categories" in self.mapping:
            table = self.mapping["sub_categories"].get(sub_category, {}).get(table_type)
            if not table:
                logger.error(f"No {table_type} table mapping found for sub-category: {sub_category}")
                raise ValueError(f"No {table_type} table mapping found for sub-category: {sub_category}")
            return table
        return self.mapping.get(table_type)

    def _execute_query(self, table_name):
        """Helper method to execute a query on the specified table."""
        try:
            logger.info(f"Executing query on table: {table_name}")
            query = text(f"SELECT * FROM {table_name}")

            with db.session() as session:
                result = session.execute(query).fetchall()
                if not result:
                    logger.warning(f"No data found in table: {table_name}")
                else:
                    logger.info(f"Retrieved data from {table_name}: {result}")

            return result
        except Exception as e:
            logger.error(f"Error executing query on table {table_name}: {e}")
            return []

    def get_major_requirements(self):
        """Retrieve the requirements for the major based on the major ID."""
        major_requirements = MAJOR_REQUIREMENTS.get(self.major_id)

        if not major_requirements:
            logger.error(f"No requirements found for major ID: {self.major_id}")
            raise ValueError(f"No requirements found for major ID: {self.major_id}")

        # Check if the major has subcategories
        if 'sub_categories' in major_requirements:
            # Handle Applied Psychology subcategory
            if self.major_name == "Applied Psychology":
                applied_psych_requirements = major_requirements['sub_categories'].get("Applied Psychology", {})
                required_electives = applied_psych_requirements.get("applied_elective_courses_needed", 0)
                major_requirements['elective_courses_needed'] = required_electives

            # Handle Sociology and Culture subcategory
            elif self.major_name == "Sociology and Culture":
                sociology_cult_requirements = major_requirements['sub_categories'].get("Sociology and Culture", {})
                required_electives = sociology_cult_requirements.get("cult_elective_courses_needed", 0)
                major_requirements['elective_courses_needed'] = required_electives

        logger.info(f"Retrieved requirements for major ID {self.major_id}: {major_requirements}")
        return major_requirements
