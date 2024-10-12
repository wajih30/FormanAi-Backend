from flask import Blueprint, request, jsonify
from services.transcript_analysis_service import TranscriptAnalysisService
from utils.prompt_builder import PromptHandler
from services.openai_services import generate_chatgpt_response

# Define a Blueprint for transcript-related routes
transcript_bp = Blueprint('transcript_routes', __name__)

@transcript_bp.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    """
    Route to handle transcript uploads and analysis using GPT-4 Vision.
    """
    try:
        # Get the uploaded file and form data
        file = request.files.get('file')
        major_name = request.form.get('major_name')  # Retrieve major name
        student_id = request.form.get('student_id')  # Retrieve student ID

        if not file or not major_name:
            return jsonify({"error": "File and major name are required."}), 400

        # Initialize the transcript analysis service
        transcript_service = TranscriptAnalysisService(major_name)
        
        # Analyze the transcript and extract relevant data
        extracted_data = transcript_service.analyze_transcript(file)
        
        if not extracted_data:
            return jsonify({"error": "Failed to extract data from the uploaded file."}), 500

        # Initialize the prompt handler and build the transcript analysis prompt
        prompt_handler = PromptHandler(major_name)
        transcript_prompt = prompt_handler.build_transcript_analysis_prompt(
            extracted_data=extracted_data,
            remaining_courses={},
            gen_ed_status={},
            gpa=extracted_data.get('GPA'),
            cgpa=extracted_data.get('CGPA')
        )

        # Generate the response using GPT-4
        transcript_analysis_response = generate_chatgpt_response(transcript_prompt)

        return jsonify({
            "student_id": student_id,
            "major_name": major_name,
            "transcript_analysis_response": transcript_analysis_response,
            "transcript_data": extracted_data
        }), 200

    except ValueError as ve:
        # Handle known errors gracefully
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        # Handle unexpected errors gracefully
        return jsonify({"error": str(e)}), 500
