import logging
from sqlalchemy import text
from db import db
from config import MAJOR_TABLE_MAPPING, PREFIX_MAJOR_MAPPING, MAJOR_REQUIREMENTS



logger = logging.getLogger(__name__)

class CourseHandler:
    def __init__(self, major_name=None, course_code_prefix=None):
        """
        Initialize the CourseHandler using either the major name or course code prefix.
        Handles both main categories (majors) and sub-categories (sub-majors).
        """
        self.major_name = major_name
        self.major_id, self.sub_category = self.get_major_id_and_sub_category(major_name, course_code_prefix)

        if self.major_id is None:
            logger.error("No mapping found for the given major name or course code prefix.")
            raise ValueError("No mapping found for major name or course code prefix.")

        self.mapping = self._get_major_table_mapping()
        logger.info(f"Initialized CourseHandler for major ID: {self.major_id} with sub-category: {self.sub_category}")

    def get_major_id_and_sub_category(self, major_name=None, course_code_prefix=None):
        """
        Retrieve the major ID and sub-category based on the major name or prefix.
        If the major name matches a sub-category, treat it as the main major with the appropriate sub-category.
        """
        if major_name:
            for major_id, mapping in MAJOR_TABLE_MAPPING.items():
                if mapping.get("main_category") == major_name:
                    return major_id, None
                if "sub_categories" in mapping:
                    for sub_category in mapping["sub_categories"]:
                        if sub_category == major_name:
                            return major_id, sub_category

            for major_id, requirements in MAJOR_REQUIREMENTS.items():
                if "sub_categories" in requirements:
                    for sub_category in requirements["sub_categories"]:
                        if sub_category == major_name:
                            return major_id, sub_category

        if course_code_prefix:
            return PREFIX_MAJOR_MAPPING.get(course_code_prefix), None

        logger.error(f"No mapping found for major name: {major_name} or course code prefix: {course_code_prefix}")
        return None, None

    def _get_major_table_mapping(self):
        """Retrieve the mapping for the major or sub-category."""
        major_mapping = MAJOR_TABLE_MAPPING.get(self.major_id)
        if not major_mapping:
            logger.error(f"No mapping found for major ID: {self.major_id}")
            raise ValueError(f"No mapping found for major ID: {self.major_id}")

        
        if self.sub_category:
            sub_mapping = major_mapping.get("sub_categories", {}).get(self.sub_category)
            if not sub_mapping:
                logger.error(f"No mapping found for sub-category: {self.sub_category}")
                raise ValueError(f"No mapping found for sub-category: {self.sub_category}")
            return sub_mapping

        return major_mapping

    def query_core_courses(self):
        """Query core courses for the major or sub-category."""
        core_table = self.mapping.get("core")
        return self._execute_query(core_table)

    def query_elective_courses(self):
        """Query elective courses for the major or sub-category."""
        elective_table = self.mapping.get("elective")
        return self._execute_query(elective_table)

    def query_supporting_courses(self):
        """Query supporting courses for the major."""
        supporting_table = self.mapping.get("supporting")
        if not supporting_table:
            logger.info(f"No supporting courses found for major ID: {self.major_id}")
            return []

        return self._execute_query(supporting_table)

    

    def _execute_query(self, table_name):
        """Helper method to execute a query on the specified table."""
        if not table_name:
            logger.error("No table name provided for query execution.")
            return []

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

        if "sub_categories" in major_requirements and self.sub_category:
            sub_requirements = major_requirements["sub_categories"].get(self.sub_category, {})
            major_requirements = {**major_requirements, **sub_requirements} 
        defaults = {
            "core_courses_needed": 0,
            "elective_courses_needed": 0,
            "supporting_courses_needed": 0,
            "supporting_prefixes": [],
        }
        for key, default in defaults.items():
            if key not in major_requirements:
                major_requirements[key] = default

        logger.info(f"Retrieved requirements for major ID {self.major_id}: {major_requirements}")
        return major_requirements
