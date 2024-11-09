from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Create a scoped session for database access if needed
session = db.session