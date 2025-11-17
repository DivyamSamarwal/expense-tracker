from app import app, db
import models  # Import the models to register them

# Create the application context
with app.app_context():
    # Create all tables
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")