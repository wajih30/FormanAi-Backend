# utils/query_parser.py
import re

def parse_query(user_input):
    """
    Parse the user query to identify the intent, course code, and any other entities.

    Args:
        user_input (str): The raw input from the user.

    Returns:
        dict: Dictionary containing identified course codes, intent, and any other relevant data.
    """
    # Normalize the user input for consistent matching
    normalized_input = user_input.lower().strip()

    # Intent Mapping: Define the potential intents and their associated keywords
    intent_mapping = {
        "prerequisite": r"\b(pre[\s-]?req|prerequisite|prereq)\b",
        "core course": r"\b(core course|main courses|required courses)\b",
        "elective": r"\b(elective|optional courses)\b",
        "research requirements": r"\b(research|internship|project)\b",
        "gpa required": r"\b(gpa|min\.? gpa|minimum gpa)\b",
        "credits required": r"\b(credits|credit hours|cr\.? hrs)\b"
    }

    # Detect course code using a flexible regex pattern
    course_code_pattern = r'\b([A-Z]{4})\s?(\d{3}[A-Z]?)\b'
    course_code_match = re.search(course_code_pattern, normalized_input, flags=re.IGNORECASE)
    course_code = course_code_match.group(0).replace(" ", "").upper() if course_code_match else None

    # Determine the query intent using a single loop through the intent mappings
    query_intent = None
    for intent, pattern in intent_mapping.items():
        if re.search(pattern, normalized_input):
            query_intent = intent
            break

    # Construct the result dictionary with enhanced error handling
    result = {
        "course_code": course_code,
        "query_intent": query_intent,
        "original_query": user_input,
        "parsed_status": "success" if query_intent or course_code else "unrecognized query"
    }

    # Handle edge case if neither intent nor course code is found
    if result["parsed_status"] == "unrecognized query":
        result["error_message"] = "Unable to identify intent or course code from your query."

    return result
