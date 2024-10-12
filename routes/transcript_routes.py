from flask import Blueprint, request, jsonify
from services.transcript_analysis_service import TranscriptService
from utils.prompt_builder import build_transcript_analysis_prompt
from services.openai_services import generate_chatgpt_response

transcript_bp = Blueprint('transcript_routes', __name__)

@transcript_bp.route('/upload_transcript', methods=['POST'])
def upload_transcript():
    """
    Route to handle transcript uploads and analysis using GPT-4 Vision.
    """
    try:
        file = request.files.get('file')
        major_name = request.form.get('major_name')  # Retrieve the major selected by the user
        student_id = request.form.get('student_id')

        if not file or not major_name or not student_id:
            return jsonify({"error": "Missing required information"}), 400

        # Analyze the transcript file
        transcript_service = TranscriptService()
        extracted_data = transcript_service.analyze_transcript(file)

        if not extracted_data:
            return jsonify({"error": "Failed to extract data from the uploaded file."}), 500

        # Build the transcript analysis prompt
        transcript_prompt = build_transcript_analysis_prompt(extracted_data, major_name)

        # Generate the response from GPT-4 based on the extracted data
        transcript_analysis_response = generate_chatgpt_response(transcript_prompt)

        return jsonify({
            "student_id": student_id,
            "major_name": major_name,
            "transcript_analysis_response": transcript_analysis_response,
            "transcript_data": extracted_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
