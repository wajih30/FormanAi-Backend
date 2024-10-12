# utils/transcript_extraction.py

import re

def extract_course_data_from_text(raw_text):
    """
    Extract course codes, names, and grades from the raw text using regex.

    Args:
        raw_text (str): Text extracted from transcript.

    Returns:
        dict: Dictionary containing extracted data arranged by semesters.
    """
    # Regex pattern to match course code (e.g., CS101), course name, and grade (A, B+, etc.)
    course_pattern = r"([A-Za-z]{2,4}\d{3})\s+([\w\s,&-]+?)\s+(A|A-|B\+|B|B-|C\+|C|C-|D\+|D|F)"

    # Regex pattern to detect semester labels (e.g., "Semester 1", "Fall 2022", "Spring 2021")
    semester_pattern = r"(Semester\s+\d+|Fall\s+\d{4}|Spring\s+\d{4}|Winter\s+\d{4}|Summer\s+\d{4})"

    # Initialize the transcript data dictionary
    transcript_data = {}
    current_semester = None

    # Split the raw text into lines and process each line
    for line in raw_text.splitlines():
        line = line.strip()  # Remove any extra spaces or newlines

        # Check if the line matches a semester pattern
        semester_match = re.match(semester_pattern, line, re.IGNORECASE)
        if semester_match:
            current_semester = semester_match.group(1)
            transcript_data[current_semester] = []  # Initialize a list for the semester

        # Check if the line matches a course pattern
        course_match = re.match(course_pattern, line)
        if course_match and current_semester:
            course_code, course_name, grade = course_match.groups()
            transcript_data[current_semester].append({
                "course_code": course_code.strip(),
                "course_name": course_name.strip().title(),
                "grade": grade.strip()
            })

    return transcript_data
