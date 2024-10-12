# utils/normalization.py
import re
from config import MAJOR_NAME_MAPPING

def get_major_id_from_name(major_name):
    """
    Maps the major name (or sub-major) to the corresponding major_id using the MAJOR_NAME_MAPPING.

    Args:
        major_name (str): The name of the major provided by the user.

    Returns:
        int or None: The corresponding major_id, or None if the major_name is not found.
    """
    normalized_major_name = major_name.strip().title()  # Normalize major name for matching
    major_data = MAJOR_NAME_MAPPING.get(normalized_major_name)

    if isinstance(major_data, dict) and "id" in major_data:
        return major_data["id"]
    return major_data  # Will return None if the name is not found

def normalize_course_code(course_code):
    """
    Normalize course code by removing spaces, handling dashes, and converting to uppercase.

    Args:
        course_code (str): The course code to normalize.

    Returns:
        str: The normalized course code.
    """
    return re.sub(r'[\s\-]+', '', course_code).upper()

def normalize_course_name(course_name):
    """
    Normalize course name by removing extra spaces and converting to title case.

    Args:
        course_name (str): The course name to normalize.

    Returns:
        str: The normalized course name.
    """
    return re.sub(r'\s+', ' ', course_name).strip().title()
