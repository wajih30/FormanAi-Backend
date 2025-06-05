import logging
from models.student_data_handler import StudentDataHandler


logger = logging.getLogger(__name__)




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
        required_courses = gpt_input['required_courses']  
        major_requirements = gpt_input['major_requirements']

        logger.info("Preparing degree audit prompt with GPT input.")

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
   - for gen ed for each department if any of the coursse code the student has studied is starting from the course code that is mentioned in the courses list then that requirement would be counted as completed look for completed courses through students grade and the course_code of that course studied and then the course code that is given in the courses list u need to check that.

{major_requirements}

   **Degree Requirements:**

     - **Core Courses**:
     Course_code:     course name:

     (which is needed
     compare the 
     completed courses) 
{core_courses_section}

     - **Elective Courses**:
      Course_code:     course name:
     
     (which is needed
     compare the 
     completed courses) 
{elective_courses_section}

     - **Supporting Courses**:
      Course_code:     course name:
     
     (which is needed
     compare the 
     completed courses) 
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
   "Provide the JSON within a code block tagged as JSON.\n"

   these are all the course codes prefixes for each major :
   # Computer Science and IT
    "CSCS": 1,  # Computer Science
    "COMP": 1,  # Computer Science (electives prefix)

    # Life Sciences
    "BIOL": 2,  # Biology
    "BIOT": 3,  # Biotechnology

    # Business and Economics
    "BUSN": 4,  # Business
    "ECON": 6,  # Economics

    # Chemistry and Physical Sciences
    "CHEM": 5,  # Chemistry
    "PHYS": 15,  # Physics

    # Social Sciences and Humanities
    "ENGL": 8,  # English
    "GEOG": 10,  # Geography
    "HIST": 11,  # History
    "MCOM": 12,  # Mass Communication
    "MATH": 13,  # Mathematics
    "PHIL": 14,  # Philosophy
    "PLSC": 16,  # Political Science
    "PSYC": 17,  # Psychology
    "SOCL": 19,  # Sociology

    # Religious Studies and Urdu
    "ISLM": 18,  # Islamiat (Islamic Studies)
    "URDU": 21,  # Urdu
    "LING": 23,  # Linguistics

    # Environmental Sciences
    "ENVR": 9,  # Environmental Sciences

    # Education
    "EDUC": 7,  # Education

    # Statistics
    "STAT": 20,  # Statistics

    # Pharmacy
    "PHRM": 22,  # Pharmacy

    # Religious Studies (Christian)
    "CRST": 24  # Religious Studies (Christian)


"Here is the required structure:\n"
"```json\n"
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
        required_courses = gpt_input['required_courses']  
        major_requirements = gpt_input['major_requirements']

        logger.info("Preparing advising prompt with GPT input.")

       
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
   -"You need to provide student course recommendations using the courses list and from the needed courses that are left after checking users completed courses and the incompleted courses and suggest courses from the incompleted courses based on their grades and gpa and suggesting them courses according to the dificulty level as the lower difficulty level courses are present in the general education and mainly the core courses are the difficult one.

4. **Career Guidance**:
   - Suggest potential career paths where the student can excel, based on their academic strengths and interests.

5. **Finalize the Advising Plan**:
   - Ensure all advice is actionable and aligns with academic regulations.
   - Encourage the student to consult with their academic advisor for personalized guidance.
   - donot add extra sentences out side of the json parantheses.
   -- " give a detailed and extensive and comprehensive answer and  advice response and be real"
   "Provide the JSON within a code block tagged as JSON.\n"
"Here is the required structure:\n"
"```json\n"
{{
    "advising_notes": [
        "Provide clear and concise advising notes here and only suggest advice on users major courses which include core,elective and supporting donot focuse on weaknesses in general ed department but do recommend them to retake it incase there is a bad grade in any of its department.",
        "Include recommendations on courses the user can study in the future recommend them from the departments and courses fields that the user has left to study, strategies should be very impressive,user strengths and weaknesses and potential career paths should be well explained."
        "Tell the user what courses he can take in the future to complete his degree as soon as possible from the courses that are left to be completed
    ]
}}


"""
        logger.info("Advising prompt successfully generated.")
        return prompt.strip()
