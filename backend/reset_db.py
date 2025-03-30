from app import app, db, Admin
import os
import shutil
import sys

def reset_database():
    with app.app_context():
        try:
            # Add confirmation prompt
            if len(sys.argv) <= 1 or sys.argv[1] != "--force":
                confirm = input("WARNING: This will delete all data in the database! Continue? (y/n): ")
                if confirm.lower() != 'y':
                    print("Database reset cancelled.")
                    return False
            
            # Check if database file exists and remove it
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'padashetty.db')
            if os.path.exists(db_path):
                print(f"Removing existing database file: {db_path}")
                os.remove(db_path)
                print("Database file removed.")
            
            # Backup uploaded files
            backup_dir = 'uploads_backup'
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                print(f"Backing up existing uploads to {backup_dir}...")
                if os.path.exists(backup_dir):
                    shutil.rmtree(backup_dir)
                shutil.copytree(app.config['UPLOAD_FOLDER'], backup_dir)
                print("Uploads backed up successfully.")
            
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("Tables created successfully.")
            
            # Create admin user
            print("Creating admin user...")
            admin = Admin(
                username='pcc',
                password='pcc@8618',  # Plain text password as in the original code
                selected_class=''
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
            
            # Ensure upload directories exist
            upload_dirs = [
                os.path.join(app.config['UPLOAD_FOLDER']),
                os.path.join(app.config['UPLOAD_FOLDER'], 'admission_forms'),
                os.path.join(app.config['UPLOAD_FOLDER'], 'notes'),
                os.path.join(app.config['UPLOAD_FOLDER'], 'test_results')
            ]
            
            for directory in upload_dirs:
                os.makedirs(directory, exist_ok=True)
                print(f"Verified directory: {directory}")
            
            print("Database reset and initialization completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during database reset: {e}")
            return False

if __name__ == '__main__':
    reset_database()
