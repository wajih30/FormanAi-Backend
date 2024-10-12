import logging
from PIL import Image
from pdf2image import convert_from_bytes
import openai
import os
from utils.normalization import normalize_course_code, normalize_course_name

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('transcript_vision_service.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TranscriptVisionService:
    """Service to handle transcript extraction using GPT-4 Vision API for both PDF and image files."""

    def extract_transcript_data(self, transcript_file):
        """
        Extract transcript data from a given file (PDF or image).
        
        Args:
            transcript_file: Uploaded transcript file (PDF or image).

        Returns:
            dict: Extracted data or error message.
        """
        try:
            file_ext = transcript_file.filename.split('.')[-1].lower()

            if file_ext == 'pdf':
                logger.info("Processing transcript PDF file.")
                images = self._convert_pdf_to_images(transcript_file)
            elif file_ext in ['jpg', 'jpeg', 'png']:
                logger.info("Processing transcript image file.")
                images = [Image.open(transcript_file)]
            else:
                logger.error(f"Unsupported file format: {file_ext}")
                return {"error": "Unsupported file format. Please upload a PDF, JPG, or PNG file."}

            return self._extract_data_from_images(images)
        except Exception as e:
            logger.error(f"Error extracting transcript data: {e}")
            return {"error": f"Failed to process transcript: {str(e)}"}

    def _convert_pdf_to_images(self, pdf_file):
        """
        Convert PDF to images using pdf2image.

        Args:
            pdf_file: PDF file uploaded by the user.

        Returns:
            list: List of images or an empty list if conversion fails.
        """
        try:
            logger.info("Converting PDF to images using pdf2image.")
            return convert_from_bytes(pdf_file.read())
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []

    def _extract_data_from_images(self, images):
        """
        Process each image using GPT-4 Vision API to extract academic information.

        Args:
            images (list): List of images (from PDF or directly uploaded).

        Returns:
            dict: Extracted academic information.
        """
        extracted_data = {"completed_courses": [], "GPA": "N/A", "CGPA": "N/A", "semesters": {}}

        for i, image in enumerate(images):
            try:
                logger.info(f"Processing image {i + 1} with GPT-4 Vision API.")
                temp_image_path = f"temp_image_{i}.png"
                image.save(temp_image_path)

                with open(temp_image_path, "rb") as img_file:
                    response = openai.Image.create(
                        file=img_file,
                        prompt=(
                            "Extract academic information including course codes, course names, credits, "
                            "GPA, CGPA, and organize it by semesters (Spring, Summer, Fall, Winter)."
                        )
                    )
                    extracted_data = self._parse_gpt4_response(response)

                os.remove(temp_image_path)  # Clean up temporary image file
            except Exception as e:
                logger.error(f"Error processing image {i + 1}: {e}")

        return extracted_data

    def _parse_gpt4_response(self, response):
        """
        Parse the response from GPT-4 Vision API to extract academic information.

        Args:
            response (dict): Response from GPT-4 Vision API.

        Returns:
            dict: Parsed academic information (course codes, names, credits, GPA, CGPA, etc.).
        """
        logger.info("Parsing GPT-4 Vision API response.")
        parsed_data = {"completed_courses": [], "GPA": "N/A", "CGPA": "N/A", "semesters": {}}

        try:
            courses = response.get('courses', [])
            for course in courses:
                normalized_course_code = normalize_course_code(course.get('course_code', ''))
                normalized_course_name = normalize_course_name(course.get('course_name', ''))

                parsed_data['completed_courses'].append({
                    'course_code': normalized_course_code,
                    'course_name': normalized_course_name,
                    'credits': course.get('credits', 'N/A')
                })

            parsed_data['GPA'] = response.get('gpa', 'N/A')
            parsed_data['CGPA'] = response.get('cgpa', 'N/A')
            parsed_data['semesters'] = response.get('semesters', {})

        except Exception as e:
            logger.error(f"Error parsing GPT-4 Vision response: {e}")

        return parsed_data
