from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import jwt
import datetime
from functools import wraps
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from dotenv import load_dotenv
import urllib.parse

# Helper functions for handling directories and files
def ensure_directory_exists(directory):
    """Ensure a directory exists and is writable"""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        except Exception as e:
            print(f"Error creating directory {directory}: {str(e)}")
            return False
    
    # Check if directory is writable
    if not os.access(directory, os.W_OK):
        print(f"Warning: Directory {directory} is not writable")
        return False
    
    return True

def verify_file_path(path):
    """Verify that a file path is valid and the parent directory exists"""
    if not path:
        return False
    
    directory = os.path.dirname(path)
    return ensure_directory_exists(directory)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*").split(",")}})

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'padashetty_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///padashetty.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['WHATSAPP_GROUP_LINK'] = os.getenv('WHATSAPP_GROUP_LINK', 'https://chat.whatsapp.com/HkSWuBBqXpMG2DFmqnVORf')
app.config['FRONTEND_URL'] = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Ensure upload directories exist
upload_dirs = [
    os.path.join(app.config['UPLOAD_FOLDER']),
    os.path.join(app.config['UPLOAD_FOLDER'], 'admission_forms'),
    os.path.join(app.config['UPLOAD_FOLDER'], 'notes'),
    os.path.join(app.config['UPLOAD_FOLDER'], 'test_results')
]

for directory in upload_dirs:
    ensure_directory_exists(directory)
    print(f"Verified directory: {directory}")

# Initialize database
db = SQLAlchemy(app)

# Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    selected_class = db.Column(db.String(10), nullable=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_number = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    school_name = db.Column(db.String(200), nullable=True)
    class_level = db.Column(db.String(10), nullable=False)  # 7th to 12th
    admission_date = db.Column(db.Date, nullable=False)
    admission_form_path = db.Column(db.String(255), nullable=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    present = db.Column(db.Boolean, default=False)
    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.Date, nullable=False)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    class_level = db.Column(db.String(10), nullable=False)  # 7th to 12th
    date = db.Column(db.Date, nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)

class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    marks_obtained = db.Column(db.Float, nullable=False)
    test = db.relationship('Test', backref=db.backref('results', lazy=True))
    student = db.relationship('Student', backref=db.backref('test_results', lazy=True))
    pdf_path = db.Column(db.String(255), nullable=True)
    shared_to_whatsapp = db.Column(db.Boolean, default=False)

# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            if 'admin_id' in data:
                current_user = Admin.query.get(data['admin_id'])
                kwargs['is_admin'] = True
            else:
                current_user = Student.query.get(data['student_id'])
                kwargs['is_admin'] = False
            
            if not current_user:
                return jsonify({'message': 'Invalid token!'}), 401
            
            kwargs['current_user'] = current_user
        except:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# Routes
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    admin = Admin.query.filter_by(username=username).first()
    
    if admin and admin.password == password:  # For simplicity, not using password hashing for predefined admin
        token = jwt.encode({
            'admin_id': admin.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/student/login', methods=['POST'])
def student_login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password are required!'}), 400
    
    student = Student.query.filter_by(username=data.get('username')).first()
    
    if not student:
        # Try with admission number as fallback
        student = Student.query.filter_by(admission_number=data.get('username')).first()
    
    # For simplicity, check if the password matches the pattern: username123
    expected_password = f"{student.username}123" if student else None
    
    if not student or data.get('password') != expected_password:
        return jsonify({'message': 'Invalid credentials!'}), 401
    
    token = jwt.encode({
        'student_id': student.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token,
        'student_id': student.id,
        'name': student.name,
        'admission_number': student.admission_number,
        'class_level': student.class_level
    })

@app.route('/api/admin/students', methods=['GET'])
@token_required
def get_students(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    students = Student.query.all()
    result = []
    
    for student in students:
        student_data = {
            'id': student.id,
            'admission_number': student.admission_number,
            'name': student.name,
            'email': student.email,
            'phone': student.phone,
            'school_name': student.school_name,
            'class_level': student.class_level,
            'admission_date': student.admission_date.strftime('%Y-%m-%d'),
            'has_admission_form': bool(student.admission_form_path)
        }
        result.append(student_data)
    
    return jsonify(result)

@app.route('/api/admin/students', methods=['POST'])
@token_required
def add_student(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    school_name = request.form.get('school_name')
    class_level = request.form.get('class_level')
    
    if not name:
        return jsonify({'message': 'Student name is required!'}), 400
    
    if not class_level:
        return jsonify({'message': 'Class level is required!'}), 400
    
    # Generate admission number (PCC + class + 5-digit number)
    last_student = Student.query.filter_by(class_level=class_level).order_by(Student.id.desc()).first()
    
    if last_student:
        # Extract the numeric part of the last admission number
        last_num = int(last_student.admission_number.split(class_level)[1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    # Format: PCC + class + 5-digit number (e.g., PCC7th00001)
    admission_number = f"PCC{class_level}{new_num:05d}"
    
    # Generate username and password
    username = name.lower().replace(' ', '_')  # Convert name to lowercase and replace spaces with underscores
    password = f"{username}123"  # Password is username + 123
    
    # Create new student
    new_student = Student(
        admission_number=admission_number,
        username=username,
        password=password,  # Store password directly instead of hashing
        name=name,
        email=email,
        phone=phone,
        school_name=school_name,
        class_level=class_level,
        admission_date=datetime.datetime.now().date()
    )
    
    # Handle file upload if present
    if 'admission_form' in request.files:
        file = request.files['admission_form']
        if file and file.filename:
            filename = secure_filename(f"{admission_number}_{file.filename}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'admission_forms', filename)
            file.save(file_path)
            new_student.admission_form_path = file_path
    
    db.session.add(new_student)
    db.session.commit()
    
    return jsonify({
        'message': 'Student added successfully!',
        'admission_number': admission_number,
        'username': username,
        'password': password
    }), 201

@app.route('/api/admin/students/<int:student_id>/admission-form', methods=['POST'])
@token_required
def upload_admission_form(current_user, is_admin, student_id):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    student = Student.query.get(student_id)
    if not student:
        return jsonify({'message': 'Student not found!'}), 404
    
    if 'admission_form' not in request.files:
        return jsonify({'message': 'No file part!'}), 400
    
    file = request.files['admission_form']
    if file.filename == '':
        return jsonify({'message': 'No file selected!'}), 400
    
    filename = secure_filename(f"{student.admission_number}_{file.filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'admission_forms', filename)
    file.save(file_path)
    
    student.admission_form_path = file_path
    db.session.commit()
    
    return jsonify({'message': 'Admission form uploaded successfully'})

@app.route('/api/student/admission-form', methods=['GET'])
@token_required
def get_admission_form(current_user, is_admin):
    if is_admin:
        return jsonify({'message': 'Not accessible by admin!'}), 403
    
    student = current_user
    if not student.admission_form_path:
        return jsonify({'message': 'No admission form available!'}), 404
    
    try:
        return send_file(student.admission_form_path, as_attachment=True, download_name=f"{student.admission_number}_admission_form.pdf")
    except FileNotFoundError:
        return jsonify({'message': 'File not found on server'}), 404

@app.route('/api/admin/attendance', methods=['POST'])
@token_required
def mark_attendance(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    data = request.get_json()
    date_str = data.get('date')
    attendance_data = data.get('attendance')
    
    try:
        attendance_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format!'}), 400
    
    for item in attendance_data:
        student_id = item.get('student_id')
        present = item.get('present', False)
        
        # Check if attendance record already exists
        attendance = Attendance.query.filter_by(
            student_id=student_id,
            date=attendance_date
        ).first()
        
        if attendance:
            attendance.present = present
        else:
            attendance = Attendance(
                student_id=student_id,
                date=attendance_date,
                present=present
            )
            db.session.add(attendance)
    
    db.session.commit()
    
    return jsonify({'message': 'Attendance marked successfully'})

@app.route('/api/student/attendance', methods=['GET'])
@token_required
def get_student_attendance(current_user, is_admin):
    if is_admin:
        return jsonify({'message': 'Not accessible by admin!'}), 403
    
    student = current_user
    attendances = Attendance.query.filter_by(student_id=student.id).all()
    result = []
    
    for attendance in attendances:
        result.append({
            'date': attendance.date.strftime('%Y-%m-%d'),
            'present': attendance.present
        })
    
    return jsonify(result)

@app.route('/api/admin/notes', methods=['POST'])
@token_required
def upload_note(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    if 'note_file' not in request.files:
        return jsonify({'message': 'No file part!'}), 400
    
    file = request.files['note_file']
    if file.filename == '':
        return jsonify({'message': 'No file selected!'}), 400
    
    title = request.form.get('title')
    subject = request.form.get('subject')
    
    if not title or not subject:
        return jsonify({'message': 'Title and subject are required!'}), 400
    
    filename = secure_filename(f"{subject}_{title}_{datetime.datetime.now().strftime('%Y%m%d')}_{file.filename}")
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'notes', filename)
    file.save(file_path)
    
    new_note = Note(
        title=title,
        subject=subject,
        file_path=file_path,
        upload_date=datetime.datetime.now().date()
    )
    
    db.session.add(new_note)
    db.session.commit()
    
    return jsonify({'message': 'Note uploaded successfully'})

@app.route('/api/notes', methods=['GET'])
@token_required
def get_notes(current_user, is_admin):
    subject = request.args.get('subject')
    
    query = Note.query
    if subject:
        query = query.filter_by(subject=subject)
    
    notes = query.all()
    result = []
    
    for note in notes:
        result.append({
            'id': note.id,
            'title': note.title,
            'subject': note.subject,
            'upload_date': note.upload_date.strftime('%Y-%m-%d')
        })
    
    return jsonify(result)

@app.route('/api/notes/<int:note_id>/download', methods=['GET'])
def download_note(note_id):
    # Check for token in query parameters
    token = request.args.get('token')
    
    if not token:
        return jsonify({'message': 'Token is missing!'}), 401
    
    try:
        # Verify token
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        
        note = Note.query.get(note_id)
        if not note:
            return jsonify({'message': 'Note not found!'}), 404
        
        try:
            filename = os.path.basename(note.file_path)
            return send_file(note.file_path, as_attachment=True, download_name=filename)
        except FileNotFoundError:
            return jsonify({'message': 'File not found on server'}), 404
    except:
        return jsonify({'message': 'Invalid token!'}), 401

@app.route('/api/admin/tests', methods=['POST'])
@token_required
def add_test(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    data = request.get_json()
    name = data.get('name')
    subject = data.get('subject')
    class_level = data.get('class_level')
    date_str = data.get('date')
    max_marks = data.get('max_marks')
    
    try:
        test_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format!'}), 400
    
    new_test = Test(
        name=name,
        subject=subject,
        class_level=class_level,
        date=test_date,
        max_marks=max_marks
    )
    
    db.session.add(new_test)
    db.session.commit()
    
    return jsonify({
        'message': 'Test added successfully',
        'test_id': new_test.id
    })

@app.route('/api/admin/tests/<int:test_id>/results', methods=['POST'])
@token_required
def add_test_results(current_user, is_admin, test_id):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    test = Test.query.get(test_id)
    if not test:
        return jsonify({'message': 'Test not found!'}), 404
    
    data = request.get_json()
    results = data.get('results')
    
    for result in results:
        student_id = result.get('student_id')
        marks_obtained = result.get('marks_obtained')
        
        # Check if result already exists
        test_result = TestResult.query.filter_by(
            test_id=test_id,
            student_id=student_id
        ).first()
        
        if test_result:
            test_result.marks_obtained = marks_obtained
        else:
            test_result = TestResult(
                test_id=test_id,
                student_id=student_id,
                marks_obtained=marks_obtained
            )
            db.session.add(test_result)
    
    db.session.commit()
    
    return jsonify({'message': 'Test results added successfully'})

@app.route('/api/student/tests', methods=['GET'])
@token_required
def get_student_tests(current_user, is_admin):
    if is_admin:
        return jsonify({'message': 'Not accessible by admin!'}), 403
    
    student = current_user
    results = TestResult.query.filter_by(student_id=student.id).all()
    result_data = []
    
    for result in results:
        result_data.append({
            'test_name': result.test.name,
            'subject': result.test.subject,
            'date': result.test.date.strftime('%Y-%m-%d'),
            'max_marks': result.test.max_marks,
            'marks_obtained': result.marks_obtained
        })
    
    return jsonify(result_data)

@app.route('/api/admin/tests', methods=['GET'])
@token_required
def get_tests(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    tests = Test.query.all()
    result = []
    
    for test in tests:
        result.append({
            'id': test.id,
            'name': test.name,
            'subject': test.subject,
            'class_level': test.class_level,
            'date': test.date.strftime('%Y-%m-%d'),
            'max_marks': test.max_marks
        })
    
    return jsonify(result)

@app.route('/api/student/test-results/<int:test_result_id>/pdf', methods=['GET'])
@token_required
def get_test_result_pdf(current_user, is_admin, test_result_id):
    if is_admin:
        return jsonify({'message': 'Not accessible by admin!'}), 403
    
    try:
        test_result = TestResult.query.get(test_result_id)
        if not test_result:
            return jsonify({'message': 'Test result not found!'}), 404
        
        if not test_result.pdf_path or not os.path.exists(test_result.pdf_path):
            # Generate PDF
            test_results_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'test_results')
            os.makedirs(test_results_dir, exist_ok=True)
            
            # Create a PDF with a unique timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{test_result.test.name}_{test_result.student.name}_{timestamp}.pdf"
            file_path = os.path.join(test_results_dir, filename)
            
            # Generate PDF using reportlab
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Create content
            content = []
            
            # Add title
            title = Paragraph(f"Test Result: {test_result.test.name}", styles['Title'])
            content.append(title)
            
            # Add details
            content.append(Paragraph(f"<b>Student:</b> {test_result.student.name}", styles['Normal']))
            content.append(Paragraph(f"<b>Subject:</b> {test_result.test.subject}", styles['Normal']))
            content.append(Paragraph(f"<b>Class:</b> {test_result.test.class_level}", styles['Normal']))
            content.append(Paragraph(f"<b>Date:</b> {test_result.test.date.strftime('%Y-%m-%d')}", styles['Normal']))
            content.append(Spacer(1, 0.25*inch))
            content.append(Paragraph(f"<b>Maximum Marks:</b> {test_result.test.max_marks}", styles['Normal']))
            content.append(Paragraph(f"<b>Marks Obtained:</b> {test_result.marks_obtained}", styles['Normal']))
            
            percentage = (test_result.marks_obtained / test_result.test.max_marks) * 100
            content.append(Paragraph(f"<b>Percentage:</b> {percentage:.2f}%", styles['Normal']))
            
            # Build PDF
            try:
                doc.build(content)
                print(f"Student PDF generated successfully at: {file_path}")
            except Exception as e:
                print(f"Error building student PDF: {str(e)}")
                return jsonify({'message': f'Error building PDF: {str(e)}'}), 500
                
            # Make path absolute if it's not already
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
                
            test_result.pdf_path = file_path
            db.session.commit()
        
        try:
            filename = os.path.basename(test_result.pdf_path)
            return send_file(
                test_result.pdf_path, 
                as_attachment=True, 
                download_name=filename,
                mimetype='application/pdf'
            )
        except FileNotFoundError:
            return jsonify({'message': 'PDF file not found on server'}), 404
    except Exception as e:
        # Log the error
        print(f"Student PDF Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error generating or downloading PDF: {str(e)}'}), 500

@app.route('/api/admin/select-class', methods=['POST'])
@token_required
def select_class(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    data = request.get_json()
    class_level = data.get('class_level')
    
    if not class_level:
        return jsonify({'message': 'Class level is required!'}), 400
    
    # Update admin's selected class
    admin = Admin.query.get(current_user.id)
    admin.selected_class = class_level
    db.session.commit()
    
    return jsonify({'message': f'Class {class_level} selected successfully!'})

@app.route('/api/admin/current-class', methods=['GET'])
@token_required
def get_current_class(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    admin = Admin.query.get(current_user.id)
    
    return jsonify({
        'selected_class': admin.selected_class
    })

@app.route('/api/admin/class-students', methods=['GET'])
@token_required
def get_class_students(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    admin = Admin.query.get(current_user.id)
    if not admin.selected_class:
        return jsonify({'message': 'No class selected!'}), 400
    
    students = Student.query.filter_by(class_level=admin.selected_class).all()
    result = []
    
    for student in students:
        result.append({
            'id': student.id,
            'admission_number': student.admission_number,
            'name': student.name,
            'email': student.email,
            'phone': student.phone,
            'school_name': student.school_name,
            'class_level': student.class_level,
            'admission_date': student.admission_date.strftime('%Y-%m-%d'),
            'has_admission_form': bool(student.admission_form_path)
        })
    
    return jsonify(result)

@app.route('/api/admin/class-tests', methods=['GET'])
@token_required
def get_class_tests(current_user, is_admin):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    admin = Admin.query.get(current_user.id)
    if not admin.selected_class:
        return jsonify({'message': 'No class selected!'}), 400
    
    tests = Test.query.filter_by(class_level=admin.selected_class).all()
    result = []
    
    for test in tests:
        result.append({
            'id': test.id,
            'name': test.name,
            'subject': test.subject,
            'class_level': test.class_level,
            'date': test.date.strftime('%Y-%m-%d'),
            'max_marks': test.max_marks
        })
    
    return jsonify(result)

@app.route('/api/admin/generate-test-results-pdf/<int:test_id>', methods=['POST'])
@token_required
def generate_test_results_pdf(current_user, is_admin, test_id):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'message': 'Test not found!'}), 404
        
        # Get all results for this test
        results = TestResult.query.filter_by(test_id=test_id).all()
        if not results:
            return jsonify({'message': 'No results found for this test!'}), 404
        
        # Ensure the directory exists
        test_results_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'test_results')
        os.makedirs(test_results_dir, exist_ok=True)
        
        # Create a unique filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{test.class_level}_{test.subject}_{test.name}_{timestamp}_results.pdf"
        file_path = os.path.join(test_results_dir, filename)
        
        # Create PDF directly to file instead of using memory buffer
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Check if Title style already exists before adding
        title_style = None
        for style_name in styles.byName:
            if style_name == 'Title':
                title_style = styles['Title']
                break
                
        if not title_style:
            # Only add if not already defined
            styles.add(ParagraphStyle(name='Title', 
                                    fontName='Helvetica-Bold',
                                    fontSize=16, 
                                    alignment=1,
                                    spaceAfter=20))
        
        # Create content
        content = []
        
        # Add title
        title = Paragraph(f"Padashetty Coaching Class - {test.name} Results", styles['Title'])
        content.append(title)
        
        # Add test details
        content.append(Paragraph(f"<b>Subject:</b> {test.subject}", styles['Normal']))
        content.append(Paragraph(f"<b>Class:</b> {test.class_level}", styles['Normal']))
        content.append(Paragraph(f"<b>Date:</b> {test.date.strftime('%Y-%m-%d')}", styles['Normal']))
        content.append(Paragraph(f"<b>Maximum Marks:</b> {test.max_marks}", styles['Normal']))
        content.append(Spacer(1, 0.25*inch))
        
        # Create table data
        data = [['Student Name', 'Admission Number', 'Phone', 'Marks Obtained', 'Percentage']]
        
        for result in results:
            student = Student.query.get(result.student_id)
            if student:
                percentage = (result.marks_obtained / test.max_marks) * 100
                data.append([
                    student.name,
                    student.admission_number,
                    student.phone or 'N/A',
                    str(result.marks_obtained),
                    f"{percentage:.2f}%"
                ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(table)
        
        # Add WhatsApp sharing info
        content.append(Spacer(1, 0.5*inch))
        content.append(Paragraph("<b>Join our WhatsApp group for more updates:</b>", styles['Normal']))
        content.append(Paragraph(app.config['WHATSAPP_GROUP_LINK'], styles['Normal']))
        
        # Build PDF directly to file
        try:
            doc.build(content)
            print(f"PDF generated successfully at: {file_path}")
        except Exception as e:
            print(f"Error building PDF: {str(e)}")
            return jsonify({'message': f'Error building PDF: {str(e)}'}), 500
        
        # Make path absolute if it's not already
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        # Verify the file exists
        if not os.path.exists(file_path):
            return jsonify({'message': 'Failed to create PDF file'}), 500
            
        # Update all test results with the PDF path
        for result in results:
            result.pdf_path = file_path
        
        db.session.commit()
        
        return jsonify({
            'message': 'Test results PDF generated successfully!',
            'pdf_url': f'/api/admin/test-results-pdf/{test_id}'
        })
    
    except Exception as e:
        # Log the error
        print(f"PDF Generation Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error generating PDF: {str(e)}'}), 500

@app.route('/api/admin/test-results-pdf/<int:test_id>', methods=['GET'])
def download_test_results_pdf(test_id):
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'message': 'Test not found!'}), 404
        
        # Get first result to get the PDF path
        result = TestResult.query.filter_by(test_id=test_id).first()
        if not result or not result.pdf_path:
            return jsonify({'message': 'PDF not found!'}), 404
        
        # Check if file exists
        if not os.path.exists(result.pdf_path):
            return jsonify({'message': 'PDF file not found on server!'}), 404
        
        # Get the filename for download
        filename = os.path.basename(result.pdf_path)
        
        # Use a direct file path
        try:
            print(f"Sending file: {result.pdf_path}")
            response = send_file(
                path_or_file=result.pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
            return response
        except Exception as e:
            print(f"Error sending file: {str(e)}")
            return jsonify({'message': f'Error sending PDF: {str(e)}'}), 500
    except Exception as e:
        # Log the error
        print(f"PDF Download Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error downloading PDF: {str(e)}'}), 500

@app.route('/api/admin/share-results-whatsapp/<int:test_id>', methods=['GET'])
@token_required
def share_results_whatsapp(current_user, is_admin, test_id):
    if not is_admin:
        return jsonify({'message': 'Not authorized!'}), 403
    
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'message': 'Test not found!'}), 404
        
        # Get first result to get the PDF path
        result = TestResult.query.filter_by(test_id=test_id).first()
        if not result or not result.pdf_path or not os.path.exists(result.pdf_path):
            return jsonify({'message': 'Generate PDF first!'}), 400
        
        # Mark as shared to WhatsApp
        results = TestResult.query.filter_by(test_id=test_id).all()
        for result in results:
            result.shared_to_whatsapp = True
        
        db.session.commit()
        
        # Prepare a direct WhatsApp sharing link with URL encoding
        text = f"Test results for {test.name} ({test.class_level} class) in {test.subject} are ready! Max marks: {test.max_marks}"
        encoded_text = urllib.parse.quote(text)
        whatsapp_share_link = f"https://wa.me/?text={encoded_text}"
        
        # Return WhatsApp group link and share link
        print(f"WhatsApp share link: {whatsapp_share_link}")
        return jsonify({
            'whatsapp_link': app.config['WHATSAPP_GROUP_LINK'],
            'whatsapp_share_link': whatsapp_share_link,
            'message': f'Test results for {test.name} are ready to share!'
        })
    except Exception as e:
        # Log the error
        print(f"WhatsApp Sharing Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Error preparing WhatsApp sharing: {str(e)}'}), 500

# Initialize database with admin user
def create_tables_and_admin():
    with app.app_context():
        # Create tables if they don't exist
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

if __name__ == '__main__':
    create_tables_and_admin()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
