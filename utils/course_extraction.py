import re

def extract_course_code(user_input):
    """
    Extracts the course code from user input.

    Args:
        user_input (str): The input string provided by the user.

    Returns:
        str: Extracted course code with no spaces, or None if not found.
    """
    match = re.search(r'\b([A-Z]{3,4}\s?\d{3}[A-Z]?)\b', user_input)
    return match.group(1).replace(" ", "") if match else None

def classify_query(user_input):
    """
    Classifies the user query based on detected keywords.

    Args:
        user_input (str): The input string provided by the user.

    Returns:
        list: A list of keywords found in the user input, or 'general' if no specific keyword is detected.
    """
    # Normalize user input by converting it to lowercase for matching
    normalized_input = user_input.lower()

    # Define query-related keywords
    keywords = {
        "prerequisite": ["prerequisite", "pre-req", "pre requisite", "required before"],
        "core": ["core course", "core", "mandatory", "required"],
        "research": ["research", "internship", "thesis", "capstone"],
        "elective": ["elective", "optional", "choose"],
        "supporting": ["supporting course", "additional", "minor"],
    }

    # Find matching keywords in user input
    found_keywords = []
    for key, variations in keywords.items():
        if any(variation in normalized_input for variation in variations):
            found_keywords.append(key)

    # If no keywords found, classify as 'general'
    return found_keywords if found_keywords else ["general"]
