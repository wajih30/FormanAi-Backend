from flask import Flask, jsonify
from flask_session import Session
from dotenv import load_dotenv
import os
import logging
from routes.transcript_routes import transcript_bp
from routes.degree_audit_routes import degree_audit_bp
from routes.advising_routes import advising_bp
from routes.chat_routes import chat_bp
from db import init_db
from flask_cors import CORS  # Import CORS

# Load environment variables
load_dotenv()

# Configure logging (as in your original code)
log_file = os.path.abspath(os.path.join(os.getcwd(), 'application.log'))
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='w',
)

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask app instance."""
    app = Flask(__name__)

    # CORS Configuration
    cors = CORS(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": "http://localhost:3000"  # Replace with your frontend URL
        }
    })

    # App configurations from environment variables
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.warning("DATABASE_URL not set. Defaulting to in-memory SQLite.")
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Secret Key for Flask Sessions
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        logger.warning("SECRET_KEY not set. Generating a random secret key.")
        app.secret_key = os.urandom(24)
    else:
        app.secret_key = secret_key

    # Enable session storage
    app.config['SESSION_TYPE'] = 'filesystem'  # Store session data on the file system
    app.config['SESSION_PERMANENT'] = False    # Make sessions temporary (deleted on browser close)
    app.config['SESSION_USE_SIGNER'] = True    # Sign cookies for extra security
    app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')  # Directory to store session files
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)  # Ensure session folder exists
    Session(app)  # Initialize session management

    # File upload configurations
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file uploads to 16MB

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize the database with the app
    init_db(app)

    # Register blueprints
    app.register_blueprint(transcript_bp, url_prefix='/api/transcripts')
    app.register_blueprint(degree_audit_bp, url_prefix='/api/degree-audit')
    app.register_blueprint(advising_bp, url_prefix='/api/advising')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')

    logger.info("Flask application setup completed with registered routes.")

    # Log registered routes
    for rule in app.url_map.iter_rules():
        logger.info(f"Registered route: {rule}")

    # Home route for testing the server
    @app.route('/')
    def home():
        logger.info("Home route accessed.")
        return jsonify({"message": "Welcome to the Academic Transcript Processing API!"}), 200

    # Error handlers (as in your original code)
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error occurred: {error}")
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error occurred: {error}", exc_info=True)
        return jsonify({"error": "Internal server error."}), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        logger.warning(f"413 error occurred: {error}")
        return jsonify({"error": "File size exceeds the maximum allowed limit."}), 413

    return app


if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        app = create_app()
        app.run(debug=True, host="127.0.0.1", port=5000)
    except Exception as e:
        logger.critical(f"Critical error starting the application: {str(e)}", exc_info=True)
