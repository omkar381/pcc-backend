from app import app, db, Admin
import sqlite3
import os

def migrate_database():
    with app.app_context():
        try:
            # First, ensure all tables are created
            print("Creating database tables if they don't exist...")
            db.create_all()
            print("Tables created or already exist.")
            
            # Connect to the database
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'padashetty.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if selected_class column exists in admin table
            cursor.execute("PRAGMA table_info(admin)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            if 'selected_class' not in column_names:
                print("Adding 'selected_class' column to admin table...")
                cursor.execute("ALTER TABLE admin ADD COLUMN selected_class TEXT")
                conn.commit()
                print("Column added successfully!")
            else:
                print("Column 'selected_class' already exists.")
            
            conn.close()
            
            # Create or update admin user
            admin = Admin.query.filter_by(username='pcc').first()
            if not admin:
                # Create new admin with selected_class
                admin = Admin(username='pcc', password='pcc@8618', selected_class='')
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully!")
            elif admin.selected_class is None:
                # Update existing admin with selected_class
                admin.selected_class = ''  # Default empty string
                db.session.commit()
                print("Updated admin user with default selected_class value.")
            
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            return False
        
        return True

if __name__ == '__main__':
    migrate_database()
