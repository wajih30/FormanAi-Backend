import logging
from config import MAJOR_NAME_MAPPING
from models.course_handler import CourseHandler
from models.general_education_handler import GeneralEducationHandler

from utils.course_extraction import extract_course_code, classify_query  # Make sure these functions are available

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('prompt_handler.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levellevel)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class PromptHandler:
    def __init__(self, major_id, sub_major=None):
        """
        Initialize the PromptHandler with the student's major ID and optional sub-major category.

        Args:
        - major_id (int): The ID of the student's major.
        - sub_major (str, optional): Sub-category of the major, if applicable.
        """
        self.major_id = major_id
        self.sub_major = sub_major
        self.major_name = MAJOR_NAME_MAPPING.get(major_id, "Unknown Major")
        self.course_handler = CourseHandler(major_id, sub_major)
        self.gen_ed_handler = GeneralEducationHandler(major_id)

    def build_course_prompt(self, course_type):
        """
        Build a structured prompt for core, elective, or supporting courses based on the course type.

        Args:
        - course_type (str): Type of courses to retrieve (e.g., 'core', 'elective', 'supporting').

        Returns:
        - str: A formatted prompt listing the courses for the specified type.
        """
        logger.info(f"Building course prompt for {course_type} courses.")
        courses = self.course_handler.get_courses(course_type)
        if not courses:
            return f"No {course_type} courses found for the {self.major_name} major."

        formatted_courses = self.course_handler.format_course_list(courses)
        return f"Here are the {course_type} courses for the {self.major_name} major:\n{formatted_courses}"

    def build_general_education_prompt(self):
        """
        Build a prompt to explain the general education requirements for the major.

        Returns:
        - str: A structured prompt listing the general education requirements and their status.
        """
        logger.info("Building general education prompt.")
        gen_ed_status = self.gen_ed_handler.get_all_gen_ed_courses()
        return self._format_gen_ed_prompt(gen_ed_status)

    def build_prerequisite_prompt(self, course_code):
        """
        Build a structured prompt to display the prerequisites for a given course.

        Args:
        - course_code (str): The course code for which to retrieve prerequisites.

        Returns:
        - str: A formatted prompt listing the prerequisites for the specified course.
        """
        logger.info(f"Building prerequisite prompt for course: {course_code}")
        prerequisites = self.course_handler.get_prerequisites(course_code)
        if not prerequisites:
            return f"No prerequisites found for {course_code}."

        prereq_list = "\n".join(prerequisites)
        return f"The following are the prerequisites for {course_code}:\n{prereq_list}"
 




    def build_manual_query_prompt(self, query_intent):
        """
        Build a structured prompt for manual user queries, such as course requirements, remaining courses, or GPA-related queries.

        Args:
        - query_intent (str): The user's intent or query.

        Returns:
        - str: A structured prompt for ChatGPT to generate responses.
        """
        logger.info(f"Building manual query prompt for intent: {query_intent}")
        query_intent = query_intent.lower()

        # Extract major and course information dynamically
        course_code = extract_course_code(query_intent)
        keywords_found = classify_query(query_intent)

        # Core course logic based on classified query keywords
        if "core course" in keywords_found:
            return self.build_course_prompt("core")
        elif "elective" in keywords_found:
            return self.build_course_prompt("elective")
        elif "supporting course" in keywords_found:
            return self.build_supporting_courses_prompt()
        elif "general education" in keywords_found or "gen ed" in keywords_found:
            return self.build_general_education_prompt()
        elif "prerequisite" in keywords_found and course_code:
            return self.build_prerequisite_prompt(course_code)
        elif "how many electives" in keywords_found:
            return self._build_remaining_electives_prompt()
        elif "how many general ed" in keywords_found:
            return self._build_remaining_gen_ed_prompt()
        elif "gpa" in keywords_found and course_code:
            return self._build_gpa_requirement_prompt(course_code)
        elif "research" in keywords_found or "internship" in keywords_found:
            return self._build_research_course_prompt()
        else:
            return "Sorry, I could not understand the query. Please provide more details or ask about core courses, electives, general education, or specific prerequisites."
    def build_transcript_analysis_prompt(self, transcript_data, remaining_courses, gen_ed_status, gpa=None, cgpa=None):
        """
        Construct a detailed prompt for analyzing the transcript and providing course recommendations.
        Pass the conditions for suggesting easier or harder courses based on performance directly to the prompt.

        Args:
        - transcript_data (dict): Extracted transcript data arranged by semester.
        - remaining_courses (dict): Dictionary containing remaining core, elective, and general education courses.
        - gen_ed_status (dict): General education course status (completed/unmet).
        - gpa (float, optional): GPA of the student.
        - cgpa (float, optional): CGPA of the student.

        Returns:
        - str: A formatted prompt to analyze the student's performance and suggest courses.
        """
        logger.info(f"Building transcript analysis prompt for {self.major_name}")

        completed_courses = transcript_data.get("completed_courses", [])
        bad_grades = ['D', 'D-', 'F']
        difficult_course_levels = [200, 300, 400]
        easy_course_levels = [100, 200, 300]
        bad_grade_threshold = 2.5  # GPA/CGPA threshold for easier course suggestions

        # Check for bad grades and lower GPA/CGPA
        has_bad_grades = any(course['grade'] in bad_grades for course in transcript_data['courses'])
        poor_performance = gpa < bad_grade_threshold or cgpa < bad_grade_threshold

        # Separate the remaining courses into easy and difficult categories
        easy_courses = self.course_handler.filter_courses_by_level(remaining_courses, easy_course_levels)
        difficult_courses = self.course_handler.filter_courses_by_level(remaining_courses, difficult_course_levels)

        prompt = f"The student has completed the following courses: {', '.join(completed_courses)}.\n"
        prompt += f"GPA: {gpa}, CGPA: {cgpa}.\n\n"
        prompt += f"Remaining Core Courses: {', '.join([course['course_code'] for course in remaining_courses['core_courses']])}\n"
        prompt += f"Remaining Elective Courses: {', '.join([course['course_code'] for course in remaining_courses['elective_courses']])}\n"
        if 'supporting_courses' in remaining_courses:
            prompt += f"Remaining Supporting Courses: {', '.join([course['course_code'] for course in remaining_courses['supporting_courses']])}\n"

        prompt += f"Remaining General Education Requirements: {gen_ed_status}\n\n"

        # Pass the decision logic as part of the prompt
        if has_bad_grades or poor_performance:
            logger.info("Suggesting easier courses due to poor performance or bad grades.")
            prompt += f"The student's GPA ({gpa}) and CGPA ({cgpa}) are below {bad_grade_threshold}, or they have bad grades ({', '.join(bad_grades)})."
            prompt += " Given their performance, suggest easier courses (levels 100-300) from the remaining courses and general education requirements.\n"
        else:
            logger.info("Suggesting a mix of core, elective, and general education courses.")
            prompt += f"The student's GPA ({gpa}) and CGPA ({cgpa}) are acceptable, and they have not received any bad grades ({', '.join(bad_grades)})."
            prompt += " Suggest a mix of core, elective, and general education courses for the next semester, including courses from levels 200-400 where applicable.\n"

        prompt += f"\nPlease analyze the student's academic progress and recommend up to 5 courses for the next semester based on the criteria provided."

        return prompt

    def build_degree_audit_prompt(self, transcript_data, course_tables):
        """
        Build a structured prompt for degree audit analysis.

        Args:
        - transcript_data (dict): Extracted transcript data arranged by semester.
        - course_tables (dict): Dictionary containing core, elective, and general education course tables.

        Returns:
        - str: A formatted prompt for degree audit analysis.
        """
        logger.info(f"Building degree audit prompt for {self.major_name}")
        prompt = f"Degree Audit for {self.major_name} Major\n\n"
        for semester, courses in transcript_data.items():
            prompt += f"{semester}:\n"
            for course in courses:
                prompt += f"  - {course['course_code']}: {course['course_name']} (Grade: {course['grade']})\n"

        prompt += "\nCross-check the student's completed courses against the following degree requirements:\n"
        for table_name, courses in course_tables.items():
            prompt += f"\n{table_name.capitalize()} Requirements:\n"
            for course in courses:
                prompt += f"  - {course['course_code']} - {course['course_name']} (Credits: {course['credits']})\n"

        prompt += "\nIdentify any missing requirements, courses to retake if grades are low, and remaining core, elective, or supporting courses."
        return prompt

    def _format_gen_ed_prompt(self, gen_ed_status):
        """
        Format the general education status into a readable prompt.

        Args:
        - gen_ed_status (dict): General education completion status for different categories.

        Returns:
        - str: A structured prompt to summarize the general education status.
        """
        logger.info(f"Formatting general education prompt for {self.major_name}.")
        prompt = f"General Education requirements for the {self.major_name} major:\n\n"
        for category, courses in gen_ed_status.items():
            completed = len(courses)
            prompt += f"{category.replace('_', ' ').capitalize()}: {completed} completed. Courses: {', '.join([c['course_code'] for c in courses])}\n"
        return prompt

    
    
    def build_supporting_courses_prompt(self):
        """
        Build a structured prompt to display the supporting courses required for the major.

        Returns:
        - str: A formatted prompt listing the supporting courses.
        """
        logger.info("Building supporting courses prompt.")
        supporting_courses = self.course_handler.get_supporting_courses()
        if not supporting_courses:
            return f"No supporting courses required for the {self.major_name} major."

        formatted_courses = self.course_handler.format_course_list(supporting_courses)
        return f"Here are the supporting courses for the {self.major_name} major:\n{formatted_courses}"

    def build_combined_major_prompt(self):
        """
        Build a structured prompt for majors with different sub-categories (e.g., Normal vs. Applied Psychology).

        Returns:
        - str: A formatted prompt with courses for different sub-categories of the major.
        """
        if self.sub_major:
            return self._build_sub_major_prompt()

        logger.info(f"Building combined major prompt for {self.major_name}.")
        prompt = f"List of all core, elective, and supporting courses for the {self.major_name} major:\n\n"
        core_prompt = self.build_course_prompt("core")
        elective_prompt = self.build_course_prompt("elective")
        supporting_prompt = self.build_supporting_courses_prompt()

        prompt += f"{core_prompt}\n\n{elective_prompt}\n\n{supporting_prompt}"
        return prompt

    

    

    def _build_sub_major_prompt(self):
        """
        Build a structured prompt for the specified sub-major category.

        Returns:
        - str: A formatted prompt with details for the sub-major category.
        """
        logger.info(f"Building sub-major specific prompt for {self.sub_major}.")
        if self.major_id == 17:  # Psychology
            if self.sub_major == "Applied":
                return self.build_course_prompt("applied_core") + "\n" + self.build_course_prompt("applied_elective")
            else:  # Normal Psychology
                return self.build_course_prompt("core") + "\n" + self.build_course_prompt("elective")

        if self.major_id == 19:  # Sociology
            if self.sub_major == "Sociology and Cult":
                return self.build_course_prompt("cult_core") + "\n" + self.build_course_prompt("cult_elective")
            else:  # Normal Sociology
                return self.build_course_prompt("core") + "\n" + self.build_course_prompt("elective")

        return f"No sub-major specific prompt available for {self.sub_major}."
    
    def _build_remaining_electives_prompt(self):
        """
        Build a prompt to check how many elective courses remain.

        Returns:
        - str: A prompt informing the user how many elective courses are remaining.
        """
        logger.info("Building remaining electives prompt.")
        remaining_electives = self.course_handler.get_remaining_electives()
        return f"You have {remaining_electives} elective courses remaining to complete."

    def _build_remaining_gen_ed_prompt(self):
        """
        Build a prompt to check how many general education courses remain.

        Returns:
        - str: A prompt informing the user how many general education courses are remaining.
        """
        logger.info("Building remaining general education courses prompt.")
        remaining_gen_ed = self.course_handler.get_remaining_gen_ed_courses()
        return f"You have {remaining_gen_ed} general education courses remaining to complete."

    def _build_gpa_requirement_prompt(self, course_code):
        """
        Build a prompt to check the GPA requirement for a specific course.

        Args:
        - course_code (str): The course code for which to retrieve the GPA requirement.

        Returns:
        - str: A prompt displaying the GPA requirement for the course.
        """
        logger.info(f"Building GPA requirement prompt for course: {course_code}")
        gpa_requirement = self.course_handler.get_gpa_requirement(course_code)
        min_cgpa = 2.0  # Default minimum CGPA for graduation
        return f"The minimum GPA required to take {course_code} is {gpa_requirement}. The minimum CGPA to graduate is {min_cgpa}."

    def _build_research_course_prompt(self):
        """
        Build a prompt for research or internship course requirements.

        Returns:
        - str: A prompt listing the research ors internship courses for the major.
        """
        logger.info("Building research/internship course prompt.")
        research_courses = self.course_handler.get_research_courses()
        if not research_courses:
            return "No research or internship courses found for your major."

        formatted_courses = "\n".join([f"{course['course_code']} - {course['course_name']}" for course in research_courses])
        return f"Here are the research or internship courses:\n{formatted_courses}"


    
    
