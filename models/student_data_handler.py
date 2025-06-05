import logging
import json
import re
from models.course_handler import CourseHandler
from models.general_education_handler import GeneralEducationHandler
from services.transcript_vision_service import TranscriptVisionService



logger = logging.getLogger(__name__)





class StudentDataHandler:
    def __init__(self, file_paths, major_name=None, transcript_service=None, raw_transcript_data=None):
        """
        Initialize the StudentDataHandler with necessary dependencies.

        Args:
            file_paths (str or list): The file path(s) to the uploaded transcript (PDF or images).
            major_name (str, optional): The name of the student's major.
            transcript_service (TranscriptVisionService, optional): The service for transcript parsing.
            raw_transcript_data (dict, optional): Pre-extracted transcript data to avoid redundant processing.
        """
        self.file_paths = file_paths if isinstance(file_paths, list) else [file_paths]
        self.major_name = major_name
        self.transcript_service = transcript_service if transcript_service else TranscriptVisionService()
        self.transcript_data = raw_transcript_data 
        try:
            self.course_handler = CourseHandler(major_name=major_name)
            self.general_education_handler = GeneralEducationHandler(major_name=major_name)

            self.required_courses = self.fetch_required_courses()

            if not self.transcript_data:
                logger.info("Extracting transcript data using TranscriptVisionService.")
                raw_transcript_response = self.transcript_service.extract_transcript_text(self.file_paths)
                self.transcript_data = self.parse_transcript_data(raw_transcript_response)

            if not self.transcript_data or 'error' in self.transcript_data:
                error_message = self.transcript_data.get('error', 'Unknown error')
                logger.error(f"Transcript data could not be extracted: {error_message}")
                raise ValueError(f"Transcript data could not be extracted: {error_message}")

        except Exception as e:
            logger.error(f"Error initializing StudentDataHandler: {e}")
            raise

    def fetch_required_courses(self):
        """
        Fetch required courses for the student's major.

        Returns:
            dict: A dictionary of required courses categorized as core, elective, supporting, and general education.
        """
        try:
            core_courses = self.course_handler.query_core_courses()
            elective_courses = self.course_handler.query_elective_courses()
            supporting_courses = self.course_handler.query_supporting_courses()
            general_education_courses = self.general_education_handler.query_general_education_courses()

            logger.info("Successfully fetched required courses.")

            logger.debug(f"Core Courses: {core_courses}")
            logger.debug(f"Elective Courses: {elective_courses}")
            logger.debug(f"Supporting Courses: {supporting_courses}")
            logger.debug(f"General Education Courses: {general_education_courses}")

            def get_course_code_and_name(course_row):
                logger.debug(f"Course row: {course_row}, Type: {type(course_row)}")

                if isinstance(course_row, dict):
                    keys = course_row.keys()
                    course_row_dict = course_row
                elif hasattr(course_row, '_fields'):  
                    keys = course_row._fields
                    course_row_dict = course_row._asdict()
                elif hasattr(course_row, '__dict__'): 
                    keys = vars(course_row).keys()
                    course_row_dict = vars(course_row)
                elif isinstance(course_row, tuple):
 
                    if len(course_row) >= 2:
                        course_code = course_row[0]
                        course_name = course_row[1]
                        return course_code.replace(' ', ''), course_name
                    else:
                        logger.error("Course tuple does not have enough elements.")
                        raise ValueError("Course tuple does not have enough elements.")
                else:
                    logger.error(f"Unsupported course_row type: {type(course_row)}")
                    raise ValueError("Unsupported course_row type")

                course_code = None
                for key in keys:
                    if re.search('code', key, re.IGNORECASE):
                        course_code = course_row_dict[key]
                        break

                course_name = None
                for key in keys:
                    if re.search('name', key, re.IGNORECASE):
                        course_name = course_row_dict[key]
                        break

                if not course_code or not course_name:
                    raise ValueError("Course code or name not found in course_row.")

                return course_code.replace(' ', ''), course_name

            def format_courses(courses):
                formatted_courses = []
                for c in courses:
                    try:
                        logger.debug(f"Processing course: {c}, Type: {type(c)}")
                        course_code, course_name = get_course_code_and_name(c)
                        formatted_courses.append(f"{course_code}: {course_name}")
                    except ValueError as e:
                        logger.warning(f"Skipping course due to error: {e}")
                return formatted_courses

            formatted_core_courses = format_courses(core_courses)
            formatted_elective_courses = format_courses(elective_courses)
            formatted_supporting_courses = format_courses(supporting_courses)
            formatted_general_education_courses = format_courses(general_education_courses)

            logger.debug(f"Formatted Core Courses: {formatted_core_courses}")
            logger.debug(f"Formatted Elective Courses: {formatted_elective_courses}")
            logger.debug(f"Formatted Supporting Courses: {formatted_supporting_courses}")
            logger.debug(f"Formatted General Education Courses: {formatted_general_education_courses}")

            return {
                "core_courses": formatted_core_courses,
                "elective_courses": formatted_elective_courses,
                "supporting_courses": formatted_supporting_courses,
                "general_education_courses": formatted_general_education_courses,
                "raw_core_courses": core_courses,
                "raw_elective_courses": elective_courses,
                "raw_supporting_courses": supporting_courses,
                "raw_general_education_courses": general_education_courses,
            }
        except Exception as e:
            logger.error(f"Error fetching required courses: {e}")
            raise

    def parse_transcript_data(self, raw_transcript_response):
        """
        Parses the raw transcript response from the TranscriptVisionService.

        Args:
            raw_transcript_response (str or dict): The raw response from the TranscriptVisionService.

        Returns:
            dict: Parsed transcript data as a dictionary.
        """
        try:
            if isinstance(raw_transcript_response, dict):
                return raw_transcript_response
            else:
                raw_transcript_response = raw_transcript_response.strip()
                if raw_transcript_response.startswith('```json'):
                    raw_transcript_response = raw_transcript_response.strip('```json').strip('```').strip()
                parsed_data = json.loads(raw_transcript_response)
                logger.debug(f"Parsed transcript data: {parsed_data}")
                return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing transcript data: {e}")
            logger.debug(f"Raw transcript response: {raw_transcript_response}")
            return {"error": "Failed to parse transcript data from the raw response."}

    def format_major_requirements(self):
        """
        Format the major requirements into a readable string for GPT prompts.

        Returns:
            str: The formatted major requirements.
        """
        try:
            major_requirements = self.course_handler.get_major_requirements()
            formatted_requirements = f"**Major Requirements for {self.major_name}:**\n"

            core_courses_needed = major_requirements.get('core_courses_needed', 0)
            if core_courses_needed:
                formatted_requirements += f"- Core Courses Needed: {core_courses_needed}\n"

            elective_courses_needed = major_requirements.get('elective_courses_needed', 0)
            if elective_courses_needed:
                formatted_requirements += f"- Elective Courses Needed: {elective_courses_needed}\n"

            supporting_courses_needed = major_requirements.get('supporting_courses_needed', 0)
            if supporting_courses_needed:
                formatted_requirements += f"- Supporting Courses Needed: {supporting_courses_needed}\n"
                supporting_prefixes = major_requirements.get('supporting_prefixes', [])
                if supporting_prefixes:
                    prefixes = ', '.join(supporting_prefixes)
                    formatted_requirements += f"  - Supporting Course Prefixes: {prefixes}\n"

            specializations = major_requirements.get('specializations', {})
            if specializations:
                formatted_requirements += "- Specializations:\n"
                for spec, count in specializations.items():
                    formatted_requirements += f"  - {spec}: {count} courses\n"

            gen_ed_requirements = major_requirements.get('general_education', {})
            if gen_ed_requirements:
                formatted_requirements += "\n**General Education Requirements:**\n"
                for key, value in gen_ed_requirements.items():
                    if isinstance(value, list):
                        courses = ', '.join(value)
                        formatted_requirements += f"- {key.replace('_', ' ').capitalize()}: {courses}\n"
                    else:
                        formatted_requirements += f"- {key.replace('_', ' ').capitalize()}: {value}\n"

            return formatted_requirements
        except Exception as e:
            logger.error(f"Error formatting major requirements: {e}")
            raise

    def format_required_courses(self):
        """
        Format the required courses into a readable string for the GPT prompt.

        Returns:
            str: The formatted required courses.
        """
        try:
            formatted_courses = ""
            for category, courses in self.required_courses.items():
                if not category.startswith('raw_'):  # Skip raw course lists
                    formatted_courses += f"**{category.replace('_', ' ').title()}**:\n"
                    for course in courses:
                        formatted_courses += f"- {course}\n"
                    formatted_courses += "\n"
            return formatted_courses.strip()
        except Exception as e:
            logger.error(f"Error formatting required courses: {e}")
            raise

    def format_transcript_data(self):
        """
        Format the raw transcript data into a clean, readable string for GPT prompts.
        Handles missing fields and ensures all course entries are processed correctly.

        Returns:
            str: The formatted transcript data as a string.
        """
        try:
            if not self.transcript_data:
                raise ValueError("Transcript data is missing or invalid.")

            if 'error' in self.transcript_data:
                error_message = self.transcript_data['error']
                formatted_data = [
                    "### Student Transcript\n",
                    f"#### Error: {error_message}\n"
                ]
                return "\n".join(formatted_data)

            formatted_data = []
            formatted_data.append("### Student Transcript\n")

            for semester, courses in self.transcript_data.items():
                formatted_data.append(f"#### {semester}:\n")
                semester_gpa = None
                for course in courses:
                    logger.debug(f"Processing course in {semester}: {course} (Type: {type(course)})")

                    if isinstance(course, dict) and "Semester gpa" in course:
                        gpa_value = course["Semester gpa"]
                        if gpa_value:  
                            try:
                                semester_gpa = float(gpa_value)
                            except ValueError:
                                logger.warning(f"Invalid Semester GPA '{gpa_value}' for {semester}. Skipping GPA.")
                        continue  
                    if isinstance(course, str):
                        try:
                            course = json.loads(course)
                        except json.JSONDecodeError:
                            logger.error(f"Unable to parse course data: {course}")
                            continue

                    if not isinstance(course, dict):
                        logger.error(f"Invalid course data type: {type(course)}. Expected dict.")
                        continue  
                    course_code = course.get('Course_code', '').strip()
                    course_name = course.get('Course_name', '').strip()
                    grade = course.get('GR', '').strip() or course.get('grade', '').strip()
                    gpa = course.get('gpa', '').strip()

                    if not course_code and not course_name:
                        logger.debug(f"Skipping entry with missing course code and name in {semester}.")
                        continue

                    course_details = (
                        f"  - **Course Code**: {course_code}\n"
                        f"    **Course Name**: {course_name}\n"
                        f"    **Grade**: {grade}\n"
                    )

                    if gpa:  
                        course_details += f"    **GPA**: {gpa}\n"

                    formatted_data.append(course_details)

                if semester_gpa is not None:
                    formatted_data.append(f"  **Semester GPA**: {semester_gpa:.2f}\n")

            return "\n".join(formatted_data)
        except Exception as e:
            logger.error(f"Error formatting transcript data: {e}")
            raise

    def prepare_gpt_input(self):
        """
        Prepare data for GPT prompt.

        Returns:
            dict: Data prepared for GPT input.
        """
        try:
            formatted_transcript_data = self.format_transcript_data()
            formatted_required_courses = self.format_required_courses()
            formatted_major_requirements = self.format_major_requirements()
            gpt_input = {
                "formatted_transcript_data": formatted_transcript_data,
                "required_courses": {
                    "core_courses": self.required_courses.get('core_courses', []),
                    "elective_courses": self.required_courses.get('elective_courses', []),
                    "supporting_courses": self.required_courses.get('supporting_courses', []),
                    "general_education_courses": self.required_courses.get('general_education_courses', []),
                },
                "formatted_required_courses": formatted_required_courses,
                "major_name": self.major_name,
                "major_requirements": formatted_major_requirements,
            }
            logger.info("Prepared GPT input.")
            logger.debug(f"GPT Input: {gpt_input}")
            return gpt_input
        except Exception as e:
            logger.error(f"Error preparing GPT input: {e}")
            raise
