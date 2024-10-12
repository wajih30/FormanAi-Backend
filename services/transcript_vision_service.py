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

class TranscriptVisionService:
    """Service to handle transcript extraction using GPT-4 Vision API for both PDF and image files."""

    def extract_transcript_data(self, transcript_file):
        """
        Extract transcript data from a given file (PDF or image).

        Args:
        - transcript_file: Uploaded transcript file (PDF or image).

        Returns:
        - dict: Extracted data or error message.
        """
        try:
            # Check the file type and process accordingly
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

            extracted_data = self._extract_data_from_images(images)
            return extracted_data
        except Exception as e:
            logger.error(f"Error extracting transcript data: {e}")
            return {"error": f"Failed to process transcript: {str(e)}"}

    def _convert_pdf_to_images(self, pdf_file):
        """
        Convert PDF to images using pdf2image.

        Args:
        - pdf_file: PDF file uploaded by the user.

        Returns:
        - list: List of images.
        """
        try:
            logger.info("Converting PDF to images using pdf2image.")
            images = convert_from_bytes(pdf_file.read())
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            return []

    def _extract_data_from_images(self, images):
        """
        Process each image with GPT-4 Vision API to extract academic information.

        Args:
        - images (list): List of images (from PDF or directly uploaded).

        Returns:
        - dict: Extracted academic information.
        """
        extracted_data = {}

        for i, image in enumerate(images):
            try:
                logger.info(f"Processing image {i + 1} with GPT-4 Vision API.")
                temp_image_path = f"temp_image_{i}.png"
                image.save(temp_image_path)  # Save temporarily to send to API

                with open(temp_image_path, "rb") as img_file:
                    response = openai.Image.create(
                        file=img_file,
                        prompt=("Extract the academic information from this transcript page, "
                                "including course codes, course names, credits, GPA, CGPA, "
                                "and categorize by semester (Spring, Summer, Fall, Winter).")
                    )
                    extracted_data.update(self._parse_gpt4_response(response))
                    
                # Cleanup: Remove the temporary image file after processing
                os.remove(temp_image_path)

            except Exception as e:
                logger.error(f"Error processing image {i + 1}: {e}")
                continue

        return extracted_data

    def _parse_gpt4_response(self, response):
        """
        Parse the response from GPT-4 Vision API to extract academic information.

        Args:
        - response (dict): Response from GPT-4 Vision API.

        Returns:
        - dict: Parsed academic information (course codes, names, credits, GPA, CGPA, etc.).
        """
        logger.info("Parsing GPT-4 Vision API response.")
        parsed_data = {}

        try:
            courses = response.get('courses', [])
            normalized_courses = []

            for course in courses:
                normalized_course_code = normalize_course_code(course['course_code'])
                normalized_course_name = normalize_course_name(course['course_name'])

                normalized_courses.append({
                    'course_code': normalized_course_code,
                    'course_name': normalized_course_name,
                    'credits': course.get('credits', 'N/A')
                })

            parsed_data['completed_courses'] = normalized_courses
            
            # Improved handling for GPA and CGPA
            parsed_data['GPA'] = response.get('gpa', 'N/A') if 'gpa' in response else 'Not provided'
            parsed_data['CGPA'] = response.get('cgpa', 'N/A') if 'cgpa' in response else 'Not provided'
            
            parsed_data['semesters'] = response.get('semesters', {})

            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing GPT-4 Vision response: {e}")
            return {}

