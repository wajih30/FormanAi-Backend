import logging
import json
from services.openai_services import generate_chatgpt_response
from models.student_data_handler import StudentDataHandler
from utils.prompt_builder import PromptHandler

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# File handler
log_file = 'degree_audit_service.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)


class DegreeAuditService:
    """Handles the degree audit functionality for a student's academic progress."""

    def __init__(self, file_paths, major_name):
        """
        Initialize the DegreeAuditService with the student's major and files.

        Args:
            file_paths (list): List of file paths (PDF or images).
            major_name (str): The student's major.
        """
        logger.info(f"Initializing DegreeAuditService for major: {major_name}")
        self.file_paths = file_paths
        self.major_name = major_name

    def perform_audit(self):
        """
        Perform a degree audit based on the student's transcript files.

        Returns:
            dict: The degree audit result or error message.
        """
        try:
            # Step 1: Initialize StudentDataHandler
            logger.info("Initializing StudentDataHandler.")
            student_data_handler = StudentDataHandler(
                file_paths=self.file_paths,
                major_name=self.major_name
            )
            logger.info("Transcript data successfully processed.")

            # Step 2: Generate degree audit prompt
            logger.info("Generating degree audit prompt.")
            prompt_handler = PromptHandler(student_data_handler=student_data_handler)
            degree_audit_prompt = prompt_handler.build_degree_audit_prompt()
            logger.debug(f"Generated degree audit prompt: {degree_audit_prompt}")

            # Step 3: Call OpenAI API for the audit response
            logger.info("Sending degree audit prompt to OpenAI API.")
            audit_response = generate_chatgpt_response(
                prompt=degree_audit_prompt,
                max_tokens=3000,
                temperature=0.0
            )
            logger.debug(f"Raw GPT response: {audit_response}")

            # Step 4: Parse and validate the GPT response
            if audit_response and hasattr(audit_response, "choices") and audit_response.choices:
                raw_content = audit_response.choices[0].message.content.strip()
                logger.debug(f"Raw GPT response content: {raw_content}")

                # Step 5: Extract JSON from response
                parsed_content = self._extract_json(raw_content)
                if parsed_content:
                    logger.info("Degree audit completed successfully.")
                    return {
                        "status": "success",
                        "audit_info": parsed_content,
                        "raw_response": raw_content
                    }
                else:
                    logger.error("Failed to extract valid JSON from GPT response.")
                    return {
                        "status": "error",
                        "message": "Failed to parse the GPT response into a valid JSON format.",
                        "raw_response": raw_content
                    }

            logger.error("Invalid GPT response: No valid choices found.")
            return {"status": "error", "message": "GPT response is invalid or empty."}

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            return {"status": "error", "message": str(ve)}

        except Exception as e:
            logger.error(f"Unexpected error during degree audit: {e}", exc_info=True)
            return {"status": "error", "message": "An unexpected error occurred during the degree audit process."}

    def _extract_json(self, raw_content):
        """
        Extract JSON from GPT response content.

        Args:
            raw_content (str): The raw response content.

        Returns:
            dict or None: Extracted JSON data if valid, otherwise None.
        """
        try:
            # Attempt direct JSON parsing
            return json.loads(raw_content)
        except json.JSONDecodeError:
            logger.warning("Direct JSON parsing failed. Attempting to extract JSON fragment.")
            start_idx = raw_content.find("{")
            end_idx = raw_content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                try:
                    json_fragment = raw_content[start_idx:end_idx + 1]
                    logger.debug(f"Extracted JSON fragment: {json_fragment}")
                    return json.loads(json_fragment)
                except json.JSONDecodeError as inner_error:
                    logger.error(f"Failed to parse JSON fragment: {inner_error}")
            return None
