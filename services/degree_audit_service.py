import logging
import json
import re
from services.openai_services import generate_chatgpt_response
from models.student_data_handler import StudentDataHandler
from utils.prompt_builder import PromptHandler


logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),  
        logging.FileHandler("degree_audit_service.log")  
    ]
)

logger = logging.getLogger(__name__)

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
            logger.info("Initializing StudentDataHandler.")
            student_data_handler = StudentDataHandler(
                file_paths=self.file_paths,
                major_name=self.major_name
            )
            logger.info("Transcript data successfully processed.")

            logger.info("Generating degree audit prompt.")
            prompt_handler = PromptHandler(student_data_handler=student_data_handler)
            degree_audit_prompt = prompt_handler.build_degree_audit_prompt()
            logger.debug(f"Generated degree audit prompt: {degree_audit_prompt}")

            logger.info("Sending degree audit prompt to OpenAI API.")
            audit_response = generate_chatgpt_response(
                prompt=degree_audit_prompt,
                max_tokens=3000,
                temperature=0.0
            )
            logger.debug(f"Raw GPT response: {audit_response}")

            if audit_response and hasattr(audit_response, "choices") and audit_response.choices:
                raw_content = audit_response.choices[0].message.content.strip()
                logger.debug(f"Raw GPT response content: {raw_content}")

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
            
            code_block_regex = re.compile(r'```json\s*(\{.*\})\s*```', re.DOTALL)
            match = code_block_regex.search(raw_content)
            if match:
                json_content = match.group(1)
                logger.debug("Extracted JSON from code block.")
                return json.loads(json_content)
            
            
            json_start = raw_content.find('{')
            json_end = raw_content.rfind('}')
            if json_start != -1 and json_end != -1:
                json_content = raw_content[json_start:json_end+1]
                logger.debug("Extracted JSON from raw content.")
                return json.loads(json_content)

            #
            logger.error("No JSON content found in the response.")
            return None

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding failed: {e}")
            return None
