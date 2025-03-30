"""
Database Backup Script

This script creates a backup of the SQLite database and uploaded files.
Run it periodically to ensure your data is safely backed up.
"""

import os
import shutil
import datetime
import sqlite3
from app import app

def backup_database():
    # Create backups directory if it doesn't exist
    backups_dir = 'backups'
    if not os.path.exists(backups_dir):
        os.makedirs(backups_dir)
    
    # Create a timestamped backup folder
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_folder = os.path.join(backups_dir, f"backup_{timestamp}")
    os.makedirs(backup_folder)
    
    # Get database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'padashetty.db')
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    try:
        # Verify database integrity
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA integrity_check")
        conn.close()
        
        # Copy database file
        db_backup_path = os.path.join(backup_folder, 'padashetty.db')
        shutil.copy2(db_path, db_backup_path)
        print(f"Database backed up to {db_backup_path}")
        
        # Backup uploaded files
        uploads_dir = app.config['UPLOAD_FOLDER']
        if os.path.exists(uploads_dir):
            uploads_backup_dir = os.path.join(backup_folder, 'uploads')
            shutil.copytree(uploads_dir, uploads_backup_dir)
            print(f"Uploads backed up to {uploads_backup_dir}")
        
        print(f"Backup completed successfully at {backup_folder}")
        return True
    
    except Exception as e:
        print(f"Error during backup: {str(e)}")
        return False

if __name__ == "__main__":
    backup_database() 