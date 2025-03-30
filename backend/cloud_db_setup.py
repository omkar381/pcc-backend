"""
Cloud Database Setup Script

This script creates the necessary tables in the database when deployed to Render.com
and ensures that the necessary directories exist.
"""

from app import app, db, Admin
import os

def setup_cloud_database():
    print("Setting up cloud database...")
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("Database tables created or verified.")
        
        # Create admin user if it doesn't exist
        admin = Admin.query.filter_by(username='pcc').first()
        if not admin:
            admin = Admin(username='pcc', password='pcc@8618', selected_class='')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")
        
        # Ensure upload directories exist
        upload_dirs = [
            os.path.join(app.config['UPLOAD_FOLDER']),
            os.path.join(app.config['UPLOAD_FOLDER'], 'admission_forms'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'notes'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'test_results')
        ]
        
        for directory in upload_dirs:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        
    print("Cloud database setup complete!")

if __name__ == "__main__":
    setup_cloud_database() 