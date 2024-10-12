# utils/normalization.py
import re
from config import MAJOR_NAME_MAPPING

def get_major_id_from_name(major_name):
    """
    Maps the major name to the corresponding major_id using the MAJOR_NAME_MAPPING.
    
    Args:
    - major_name (str): The name of the major provided by the user.

    Returns:
    - int or None: The corresponding major_id, or None if the major_name is not found.
    """
    return MAJOR_NAME_MAPPING.get(major_name, None)


def normalize_course_code(course_code):
    """Normalize course code by removing spaces and converting to uppercase."""
    return re.sub(r'\s+', '', course_code).upper()

def normalize_course_name(course_name):
    """Normalize course name by removing extra spaces and converting to title case."""
    return re.sub(r'\s+', ' ', course_name).strip().title()
