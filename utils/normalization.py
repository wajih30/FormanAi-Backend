# utils/normalization.py
import re
# utils/normalization.py
from config import MAJOR_NAME_MAPPING as MAJOR_NAME_MAPPING
# utils/normalization.py
from config import MAJOR_TABLE_MAPPING

def get_major_id_from_name(major_name):
    """Get the major ID based on the major name."""
    for major_id, mapping in MAJOR_TABLE_MAPPING.items():
        if mapping.get("main_category") == major_name:
            return major_id
        # Check for sub-category names if present
        for sub_category in mapping.get("sub_categories", {}).keys():
            if sub_category == major_name:
                return major_id
    return None

def normalize_course_code(course_code):
    """Normalize the course code by stripping spaces and converting to upper case."""
    return course_code.replace(" ", "").upper()

def normalize_course_name(course_name):
    """Normalize the course name by stripping spaces and converting to title case."""
    return course_name.strip().title()