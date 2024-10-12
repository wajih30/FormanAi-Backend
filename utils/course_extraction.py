import re

def extract_course_code(user_input):
    match = re.search(r'\b([A-Z]{4}\s?\d{3}[A-Z]?)\b', user_input)
    return match.group(1).replace(" ", "") if match else None

def classify_query(user_input):
    keywords = ["prerequisite", "core course", "research", "internship", "elective", "supporting course"]
    found_keywords = [keyword for keyword in keywords if keyword in user_input.lower()]
    return found_keywords if found_keywords else ["general"]