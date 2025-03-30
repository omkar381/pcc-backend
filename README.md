# Padashetty Coaching Class Management System

A complete web application for managing a coaching class, including student records, attendance tracking, tests, and notes.

## Features

- **Student Management**: Add and manage student information
- **Attendance Tracking**: Record and monitor student attendance
- **Notes Management**: Upload and share study materials
- **Test Management**: Create tests and record results
- **PDF Generation**: Generate PDF reports for test results
- **WhatsApp Integration**: Share test results via WhatsApp

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: React with Vite
- **Database**: SQLite
- **Styling**: Tailwind CSS
- **PDF Generation**: ReportLab

## Deployment

This application can be deployed for free while preserving all your data:

- **Frontend**: Vercel (free tier)
- **Backend**: Render.com (free tier with 1GB persistent storage)

Follow the detailed instructions in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) to deploy your application.

## Local Development

1. **Start the application**:
   ```
   start.bat
   ```

2. **Access the application**:
   - Backend API: http://localhost:5000
   - Frontend UI: http://localhost:5173

3. **Admin credentials**:
   - Username: pcc
   - Password: pcc@8618

## Data Management

- Regular backups are important! Use the backup script to create backups:
  ```
  cd backend
  python backup_database.py
  ```

- The free tier of Render.com provides 1GB of persistent storage, which should be sufficient for a moderate number of students and PDFs.

## Troubleshooting

If you encounter any issues with the application:

1. **PDF Generation Issues**: Run `start.bat fix` to repair the database
2. **Database Issues**: Run `python backend/cloud_db_setup.py` to initialize the database
3. **Deployment Issues**: See the troubleshooting section in the deployment guide

## License

This project is proprietary software developed for Padashetty Coaching Class.
