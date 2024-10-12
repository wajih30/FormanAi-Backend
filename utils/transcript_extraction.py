# utils/transcript_extraction.py

import re

def extract_course_data_from_text(raw_text):
    """
    Extract course codes, names, and grades from the raw text using regex.

    Args:
    - raw_text (str): Text extracted from transcript.

    Returns:
    - dict: Dictionary containing extracted data arranged by semesters.
    """
    # Regex pattern to match course code (e.g., CS101), course name, and grade (A, B+, etc.)
    course_pattern = r"([A-Za-z]+\d{3})\s+([A-Za-z\s]+)\s+(A|B\+|B|C\+|C|D\+|D|F)"
    extracted_courses = re.findall(course_pattern, raw_text)

    # Regex pattern to detect semester labels (e.g., "Semester 1", "Fall 2022")
    semester_pattern = r"(Semester\s+\d+|Fall\s+\d+|Spring\s+\d+)"

    # Initialize transcript data dictionary
    transcript_data = {}
    current_semester = None

    for line in raw_text.splitlines():
        # Check if the line matches a semester pattern
        semester_match = re.match(semester_pattern, line)
        if semester_match:
            current_semester = semester_match.group(1)
            transcript_data[current_semester] = []
        else:
            # Check for a course match
            course_match = re.match(course_pattern, line)
            if course_match and current_semester:
                course_code, course_name, grade = course_match.groups()
                transcript_data[current_semester].append({
                    "course_code": course_code,
                    "course_name": course_name,
                    "grade": grade
                })

    return transcript_data
