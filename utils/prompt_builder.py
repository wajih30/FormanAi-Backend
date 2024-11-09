import logging
from models.student_data_handler import StudentDataHandler

# Configure the logger
logger = logging.getLogger(__name__)

class PromptHandler:
    def __init__(self, student_data_handler: StudentDataHandler):
        self.student_data_handler = student_data_handler
        logger.info("Initialized PromptHandler.")

    def build_degree_audit_prompt(self):
        """Build the degree audit prompt for GPT based on student's data."""
        student_data = self.student_data_handler.transcript_data
        completed_courses = student_data['completed_courses']
        required_courses = self.student_data_handler.fetch_required_courses()
        general_education_requirements = self.student_data_handler.general_education_handler.get_general_education_requirements()
        major_requirements = self.student_data_handler.course_handler.get_major_requirements()

        # Fetch the count of remaining general education requirements
        remaining_gen_ed_counts = self.student_data_handler.general_education_handler.fetch_required_courses_count()

        # Prepare the degree audit prompt
        prompt = f"""
        Conduct a degree audit for the following student:
        
        Completed Courses: {completed_courses}
        Required Core Courses: {required_courses['core_courses']}
        Required Elective Courses: {required_courses['elective_courses']}
        Required Supporting Courses: {required_courses['supporting_courses']}
        General Education Requirements: {general_education_requirements}
        Major Requirements: {major_requirements}
        Remaining General Education Counts: {remaining_gen_ed_counts}

        Please identify:
        1. Any remaining core courses that the student has not completed.
        2. The total number of electives needed and how many have been completed.
        3. General education courses that still need to be fulfilled based on the requirements.
        4. Any extra courses the student has studied beyond the requirements.
        5. Provide a summary of the degree progress and any recommendations for the next steps.
        """

        logger.info("Generated degree audit prompt for GPT.")
        return prompt

    def build_advising_prompt(self):
        """Build the advising prompt for GPT based on student's performance."""
        student_data = self.student_data_handler.transcript_data
        completed_courses = student_data['completed_courses']
        gpa = student_data.get('GPA', 0)
        cgpa = student_data.get('CGPA', 0)

        # Prepare the advising prompt
        prompt = f"""
        Analyze the following student's performance and provide course recommendations:
        
        Completed Courses: {completed_courses}
        Current GPA: {gpa}
        Current CGPA: {cgpa}

        Recommendations:
        1. Suggest easier courses (level < 300) if CGPA < 2.5, ideally one from each category.
        2. If CGPA >= 2.5, suggest degree-related courses with a focus on electives and core.
        3. If CGPA is high, recommend advanced courses (level >= 400).
        4. If the student is in their 6th semester, advise on potential career paths based on completed courses and suggest areas for improvement.

        Please provide detailed insights and recommendations.
        """

        logger.info("Generated advising prompt for GPT.")
        return prompt
