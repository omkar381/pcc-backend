from app import app, db, Admin
import os

def init_database():
    with app.app_context():
        # Create all tables without dropping existing ones
        db.create_all()
        
        # Check if admin exists
        admin = Admin.query.filter_by(username='pcc').first()
        if not admin:
            admin = Admin(username='pcc', password='pcc@8618', selected_class='')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            # Update admin if it exists but doesn't have selected_class
            if not hasattr(admin, 'selected_class') or admin.selected_class is None:
                admin.selected_class = ''
                db.session.commit()
                print("Updated admin user with selected_class field")
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
            print(f"Verified directory: {directory}")

if __name__ == '__main__':
    init_database()
    print("Database initialization completed successfully!")
