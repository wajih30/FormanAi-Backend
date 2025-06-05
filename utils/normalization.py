

from config import MAJOR_TABLE_MAPPING

def get_major_id_from_name(major_name):
    for major_id, mapping in MAJOR_TABLE_MAPPING.items():
        if mapping.get("main_category") == major_name:
            return major_id
        
        for sub_category in mapping.get("sub_categories", {}).keys():
            if sub_category == major_name:
                return major_id
    return None

def normalize_course_code(course_code):
    
    return course_code.replace(" ", "").upper()

def normalize_course_name(course_name):
    return course_name.strip().title()