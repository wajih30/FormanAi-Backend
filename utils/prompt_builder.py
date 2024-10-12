import logging
from config import MAJOR_NAME_MAPPING
from models.course_handler import CourseHandler
from models.general_education_handler import GeneralEducationHandler
from utils.course_extraction import extract_course_code, classify_query

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('prompt_handler.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class PromptHandler:
    def __init__(self, major_name, sub_major=None):
        self.major_name = major_name
        self.sub_major = sub_major
        self.major_id = self._get_major_id(major_name)

        if not self.major_id:
            raise ValueError(f"Invalid major name: {major_name}")

        self.course_handler = CourseHandler(self.major_id, sub_major)
        self.gen_ed_handler = GeneralEducationHandler(self.major_id)

    def _get_major_id(self, major_name):
        data = MAJOR_NAME_MAPPING.get(major_name)
        if isinstance(data, dict):
            return data.get("id")
        return data

    def analyze_query_intent(self, query_data):
        query_data = query_data.lower()
        course_code = extract_course_code(query_data)
        keywords = classify_query(query_data)

        return {
            "is_remaining": any(kw in query_data for kw in ["remaining", "left", "still need"]),
            "is_count": any(kw in query_data for kw in ["how many", "required", "need to complete"]),
            "is_available_list": any(kw in query_data for kw in ["choose", "available", "list"]),
            "course_code": course_code,
            "core": "core" in keywords,
            "elective": "elective" in keywords,
            "supporting": "supporting" in keywords,
            "general_ed": any(kw in keywords for kw in ["general education", "gen ed"]),
            "prerequisite": "prerequisite" in keywords,
            "research": any(kw in keywords for kw in ["research", "internship"]),
        }

    def build_manual_query_prompt(self, query_data):
        intent = self.analyze_query_intent(query_data)
        completed_courses = self.course_handler.get_completed_courses()

        if intent["prerequisite"] and intent["course_code"]:
            return self.build_prerequisite_prompt(intent["course_code"])

        if intent["core"]:
            return self.build_course_prompt("core")

        if intent["elective"]:
            if intent["is_count"]:
                return self._build_required_electives_prompt()
            elif intent["is_available_list"]:
                return self.build_course_prompt("elective", limit=self.course_handler.elective_courses_needed)
            elif intent["is_remaining"]:
                return self._build_remaining_courses_prompt("elective", completed_courses)

        if intent["supporting"]:
            return self.build_course_prompt("supporting")

        if intent["general_ed"]:
            return self.build_general_education_prompt()

        if intent["research"]:
            return self._build_research_course_prompt()

        return "Please provide more information or clarify your question so I can better assist you."

    def _build_required_electives_prompt(self):
        required_electives = self.course_handler.elective_courses_needed
        return f"For the {self.major_name} major, you need to complete {required_electives} elective courses."

    def build_course_prompt(self, course_type, limit=None):
        courses = self.course_handler.get_courses(course_type)
        if not courses:
            return f"No {course_type} courses found for the {self.major_name} major."

        if limit:
            courses = courses[:limit]

        formatted_courses = "\n".join(
            [f"{idx + 1}. {course['course_code']} - {course['course_name']}" for idx, course in enumerate(courses)]
        )
        return f"Here are the {course_type} courses you can choose from:\n\n{formatted_courses}"

    def _build_remaining_courses_prompt(self, course_type, completed_courses):
        total_courses = self.course_handler.get_courses(course_type)
        remaining = len(total_courses) - len(completed_courses)
        return f"You have {remaining} {course_type} courses remaining to complete."

    def build_prerequisite_prompt(self, course_code):
        prerequisites = self.course_handler.get_prerequisites(course_code)
        if not prerequisites:
            return f"No prerequisites found for {course_code}."
        return "\n".join(prerequisites)

    def build_general_education_prompt(self):
        gen_ed_status = self.gen_ed_handler.get_all_gen_ed_courses()
        return self._format_gen_ed_prompt(gen_ed_status)

    def _format_gen_ed_prompt(self, gen_ed_status):
        prompt = f"General Education requirements for the {self.major_name} major:\n\n"
        for category, courses in gen_ed_status.items():
            prompt += f"{category.replace('_', ' ').capitalize()}: {len(courses)} completed.\n"
        return prompt

    def _build_research_course_prompt(self):
        research_courses = self.course_handler.get_research_courses()
        if not research_courses:
            return "No research or internship courses found for your major."
        return "\n".join([f"{course['course_code']} - {course['course_name']}" for course in research_courses])

    def build_transcript_analysis_prompt(self, transcript_data, remaining_courses, gen_ed_status, gpa=None, cgpa=None):
        prompt = f"Completed Courses: {', '.join(transcript_data.get('completed_courses', []))}.\n"
        prompt += f"GPA: {gpa}, CGPA: {cgpa}.\n\n"

        for course_type, courses in remaining_courses.items():
            prompt += f"Remaining {course_type.capitalize()} Courses: {', '.join(courses)}\n"
        prompt += f"General Education Status: {gen_ed_status}\n"
        return prompt

    def build_degree_audit_prompt(self, transcript_data, course_tables):
        prompt = f"Degree Audit for {self.major_name} Major\n\n"
        for semester, courses in transcript_data.items():
            prompt += f"{semester}:\n"
            for course in courses:
                prompt += f"  - {course['course_code']}: {course['course_name']} (Grade: {course['grade']})\n"

        for table_name, courses in course_tables.items():
            prompt += f"\n{table_name.capitalize()} Requirements:\n"
            for course in courses:
                prompt += f"  - {course['course_code']} - {course['course_name']} (Credits: {course['credits']})\n"
        return prompt
