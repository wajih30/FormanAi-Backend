from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# You can leave this as is, this will allow you to initialize the app with SQLAlchemy
def init_db(app):
    """Initialize the database with the app."""
    db.init_app(app)

session = db.session

