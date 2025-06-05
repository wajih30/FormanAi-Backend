import logging
import json
from services.openai_services import generate_chatgpt_response
from models.student_data_handler import StudentDataHandler
from utils.prompt_builder import PromptHandler

logger = logging.getLogger(__name__)

class AdvisingService:
    """Handles advising functionality based on the student's academic progress."""

    def __init__(self, file_paths, major_name, sub_major=None):
        """
        Initialize the AdvisingService with student transcript files and major details.

        Args:
            file_paths (list): List of file paths (PDF or images).
            major_name (str): The student's major.
            sub_major (str): Optional sub-major name.
        """
        logger.info(f"Initializing AdvisingService for major: {major_name}, sub-major: {sub_major}")
        self.file_paths = file_paths
        self.major_name = major_name
        self.sub_major = sub_major

    def process_advising_request(self):
        """
        Process an advising request based on the student's transcript files.

        Returns:
            dict: The advising result or error message.
        """
        try:
            logger.info("Initializing StudentDataHandler.")
            student_data_handler = StudentDataHandler(
                file_paths=self.file_paths,
                major_name=self.major_name
            )
            logger.info("Transcript data successfully processed.")

            logger.info("Generating advising prompt.")
            prompt_handler = PromptHandler(student_data_handler=student_data_handler)
            advising_prompt = prompt_handler.build_advising_prompt()
            logger.debug(f"Generated advising prompt: {advising_prompt}")

            logger.info("Sending advising prompt to OpenAI API.")
            advising_response = generate_chatgpt_response(
                prompt=advising_prompt,
                max_tokens=3000,
                temperature=0.5
            )
            logger.debug(f"Raw GPT response: {advising_response}")

            if hasattr(advising_response, 'choices') and advising_response.choices:
                raw_content = advising_response.choices[0].message.content.strip()
                logger.debug(f"Raw GPT response content: {raw_content}")

                
                cleaned_content = self._clean_raw_content(raw_content)
                parsed_content = self._try_parse_json(cleaned_content)
                if parsed_content:
                    logger.info("Advising completed successfully.")
                    return {
                        "status": "success",
                        "advising_notes": parsed_content.get("advising_notes", []),
                        "raw_response": cleaned_content
                    }
                else:
                    logger.error("Failed to parse valid JSON from GPT response.")
                    return {
                        "status": "error",
                        "message": "Failed to parse the GPT response into a valid JSON format.",
                        "raw_response": cleaned_content
                    }

            logger.error("Invalid GPT response: No valid choices found.")
            return {"status": "error", "message": "GPT response is invalid or empty."}

        except ValueError as ve:
            logger.error(f"Validation error: {ve}")
            return {"status": "error", "message": str(ve)}

        except Exception as e:
            logger.error(f"Unexpected error during advising request: {e}", exc_info=True)
            return {"status": "error", "message": "An unexpected error occurred during the advising process."}

    def _clean_raw_content(self, raw_content):
        """
        Clean the raw GPT response content to remove any extra text or non-JSON content.
        
        Args:
            raw_content (str): The raw response content from GPT.
        
        Returns:
            str: The cleaned content containing only the JSON.
        """
        
        start_idx = raw_content.find("{")
        end_idx = raw_content.rfind("}") + 1
        cleaned_content = raw_content[start_idx:end_idx].strip()
        logger.debug(f"Cleaned content: {cleaned_content}")
        return cleaned_content

    def _try_parse_json(self, raw_content):
        """
        Try to directly parse JSON from the cleaned raw GPT response content.
        
        Args:
            raw_content (str): The raw response content from GPT.
        
        Returns:
            dict or None: Parsed JSON if valid, otherwise None.
        """
        try:
            
            parsed_json = json.loads(raw_content)
            logger.debug(f"Successfully parsed JSON: {parsed_json}")
            return parsed_json
        except json.JSONDecodeError as e:
            logger.error(f"Direct JSON parsing failed: {e}")
            return None
