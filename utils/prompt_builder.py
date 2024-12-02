import logging
from models.student_data_handler import StudentDataHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PromptHandler:
    def __init__(self, student_data_handler: StudentDataHandler):
        """
        Initialize the PromptHandler with the StudentDataHandler instance.

        Args:
            student_data_handler (StudentDataHandler): Handles student data processing and transcript parsing.
        """
        self.student_data_handler = student_data_handler
        logger.info("PromptHandler initialized.")

    def build_degree_audit_prompt(self):
        """
        Build the degree audit prompt for GPT based on processed GPT input.

        Returns:
            str: The generated prompt for the degree audit.
        """
        gpt_input = self.student_data_handler.prepare_gpt_input()
        required_courses = gpt_input['required_courses']  # Now correctly accessing the dictionary
        major_requirements = gpt_input['major_requirements']

        logger.info("Preparing degree audit prompt with GPT input.")

        # Build the prompt sections for each course category
        core_courses_section = "\n".join([f"       - {course}" for course in required_courses.get('core_courses', [])])
        elective_courses_section = "\n".join([f"       - {course}" for course in required_courses.get('elective_courses', [])])
        supporting_courses_section = "\n".join([f"       - {course}" for course in required_courses.get('supporting_courses', [])])
        
        prompt = f"""
You are tasked with performing a detailed degree audit for a student.

**Instructions:**

1. **Normalize Course Codes**:
   - Remove any spaces in course codes before comparison (e.g., "CS 101" becomes "CS101").
   - Ensure all course codes are in a consistent format for accurate matching.

2. **Extract Passed Courses**:
   - From the transcript, extract all courses with passing grades: A, A-, B+, B, B-, C+, C, C-, D+, D.
   - Ignore courses with grades F, W, I, R, or missing grades.
   - For courses with an 'R' (Repeat) grade, consider only the most recent attempt with a passing grade.

   **Student Transcript Data:**
{gpt_input['formatted_transcript_data']}

3. **Compare Against Degree Requirements**:
   - Compare the student's passed courses with the required courses in each category.
   - Identify which requirements have been fulfilled and which courses are still needed for general and elective requirements.
   - Only include courses specified in the required courses lists.

{major_requirements}

   **Degree Requirements:**

     - **Core Courses**:
{core_courses_section}

     - **Elective Courses**:
{elective_courses_section}

     - **Supporting Courses**:
{supporting_courses_section}




4. **Important Notes**:
   - Do not double-count courses for multiple categories unless explicitly allowed.
   - Compulsory courses cannot be counted again in another category.
   - The student can take more than one course from the same department to fulfill a general education requirement, as long as the course codes are different.
   - For General Education requirements:
     - Muslims must take ISLM101; Christians must take CRST152.
     - Compulsory religious courses (URDU101, ISLM101, CRST152) do not count towards humanities requirements.

5. **Accuracy**:
   - Double-check all computations and categorizations.
   - Provide accurate and error-free results.
   donot add extra sentences out side of the output.

**Expected Output Format (in JSON)**:
{{
    "completed_courses": [
        {{"course_code": "COURSE_CODE", "course_name": "COURSE_NAME"}}
    ],
    "needed_courses": {{
        "general_courses": [
            {{
                "department": "DEPARTMENT",
                "courses_needed": NUMBER_OF_COURSES,
                "reason": "Explanation of why these courses are needed."
            }}
        ],
        "elective_courses": [
            {{
                "courses_needed": NUMBER_OF_COURSES,
                "reason": "Explanation of needed electives."
            }}
        ],
        "supporting_courses": [
            {{"course_code": "COURSE_CODE", "course_name": "COURSE_NAME"}}
        ],
        "core_courses": [
            {{"course_code": "COURSE_CODE", "course_name": "COURSE_NAME"}}
        ]
    }}
}}


"""
        logger.info("Degree audit prompt successfully generated.")
        return prompt.strip()

    def build_advising_prompt(self):
        """
        Build the advising prompt for GPT based on processed GPT input.

        Returns:
            str: The generated prompt for academic advising.
        """
        gpt_input = self.student_data_handler.prepare_gpt_input()
        required_courses = gpt_input['required_courses']  # Now correctly accessing the dictionary
        major_requirements = gpt_input['major_requirements']

        logger.info("Preparing advising prompt with GPT input.")

        # Build the prompt sections for each course category
        core_courses_section = "\n".join([f"       - {course}" for course in required_courses.get('core_courses', [])])
        elective_courses_section = "\n".join([f"       - {course}" for course in required_courses.get('elective_courses', [])])
        supporting_courses_section = "\n".join([f"       - {course}" for course in required_courses.get('supporting_courses', [])])
        general_education_courses_section = "\n".join([f"       - {course}" for course in required_courses.get('general_education_courses', [])])

        prompt = f"""
You are an academic advisor tasked with providing tailored advice to a student.

**Instructions:**

1. **Analyze Completed Courses**:
   - Consider only courses with passing grades: A, A-, B+, B, B-, C+, C, C-, D+, D.
   - Exclude courses currently being studied or with grades F, W, I, or missing grades.
   - For repeated courses ('R' grades), consider only the most recent attempt with a passing grade.
   - Normalize course codes by removing spaces for accurate comparison.

   **Student Transcript Data:**
{gpt_input['formatted_transcript_data']}

2. **Identify Remaining Requirements**:
   - Cross-reference the student's completed courses with the required courses in all categories.
   - Determine which courses are still needed for degree completion.
   - For General Education requirements, specify the departments and the number of courses needed.
   - Note any overlaps or exceptions, especially if courses from the student's major fulfill General Education requirements.

   **Degree Requirements:**

     - **Core Courses**:
{core_courses_section}

     - **Elective Courses**:
{elective_courses_section}

     - **Supporting Courses**:
{supporting_courses_section}

     - **General Education Courses**:
{general_education_courses_section}

     - **Major Requirements**:
{major_requirements}

3. **Provide Recommendations**:
   - Consider the student's strengths and weaknesses based on their academic history.
   - Offer advice on course load balancing between challenging and confidence-boosting subjects.
   - Recommend strategies for GPA improvement, such as retaking courses with low grades.

4. **Career Guidance**:
   - Suggest potential career paths where the student can excel, based on their academic strengths and interests.

5. **Finalize the Advising Plan**:
   - Ensure all advice is actionable and aligns with academic regulations.
   - Encourage the student to consult with their academic advisor for personalized guidance.
   - donot add extra sentences out side of the output.

**Expected Output Format (in JSON)**:
{{
    "advising_notes": [
        "Provide clear and concise advising notes here.",
        "Include recommendations on courses the user can study in the future, strategies,user strengths and weaknesses and potential career paths."
    ]
}}

Ensure the output is concise, well-structured, and formatted correctly.
"""
        logger.info("Advising prompt successfully generated.")
        return prompt.strip()
