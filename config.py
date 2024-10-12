import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database Configuration for MSSQL using Windows Authentication
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI API Key (if needed)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# Dictionary to store table mappings for each major, aligned by the given numbering scheme
MAJOR_TABLE_MAPPING = {
    1: {  # Computer Science
        "core": "corecourses",
        "elective": "electives",
        "supporting": "supporting_courses",
        "courses": "Courses",
        "prerequisites": "prerequisites",
        "prereq_column": "prerequisite_code",
    },
    2: {  # Biology
        "core": "biology_corecourses",
        "elective": "bio_electives",
        "supporting": "biology_supportingcourses",
        "courses": "biology_courses",
        "prerequisites": "bioll_prereqs",
        "prereq_column": "prereq_code",
    },
    3: {  # Biotechnology
        "core": "biotechcore_courses",
        "elective": "biotechelectives",
        "courses": "biotcourses",
        "prerequisites": "biot_prereqs",
        "prereq_column": "prerequisite_code",
    },
    4: {  # Business
        "core": "business_core",
        "elective": "busnelectives",
        "courses": "buisncourses",
        "prerequisites": "buisn_prereqss",
        "prereq_column": "prereq_code",
    },
    5: {  # Chemistry
        "core": "chemcore",
        "elective": "chemelective",
        "courses": "chemcourses",
        "prerequisites": "chem_prerequisitesss",
        "prereq_column": "prerequisite_code",
    },
    6: {  # Economics
        "core": "ecocore",
        "elective": "ecoelective",
        "courses": "ecocourses",
        "prerequisites": "ecopre_reqs",
        "prereq_column": "prerequisite_code",
    },
    7: {  # Education
        "core": "educ_core",
        "elective": "educ_elec",
        "courses": "educourses",
        "prerequisites": "edu_prereqss",
        "prereq_column": "prerequisite_code",
    },
    8: {  # English
        "core": "engcore",
        "elective": "engelectives",
        "courses": "engcourses",
        "prerequisites": "eng_prereqss",
        "prereq_column": "prerequisite_code",
    },
    9: {  # Environmental Sciences
        "core": "envcore",
        "elective": "envelective",
        "courses": "envcourses",
        "prerequisites": "envprereqss",
        "prereq_column": "prereq_code",
    },
    10: {  # Geography
        "core": "physical_geography_cores",
        "elective": "physical_geography_electives",
        "courses": "geocourses",
        "prerequisites": "geopre_reqss",
        "prereq_column": "prereq_course_code",
    },
    11: {  # History
        "core": "histcore",
        "elective": "histelective",
        "courses": "histcourses",
        "prerequisites": "histprereqs",
        "prereq_column": "prereq_code",
    },
    12: {  # Mass Communication
        "core": "mcomcore",
        "elective": "mcomelective",
        "courses": "mcomcourses",
        "prerequisites": "mcompreqss",
        "prereq_column": "prerequisite_code",
    },
    13: {  # Mathematics
        "core": "mathcore",
        "elective": "mathelective",
        "courses": "mathcourses",
        "prerequisites": "mathprereqs",
        "prereq_column": "prerequisite_code",
    },
    14: {  # Philosophy
        "core": "philcore",
        "elective": "philelective",
        "courses": "philcourses",
        "prerequisites": "philpre_reqss",
        "prereq_column": "prerequisite_code",
    },
    15: {  # Physics
        "core": "core_courses",
        "elective": "phys_electives",
        "courses": "physcourses",
        "prerequisites": "physcpre_reqs",
        "prereq_column": "prereq_code",
    },
    16: {  # Political Science
        "core": "polsci_core",
        "elective": "polsci_electives",
        "courses": "polscicourses",
        "prerequisites": "polscispre_reqs",
        "prereq_column": "prerequisite_code",
    },
    17: {  # Psychology (Including Applied Psychology)
         "main_category": "Psychology",
        "sub_categories": {
            "Normal": {
                "core": "psychology_core_courses",
                "elective": "psychology_elective_courses",
                "courses": "psychcourses",
                "prerequisites": "psych_prereqs",
                "prereq_column": "prerequisite_code",
            },
            "Applied": {
                "core": "applied_psychology_core_courses",
                "elective": "applied_psychology_elective_courses",
                "courses": "applied_psych_courses",
                "prerequisites": "applied_psych_prereqs",
                "prereq_column": "prerequisite_code",
            }
        }
    },
    18: {  # Religious Studies ISL
        "core": "islamic_studies_core_courses",
        "elective": "islamic_studies_major_electives",
        "courses": "isl_courses",
        "prerequisites": "isllprerequisites",
        "prereq_column": "prerequisite_code",
    },
    19: {  # Sociology
         "main_category": "Sociology",
        "sub_categories": {
            "Normal": {
                "core": "socio_core_courses",
                "elective": "socioelective",
                "courses": "sociocourses",
                "prerequisites": "socio_prerequisites",
                "prereq_column": "prereq_code",
            },
            "Sociology and Cult": {
                "core": "socioandcult_core_courses",
                "elective": "socioandcult_elective_courses",
                "courses": "socioandcult_courses",
                "prerequisites": "socioandcult_prereqs",
                "prereq_column": "prereq_code",
            }
        }
    },
    20: {  # Statistics
        "core": "statscore_courses",
        "elective": "statselective_courses",
        "courses": "stats_courses",
        "prerequisites": "stats_prerequisites",
        "prereq_column": "prereq_code",
    },
    21: {  # Urdu
        "core": "urducore_courses",
        "elective": "urdu_electives",
        "courses": "urdu_courses",
        "prerequisites": "urdu_course_prerequisites",
        "prereq_column": "prerequisite_code",
    },
    22: {  # Pharmacy
        "core": "pharmcore",
        "elective": "pharmelective",
        "courses": "pharm_courses",
    },
    23: {  # Linguistics
        "core": "lingcore",
        "elective": "lingelectives",
        "courses": "lingcourses",
        "prerequisites": "ling_prereqs",
        "prereq_column": "prerequisite_code",
    },
    24: {  # Religious Studies Chris
        "core": "chris_studies_core_courses",
        "elective": "chris_studies_major_electives",
        "courses": "ChrisCourses",
        "prerequisites": "CRSTT_prerequisites",
        "prereq_column": "prereq_code",
    },
    "general": {  # General Education (Universal Table)
        "table": "bio_general_education",
        "columns": ["course_code", "credits", "course_type"],
    },
    "criminology": {  # Criminology Department Courses (Not a Major)
        "courses": "criminology_courses",
    },
}


# config.py

# General Education Requirements and Exemptions for Each Major
GENERAL_ED_REQUIREMENTS = {
    1: {  # Computer Science
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "science_lab":1, 
        "science_lab_options": ["CHEM", "PHYS", "ENVR","BIOL","BIOT"]
        
          # Exempted for Computer Science
    },
    2: {  # Biology
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "science_lab":1, 
        "science_lab_options":["CHEM", "PHYS", "ENVR"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "mathematics":1,
        "math_options":["MATH"],
        
         # Exempted for Biology
    },
    3: {  # Biotechnology
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "science_lab":1,
        "science_lab_options": ["CHEM", "PHYS", "ENVR"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "mathematics":1,
        "math_options":["MATH"]
    },
    4: {  # Business
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 0,
        "mathematics":1,
        "math_options":["MATH"],    # Exempted (covered by major courses)
        "science_lab":2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR","BIOL","BIOT"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Exempted for Business
    },
     5: {  # Chemistry
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "mathematics":1,
        "math_options":["MATH"], 
        "science_lab":1,
        "science_lab_options": ["PHYS", "ENVR","BIOL","BIOT"],
        "cs_require":1,
        "computer_science":["CSCS"],
       },
        6: {  #Economics
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences":0,#exempted
        "science_lab":2,
        "science_lab_options": ["PHYS", "CHEM","ENVR","BIOL","BIOT"],
        "mathematics":1,
        "math_options":["MATH"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Exempted for Business
        "cs_require":1,
        "computer_science":["CSCS"],
       },7: {  # Education
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 0,  # Exempted (covered by major courses)
        "science_lab": 2,
        "mathematics":1,
        "math_options":["MATH"],
        "science_lab_options": ["PHYS", "CHEM","ENVR","BIOL","BIOT"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional for Education
        "cs_require":1,
        "computer_science":["CSCS"],
    },
    8: {  # English
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 0,  # Exempted (covered by major courses)
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "mathematics":1,
        "math_options":["MATH"],
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"], 
        "cs_require":1,
        "computer_science":["CSCS"],
    },
    9: {  # Environmental Sciences
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "science_lab": 1,
        "science_lab_options": ["CHEM", "PHYS", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"]  # Covered by Major
    },
    10: {  # Geography
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 0,  # Exempted (covered by major courses)
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional
    },
    11: {  # History
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 0,
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"], # Exempted (covered by major courses)
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional
    },
    12: {  # Mass Communication
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 0,
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"], # Exempted (covered by major courses)
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional
    },
    13: {  # Mathematics
       "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":0,
        "cs_require":1,
        "computer_science":["CSCS"],
       },
    14: {  # Philosophy
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 0,
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "mathematics":1,
        "math_options":["MATH"],
    },
    15: {  # Physics
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "science_lab": 1,
        "science_lab_options": ["CHEM", "ENVR","BIOL","BIOT"],
        "additional_courses": 0 ,# Exempted for Physics
        "cs_require":1,
        "computer_science":["CSCS"],
        "mathematics":1,
        "math_options":["MATH"], 
    },
    16: {  # Political Science
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 0,  # Exempted (covered by major courses)
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional
    },
    17: {  # Psychology
       "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 0,  # Exempted (covered by major courses)
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional
    },
    18: {  # Religious Studies ISL
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 0,
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"], # Exempted (covered by major courses)
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional
    },
    19: {  # Sociology
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 0,  # Exempted (covered by major courses)
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional
    },
    20: {  # Statistics
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
       },
    21: {  # Urdu
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 0,
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"], # Exempted (covered by major courses)
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional
    },
    22: {  # Pharmacy
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 2,
        "humanities_options": ["PHIL", "MCOM", "URDU", "ENGL", "ISLM", "CRST", "HIST", "ARTS", "MUSC", "Foreign Language"],
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "science_lab": 1,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
    },
    23: {  # Linguistics
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 0,  # Exempted (covered by major courses)
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"],
        "mathematics":1,
        "math_options":["MATH"],
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"], 
        "cs_require":1,
        "computer_science":["CSCS"],
    },
    24: {  # Religious Studies Chris
        "compulsory": ["UNIV100", "WRCM101", "WRCM102", "URDU101", "PKST101"],
        "religious": ["ISLM101", "CRST152"],
        "humanities": 0,
        "social_sciences": 2,
        "social_sciences_options": ["SOCL", "PSYC", "GEOG", "PLSC", "ECON", "EDUC", "BUSN"], # Exempted (covered by major courses)
        "science_lab": 2,
        "science_lab_options": ["CHEM", "PHYS", "ENVR", "BIOL"],
        "mathematics":1,
        "math_options":["MATH"],
        "cs_require":1,
        "computer_science":["CSCS"],
        "additional_courses_option":1,
        "additional_courses": ["CSCS", "COMP", "MATH", "PHIL 221", "STAT", "BIOL", "BIOT", "ENVR", "CHEM", "PHYS"],  # Optional
    },
}

# config.py

MAJOR_REQUIREMENTS = {
    1: {  # Computer Science
        
        "elective_courses_needed": 4,
          # Required prefixes: CSCS, MATH, STAT
        "supporting_prefixes": ["CSCS", "MATH", "STAT"],
        
        "general_education": GENERAL_ED_REQUIREMENTS[1],
    },
    2: {  # Biology
        
        "elective_courses_needed": 6,
        "supporting_courses_needed": 3,  # Required prefixes: CHEM, BIOL
        "supporting_prefixes": ["CHEM"],
        
        "general_education": GENERAL_ED_REQUIREMENTS[2],
    },
    3: {  # Biotechnology
        
        "elective_courses_needed": 4,
    
        "general_education": GENERAL_ED_REQUIREMENTS[3],
    },
    4: {  # Business
        
        "elective_courses_needed": 6,
        "specializations": {  # Business electives specialization categories
            "Operations Management": 6,
            "Accounting and Finance": 6,
            "Marketing and Sales": 6,
            "Human Resource Management": 6
        },
        "general_education": GENERAL_ED_REQUIREMENTS[4],
    },
    5: {  # Chemistry
        "core_courses_needed": 12,
        "elective_courses_needed": 3,
        "general_education": GENERAL_ED_REQUIREMENTS[5],
    },
    6: {  # Economics
        "elective_courses_needed": 8,
       
        "general_education": GENERAL_ED_REQUIREMENTS[6],
    },
    7: {  # Education
        
        "elective_courses_needed": 7,
        "elective_categories": {
            "pedagogy": 3,  # 3 pedagogy courses
            "normal": 4  # 4 normal electives
        },
        "general_education": GENERAL_ED_REQUIREMENTS[7],
    },
    8: {  # English
        
        "elective_courses_needed": 8,
      
        "general_education": GENERAL_ED_REQUIREMENTS[8],
    },
    9: {  # Environmental Sciences
        
        "elective_courses_needed": 5,
        
        "general_education": GENERAL_ED_REQUIREMENTS[9],
    },
    10: {  # Geography
        
        "physical_elective_courses_needed": 7,
        "human_elective":4,
       
        "general_education": GENERAL_ED_REQUIREMENTS[10]
    },
    11: {  # History
        
        "elective_courses_needed": 6,
        "specializations": {  # Elective categories for History
            "Mughal History": 2,
            "post mughal": 1,
            "British History": 1,
            "others":2
        },
        "general_education": GENERAL_ED_REQUIREMENTS[11],
    },
    12: {  # Mass Communication
        
        "elective_courses_needed": 10,
       
        "general_education": GENERAL_ED_REQUIREMENTS[12],
    },
    13: {  # Mathematics
        
        "elective_courses_needed": 4,
        "general_education": GENERAL_ED_REQUIREMENTS[13],
    },
    14: {  # Philosophy
        
        "elective_courses_needed": 7,
       
        "general_education": GENERAL_ED_REQUIREMENTS[14],
    },
    15: {  # Physics
        "elective_courses_needed": 6,
         # Required prefixes: PHYS, MATH, CSCS
        
        "general_education": GENERAL_ED_REQUIREMENTS[15],
    },
    16: {  # Political Science
        "core_courses_needed": 10,
        "elective_courses_needed": 8,
        
        "general_education": GENERAL_ED_REQUIREMENTS[16],
    },
     17: {  # Psychology
        "core_courses_needed": 12,
        "sub_categories": {
            "Normal": {
                "normal_elective_courses_needed": 3,
            },
            "Applied": {
                "applied_elective_courses_needed": 8,
            }
        },
        "general_education": GENERAL_ED_REQUIREMENTS[17],
    },
    18: {  # Religious Studies ISL
        "elective_courses_needed": 6,
        "general_education": GENERAL_ED_REQUIREMENTS[18],
    },
    19: {  # Sociology
        "core_courses_needed": 10,
        "sub_categories": {
            "Normal": {
                "elective_courses_needed": 6,
            },
            "Sociology and Cult": {
                "cult_elective_courses_needed": 7,
            }
        },
        "general_education": GENERAL_ED_REQUIREMENTS[19],
    },
    20: {  # Statistics
        "elective_courses_needed": 5,
        "general_education": GENERAL_ED_REQUIREMENTS[20],
    },
    21: {  # Urdu
        "elective_courses_needed": 7,
        "general_education": GENERAL_ED_REQUIREMENTS[21],
    }, 22: {  # Pharmacy
        
    },
    23: {  # Linguistics
        "elective_courses_needed": 5,
        
        "general_education": GENERAL_ED_REQUIREMENTS[23],
    },
    24: {  # Religious Studies Chris
        "core_courses_needed": 8,
        "1_elective_courses_needed":3,
        "2_elective_courses_needed":3,
        "general_education": GENERAL_ED_REQUIREMENTS[24],
    },
   
   
}

# Create a global mapping for major names to IDs or configurations
MAJOR_NAME_MAPPING = {
    "Computer Science": 1,
    "Biology": 2,
    "Biotechnology": 3,
    "Business": 4,
    "Chemistry": 5,
    "Economics": 6,
    "Education": 7,
    "English": 8,
    "Environmental Sciences": 9,
    "Geography": 10,
    "History": 11,
    "Mass Communication": 12,
    "Mathematics": 13,
    "Philosophy": 14,
    "Physics": 15,
    "Political Science": 16,
    "Psychology": {
        "id": 17,
        "sub_categories": {
            "Normal": {},
            "Applied": {}
        }
    },
    "Islamiat"
    "Isl": 18,
    "Sociology": {
        "id": 19,
        "sub_categories": {
            "Sociology": {},
            "Sociology and Cult": {}
        }
    },
    "Statistics": 20,
    "Urdu": 21,
    "Pharmacy": 22,
    "Linguistics": 23,
    "Religious Studies Chris": 24
}
