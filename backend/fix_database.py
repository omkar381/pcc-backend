from app import app, db, Admin, Student
import os
import shutil

def fix_database():
    with app.app_context():
        try:
            # Check if database file exists and remove it
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'padashetty.db')
            if os.path.exists(db_path):
                print(f"Removing existing database file: {db_path}")
                os.remove(db_path)
                print("Database file removed.")
            
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("Tables created successfully.")
            
            # Check if admin already exists (shouldn't happen after db reset, but just in case)
            admin = Admin.query.filter_by(username='pcc').first()
            if admin:
                print("Admin user already exists, removing...")
                db.session.delete(admin)
                db.session.commit()
            
            # Create admin user
            print("Creating admin user...")
            admin = Admin(
                username='pcc',
                password='pcc@8618',
                selected_class=''
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            
            # Ensure upload directories exist
            uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), app.config['UPLOAD_FOLDER'])
            
            # Remove and recreate upload directories to ensure they're clean
            if os.path.exists(uploads_dir):
                shutil.rmtree(uploads_dir)
            
            os.makedirs(os.path.join(uploads_dir, 'admission_forms'), exist_ok=True)
            os.makedirs(os.path.join(uploads_dir, 'notes'), exist_ok=True)
            os.makedirs(os.path.join(uploads_dir, 'test_results'), exist_ok=True)
            print("Upload directories created.")
            
            # Create a sample student for testing
            print("Creating sample student...")
            sample_student = Student(
                admission_number="PCC7th00001",
                username="sample_student",
                password="sample_student123",  # Plain text password
                name="Sample Student",
                email="sample@example.com",
                phone="1234567890",
                school_name="Sample School",
                class_level="7th",
                admission_date=db.func.current_date()
            )
            db.session.add(sample_student)
            db.session.commit()
            print("Sample student created successfully!")
            
            print("Database reset and initialization completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during database reset: {e}")
            return False

if __name__ == '__main__':
    fix_database()
