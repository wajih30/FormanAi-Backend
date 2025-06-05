from flask import Flask, send_from_directory, jsonify, request
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv
from routes.chat_routes import chat_bp
from db import db, init_db
import os
import logging


load_dotenv()

#
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), 
    ]
)
logger = logging.getLogger(__name__)


app = Flask(__name__)


CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "http://localhost:3000"}})


db_name = os.environ.get('DB_NAME', 'Unicourses')
db_host = os.environ.get('DB_HOST', 'DESKTOP-I58CVTK')  
logger.info(f"Database connection details: HOST={db_host}, NAME={db_name}")


app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc://@DESKTOP-I58CVTK/Unicourses"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&trusted_connection=yes"
    "&TrustServerCertificate=yes"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


init_db(app)

secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    logger.critical("SECRET_KEY environment variable not set. Exiting application.")
    raise EnvironmentError("SECRET_KEY must be set when SESSION_USE_SIGNER=True")

app.config['SECRET_KEY'] = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.path.abspath(os.getenv('SESSION_FILE_DIR', 'flask_session'))
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

Session(app)


upload_folder = os.path.abspath(os.getenv('UPLOAD_FOLDER', 'uploads'))
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def sanitize_file_paths(file_paths):
    sanitized_paths = []
    for path in file_paths:
        
        filename = os.path.basename(path)
        sanitized_paths.append(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return sanitized_paths


app.register_blueprint(chat_bp, url_prefix='/api/chat')


@app.route('/')
def home():
    return "Welcome to the Flask app!"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200


with app.app_context():
    try:
        db.create_all()
        logger.info("Database setup completed successfully.")
    except Exception as e:
        logger.critical(f"Failed to set up the database: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    try:
        logger.info("Starting Flask application in development mode...")
        app.run(host="127.0.0.1", port=5000, debug=True)  
    except Exception as e:
        logger.critical(f"Critical error starting the application: {e}", exc_info=True)
