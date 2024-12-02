import re
import logging

logger = logging.getLogger(__name__)

def extract_gpa_from_text(raw_text):
    """
    Extract the GPA from the raw transcript text as a fallback.
    
    Args:
        raw_text (str): The input transcript text.

    Returns:
        float: GPA if found, otherwise 0.0.
    """
    try:
        gpa_pattern = r"\bGPA\s*:\s*([0-4]\.\d{1,2})\b"
        match = re.search(gpa_pattern, raw_text)

        if match:
            gpa = float(match.group(1))
            logger.info(f"GPA extracted: {gpa}")
            return gpa

        logger.warning("GPA not found in the transcript.")
        return 0.0

    except Exception as e:
        logger.error(f"Error extracting GPA: {e}")
        return 0.0
