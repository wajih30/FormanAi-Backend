import os
import logging
import base64
import openai
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance
from io import BytesIO
import json
import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)  # Ensure that debug logs are captured

class TranscriptVisionService:
    def __init__(self):
        """
        Initializes the TranscriptVisionService with OpenAI GPT-4 configuration.
        """
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.poppler_path = os.getenv("POPPLER_PATH")
        self.output_folder = "/tmp/processed_images"  
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)  
        if not self.poppler_path:
            logger.error("Poppler path is not set in the environment variables.")
            raise EnvironmentError("Poppler path is not set. Ensure it is configured correctly in the .env file.")
        if not openai.api_key:
            logger.error("OpenAI API key is not set in the environment variables.")
            raise EnvironmentError("OpenAI API key is missing. Please set it in your environment variables.")
        self.api_call_in_progress = False

    def validate_file_type(self, file_path):
        """
        Validates the file type based on its extension.
        """
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        if not any(file_path.lower().endswith(ext) for ext in valid_extensions):
            logger.error(f"Unsupported file type: {file_path}")
            raise ValueError(f"Invalid file type. Supported types are: {', '.join(valid_extensions)}")
        logger.info(f"Validated file type: {file_path}")

    def convert_pdf_to_images(self, file_path, dpi=300):
        """
        Converts a PDF file to a list of PIL Image objects with specified DPI.
        """
        try:
            images = convert_from_path(file_path, poppler_path=self.poppler_path, dpi=dpi)
            logger.info(f"Converted PDF to {len(images)} image(s) at {dpi} DPI.")
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise

    def encode_image(self, image):
        """
        Encodes a PIL Image to a base64 string.
        """
        try:
            buffer = BytesIO()
            image.save(buffer, format="JPEG")
            buffer.seek(0)
            encoded_image = base64.b64encode(buffer.read()).decode("utf-8")
            logger.debug("Image successfully encoded to base64.")
            return f"data:image/jpeg;base64,{encoded_image}"
        except Exception as e:
            logger.error(f"Error encoding image to base64: {e}")
            raise

    def split_image_into_sections(self, image, sections=4):
        """
        Splits an image into horizontal sections.

        Divides the image into 4 equal sections by default.
        """
        try:
            width, height = image.size
            section_height = height // sections
            split_images = []
            for i in range(sections):
                top = i * section_height
                bottom = (i + 1) * section_height if i < sections - 1 else height
                cropped_image = image.crop((0, top, width, bottom))
                split_images.append(cropped_image)
            logger.info(f"Split image into {sections} sections.")
            return split_images
        except Exception as e:
            logger.error(f"Error splitting image: {e}")
            raise

    def preprocess_image(self, image, image_index=0):
        """
        Preprocesses the image by improving clarity, turning it black and white, and increasing contrast.
        """
        try:
            
            width, height = image.size
            
            upscale_factor = 2
            image = image.resize((width * upscale_factor, height * upscale_factor), Image.LANCZOS)

            bw_image = image.convert("L")  
            contrast_enhancer = ImageEnhance.Contrast(bw_image)
            high_contrast_image = contrast_enhancer.enhance(1.0) 
            output_path = os.path.join(self.output_folder, f"processed_image_{image_index}.jpg")
            high_contrast_image.save(output_path, quality=100)  
            logger.info(f"Processed (upscaled, black and white with enhanced contrast) image saved at: {output_path}")
            return high_contrast_image, output_path
        except Exception as e:
            logger.error(f"Error during image preprocessing: {e}")
            raise

    def create_transcript_prompt(self):
        """
        Creates a refined prompt for the GPT-4 Vision model to extract transcript details.
        """
        return (
            "You are analyzing transcript images and must return data strictly in JSON format as follows:"
            "\n- The top-level keys in the JSON are the semesters (e.g., '2024 Spring')."
            "\n- For each semester, provide a list of courses and one GPA entry as shown in the example."
            "\n- Each course object should include:"
            "\n   'Course_code': Combine 'DEPT' and 'CRSE' columns (e.g., 'CSCS203'). Ignore and do not include the 'Sec' column at all. The 'Sec' column is the 4th column in the transcript and should never appear in the final data."
            "\n   'Course_name': Extract from the 'Title' column."
            "\n   'GR': Extract the grade from the 'GR' column only if it is a valid, finalized grade."
            "\n      Valid passing grades: A, A-, B+, B, B-, C+, C, C-, D+, D."
            "\n      Valid incomplete grades: F, W, R, I."
            "\n      If the course is ongoing or in progress and the GR column is empty or does not contain a final grade, then leave 'GR' empty and do not invent any grade."
            "\n      For repeated courses, if indicated, combine grades like 'F R', 'W R', 'D R', 'I R' as needed."
            "\n   Do not extract any letters that are not in the valid grades list. Ignore them if they appear."
            "\n- After listing all courses for the semester, include one object for 'gpa' extracted from the end of that term’s totals line. If no GPA is present or the semester is ongoing, 'gpa' should be empty."
            "\n- Valid 'DEPT' values: ['CSCS', 'COMP', 'BIOL', 'BIOT', 'BUSN', 'ECON', 'CHEM', 'PHYS', 'ENGL', 'GEOG', "
            "'HIST', 'MCOM', 'MATH', 'PHIL', 'PLSC', 'PSYC', 'SOCL', 'ISLM', 'URDU', 'LING', 'ENVR', 'EDUC', 'STAT', "
            "'PHRM', 'CRST', 'PKST']. Combine 'DEPT' + 'CRSE' to form 'Course_code'."
            "\n- Each course row: The 10th column contains the GR. Do not confuse columns. The 'Sec' column (4th column) must be completely ignored and never interpreted as a grade."
            "\n- Example output:"
            "\n```json"
            "\n{"
            "\n  '2024 Spring': ["
            "\n    {'Course_code': 'PKST101', 'Course_name': 'Pakistan Studies', 'GR': 'A'},"
            "\n    {'Course_code': 'SOCL102', 'Course_name': 'Sociology I', 'GR': 'B'},"
            "\n    {'gpa': '3.5'}"
            "\n  ],"
            "\n  '2024 Fall': ["
            "\n    {'Course_code': 'CSCS203', 'Course_name': 'Differential Equations', 'GR': 'A-'},"
            "\n    {'Course_code': 'PHYS101', 'Course_name': 'Physics I', 'GR': 'B+'},"
            "\n    {'gpa': '3.7'}"
            "\n  ]"
            "\n}"
            "\n```"
            "\nFollow these instructions carefully. Do not include any additional commentary outside the JSON."
        )


    def image_to_text(self, images):
        
        if self.api_call_in_progress:
            logger.warning("Attempt to call image_to_text while a call is already in progress.")
            return {"error": "API call already in progress."}
        self.api_call_in_progress = True

        try:
           
            encoded_images = [self.encode_image(image) for image in images]

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": self.create_transcript_prompt()  
                        },
                        *[
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": encoded_image  
                                }
                            }
                            for encoded_image in encoded_images 
                        ]
                    ]
                }
            ]

            logger.info("Sending transcript images to OpenAI GPT-4 for processing.")

            response = openai.chat.completions.create(
                model="gpt-4o",  
                messages=messages,
                max_tokens=4000,
                temperature=0  
            )

            extracted_data = response.choices[0].message.content.strip()
            logger.debug(f"Data extraction successful. Extracted data:\n{extracted_data}")

            return extracted_data
        except Exception as e:
            logger.error(f"Error during OpenAI Vision API processing: {e}")
            raise
        finally:
            self.api_call_in_progress = False



    def extract_transcript_text(self, file_paths):
        """
        Extracts transcript data from multiple file paths and processes images accordingly.

        Args:
            file_paths (list or str): List of file paths or a single file path to process.

        Returns:
            dict: Parsed transcript data or error message.
        """
        try:
            if not isinstance(file_paths, list):
                file_paths = [file_paths]

            all_images = []
            for file_path in file_paths:
                self.validate_file_type(file_path)
                images = (
                    self.convert_pdf_to_images(file_path)
                    if file_path.lower().endswith(".pdf")
                    else [Image.open(file_path)]
                )
                logger.info(f"Loaded {len(images)} image(s) from file: {file_path}")
                all_images.extend(images)

            processed_images = []
            for index, image in enumerate(all_images):
                split_images = self.split_image_into_sections(image, sections=3)
                for section_index, section in enumerate(split_images):
                    preprocessed_image, _ = self.preprocess_image(section, image_index=f"{index}_{section_index}")
                    processed_images.append(preprocessed_image)

            raw_data = self.image_to_text(processed_images)

            # Attempt to extract JSON from the response
            if raw_data.strip().startswith("```json"):
                # Extract JSON within code block
                json_match = re.search(r'```json\s*(\{.*\})\s*```', raw_data, re.DOTALL)
                if json_match:
                    raw_data = json_match.group(1)
                else:
                    logger.error("JSON code block not properly formatted.")
                    return {"error": "Failed to extract JSON from GPT response."}
            else:
                
                json_match = re.search(r'(\{.*\})', raw_data, re.DOTALL)
                if json_match:
                    raw_data = json_match.group(1)
                else:
                    logger.error("No JSON found in GPT response.")
                    return {"error": "Failed to extract JSON from GPT response."}

            try:
                parsed_data = json.loads(raw_data)
                logger.info("Parsed transcript data successfully.")
                return parsed_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT response into JSON: {e}")
                logger.debug(f"Raw Data: {raw_data}")
                return {"error": "Failed to parse GPT response into JSON format."}

        except Exception as e:
            logger.error(f"Error extracting transcript text: {e}", exc_info=True)
            return {"error": "Extraction failed"}
