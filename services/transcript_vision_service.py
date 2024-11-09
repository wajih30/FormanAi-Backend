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
        """Extract transcript data from a given file (PDF or image)."""
        try:
            if not hasattr(transcript_file, 'name'):
                logger.error("Uploaded file has no filename attribute.")
                return {"error": "Invalid file uploaded."}

            file_ext = transcript_file.name.split('.')[-1].lower()
            logger.info(f"Uploaded file extension: {file_ext}")

            if file_ext == 'pdf':
                logger.info("Processing transcript PDF file.")
                images = self._convert_pdf_to_images(transcript_file)
                if not images:
                    logger.error("No pages found in the PDF.")
                    return {"error": "PDF has no pages."}
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
        """Convert PDF to images using pdf2image."""
        try:
            logger.info("Converting PDF to images using pdf2image.")
            return convert_from_bytes(pdf_file.read())
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            # Return an empty list if the PDF structure is invalid
            raise Exception("Invalid PDF structure")  # Raise a custom exception for the test to catch

    def _extract_data_from_images(self, images):
        """Process each image using GPT-4 Vision API to extract academic information."""
        extracted_data = {
            "completed_courses": [], 
            "failed_courses": [],  
            "GPA": "N/A", 
            "CGPA": "N/A", 
            "semesters": {}
        }

        for i, image in enumerate(images):
            temp_image_path = f"temp_image_{i}.png"
            try:
                logger.info(f"Processing image {i + 1} with GPT-4 Vision API.")
                image.save(temp_image_path)

                with open(temp_image_path, "rb") as img_file:
                    response = openai.Image.create(
                        file=img_file,
                        prompt=self._build_vision_prompt()  
                    )
                    extracted_data.update(self._parse_gpt4_response(response))

            except Exception as e:
                logger.error(f"Error processing image {i + 1}: {e}")
            finally:
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)  # Ensure cleanup

        return extracted_data

    def _build_vision_prompt(self):
        """Build the prompt to guide GPT-4 Vision on how to extract relevant transcript information."""
        return (
            "You are analyzing a university transcript. Please extract the following details:\n"
            "- Semester name and year (e.g., Fall 2021, Spring 2022)\n"
            "- For each course, extract the course code, course name, credits, and grade\n"
            "- GPA and CGPA, if present, for each semester\n"
            "- Include courses with failing grades (F) in the failed courses list.\n"
            "Return the data in JSON format, organized by semester."
        )

    def _parse_gpt4_response(self, response):
        """Parse the response from GPT-4 Vision API to extract academic information."""
        logger.info("Parsing GPT-4 Vision API response.")
        parsed_data = {
            "completed_courses": [], 
            "failed_courses": [], 
            "GPA": "N/A", 
            "CGPA": "N/A", 
            "semesters": {}
        }

        try:
            # Accessing the data returned from the response
            courses = response.get('data', {}).get('courses', [])
            for course in courses:
                normalized_course_code = normalize_course_code(course.get('course_code', ''))
                normalized_course_name = normalize_course_name(course.get('course_name', ''))
                grade = course.get('grade', 'N/A')
                credits = course.get('credits', 'N/A')

                course_data = {
                    'course_code': normalized_course_code,
                    'course_name': normalized_course_name,
                    'credits': credits,
                    'grade': grade
                }

                if grade == "F":
                    parsed_data['failed_courses'].append(course_data)
                else:
                    parsed_data['completed_courses'].append(course_data)

            parsed_data['GPA'] = response.get('data', {}).get('gpa', 'N/A')
            parsed_data['CGPA'] = response.get('data', {}).get('cgpa', 'N/A')
            parsed_data['semesters'] = response.get('data', {}).get('semesters', {})

        except Exception as e:
            logger.error(f"Error parsing GPT-4 Vision response: {e}")

        return parsed_data
