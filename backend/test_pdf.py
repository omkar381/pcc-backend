"""
Test script to verify PDF generation capability.
This script creates a simple PDF to test if reportlab is working correctly.
"""

import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def test_pdf_generation():
    # Create a directory for test files if it doesn't exist
    os.makedirs('test_output', exist_ok=True)
    
    # Create a PDF in memory
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Add some text
    can.drawString(100, 750, "Test PDF Generation")
    can.drawString(100, 700, "If you can see this, reportlab is working correctly!")
    
    # Save the PDF
    can.save()
    
    # Get the PDF data
    packet.seek(0)
    pdf_data = packet.read()
    
    # Write to file
    with open('test_output/test.pdf', 'wb') as f:
        f.write(pdf_data)
    
    print("PDF file created successfully at 'test_output/test.pdf'")
    print("If the file exists and can be opened, reportlab is working correctly.")

if __name__ == '__main__':
    test_pdf_generation() 