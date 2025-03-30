"""
Deployment Test Script for Padashetty Coaching Class Application

This script tests the environment setup and critical dependencies 
required for deploying the application to Railway.app and Vercel.
"""

import os
import sys
import importlib
import subprocess

def check_module(module_name):
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} is installed")
        return True
    except ImportError:
        print(f"❌ {module_name} is NOT installed")
        return False

def check_directory(directory):
    if os.path.exists(directory):
        if os.path.isdir(directory):
            if os.access(directory, os.W_OK):
                print(f"✅ Directory '{directory}' exists and is writable")
                return True
            else:
                print(f"❌ Directory '{directory}' exists but is NOT writable")
                return False
        else:
            print(f"❌ '{directory}' exists but is NOT a directory")
            return False
    else:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Directory '{directory}' created successfully")
            return True
        except:
            print(f"❌ Failed to create directory '{directory}'")
            return False

def test_pdf_generation():
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        # Test directory
        test_dir = os.path.join('backend', 'test_output')
        if not check_directory(test_dir):
            return False
        
        # Create a simple PDF
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(100, 750, "Deployment Test")
        can.drawString(100, 700, "PDF generation is working!")
        can.save()
        
        # Write to file
        packet.seek(0)
        with open(os.path.join(test_dir, 'deployment_test.pdf'), 'wb') as f:
            f.write(packet.getvalue())
        
        print(f"✅ Successfully generated test PDF in {os.path.join(test_dir, 'deployment_test.pdf')}")
        return True
    except Exception as e:
        print(f"❌ PDF generation failed: {str(e)}")
        return False

def main():
    print("Padashetty Coaching Class Application - Deployment Test")
    print("="*60)
    
    # Check core directories
    print("\n📁 Checking directories...")
    backend_dir_ok = check_directory('backend')
    frontend_dir_ok = check_directory('frontend')
    uploads_dir_ok = check_directory(os.path.join('backend', 'uploads'))
    uploads_forms_ok = check_directory(os.path.join('backend', 'uploads', 'admission_forms'))
    uploads_notes_ok = check_directory(os.path.join('backend', 'uploads', 'notes'))
    uploads_results_ok = check_directory(os.path.join('backend', 'uploads', 'test_results'))
    
    # Check backend dependencies
    print("\n📦 Checking backend dependencies...")
    flask_ok = check_module('flask')
    flask_cors_ok = check_module('flask_cors')
    sqlalchemy_ok = check_module('flask_sqlalchemy')
    reportlab_ok = check_module('reportlab')
    dotenv_ok = check_module('dotenv')
    jwt_ok = check_module('jwt')
    
    # Test PDF generation
    print("\n📄 Testing PDF generation...")
    pdf_ok = test_pdf_generation()
    
    # Print summary
    print("\n📋 Test Summary")
    print("="*60)
    all_ok = all([
        backend_dir_ok, frontend_dir_ok, uploads_dir_ok, 
        uploads_forms_ok, uploads_notes_ok, uploads_results_ok,
        flask_ok, flask_cors_ok, sqlalchemy_ok, reportlab_ok, 
        dotenv_ok, jwt_ok, pdf_ok
    ])
    
    if all_ok:
        print("✅ All tests passed! Your application is ready for deployment.")
    else:
        print("❌ Some tests failed. Fix the issues above before deploying.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 