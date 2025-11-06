"""
Monthly OD Report Generator
Generates and sends Excel reports to faculty with student OD proof submission status
"""

import os
from datetime import datetime, timedelta
from flask import Flask
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from flask_mail import Mail, Message

def generate_monthly_od_report(db, Student, ODRequest, Faculty, ProofStatus, mail):
    """
    Generate Excel report with OD proof submission status
    Returns BytesIO object containing the Excel file
    """
    
    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "OD Proof Status Report"
    
    # Get current month and year
    now = datetime.now()
    month_name = now.strftime("%B %Y")
    
    # Report title
    ws.merge_cells('A1:J1')
    title_cell = ws['A1']
    title_cell.value = f"KGiSL Institute of Technology - Monthly OD Report ({month_name})"
    title_cell.font = Font(size=16, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 30
    
    # Report generation info
    ws.merge_cells('A2:J2')
    info_cell = ws['A2']
    info_cell.value = f"Generated on: {now.strftime('%d-%m-%Y %I:%M %p')}"
    info_cell.font = Font(size=10, italic=True)
    info_cell.alignment = Alignment(horizontal='center')
    ws.row_dimensions[2].height = 20
    
    # Headers
    headers = [
        'S.No',
        'Student Name',
        'Roll Number',
        'Department',
        'Event Name',
        'Event Date',
        'Status',
        'Attendance Proof',
        'Certificate',
        'Pending Action'
    ]
    
    header_row = 4
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col_num)
        cell.value = header
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    ws.row_dimensions[header_row].height = 25
    
    # Get all approved OD requests with pending proofs
    requests = ODRequest.query.filter(
        ODRequest.status == 'approved'
    ).order_by(ODRequest.created_at.desc()).all()
    
    # Data rows
    row_num = header_row + 1
    s_no = 1
    
    for request in requests:
        student = request.student
        
        # Determine proof status
        attendance_status = "Submitted" if request.attendance_proof_filename else "Pending"
        certificate_status = "Submitted" if request.certificate_filename else "Pending"
        
        # Determine pending action
        if request.proof_submission_status == ProofStatus.attendance_pending:
            pending_action = "Attendance Proof Required"
        elif request.proof_submission_status == ProofStatus.certificate_pending:
            pending_action = "Certificate Required"
        elif request.proof_submission_status == ProofStatus.COMPLETED:
            pending_action = "Completed"
        else:
            pending_action = "Not Started"
        
        # Write data
        data = [
            s_no,
            student.name if student else "N/A",
            student.roll_number if student else "N/A",
            student.department if student else "N/A",
            request.event_name,
            request.from_date.strftime('%d-%m-%Y') if request.from_date else "N/A",
            request.status.title(),
            attendance_status,
            certificate_status,
            pending_action
        ]
        
        for col_num, value in enumerate(data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = value
            cell.alignment = Alignment(horizontal='center' if col_num == 1 else 'left', vertical='center')
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Color coding for status columns
            if col_num == 8:  # Attendance Proof
                if value == "Submitted":
                    cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                    cell.font = Font(color="006100")
                else:
                    cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                    cell.font = Font(color="9C0006")
            
            elif col_num == 9:  # Certificate
                if value == "Submitted":
                    cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                    cell.font = Font(color="006100")
                else:
                    cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                    cell.font = Font(color="9C0006")
            
            elif col_num == 10:  # Pending Action
                if value == "Completed":
                    cell.fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
                    cell.font = Font(color="006100", bold=True)
                elif "Required" in value:
                    cell.fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
                    cell.font = Font(color="9C5700", bold=True)
        
        ws.row_dimensions[row_num].height = 20
        row_num += 1
        s_no += 1
    
    # Summary section
    summary_row = row_num + 2
    ws.merge_cells(f'A{summary_row}:D{summary_row}')
    summary_cell = ws[f'A{summary_row}']
    summary_cell.value = "SUMMARY"
    summary_cell.font = Font(size=12, bold=True, color="FFFFFF")
    summary_cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    summary_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Summary data
    total_requests = len(requests)
    attendance_pending = len([r for r in requests if not r.attendance_proof_filename])
    certificate_pending = len([r for r in requests if not r.certificate_filename and r.attendance_proof_filename])
    completed = len([r for r in requests if r.proof_submission_status == ProofStatus.COMPLETED])
    
    summary_data = [
        ("Total Approved ODs:", total_requests),
        ("Attendance Proofs Pending:", attendance_pending),
        ("Certificates Pending:", certificate_pending),
        ("Fully Completed:", completed),
    ]
    
    summary_row += 1
    for label, value in summary_data:
        ws[f'A{summary_row}'] = label
        ws[f'A{summary_row}'].font = Font(bold=True)
        ws[f'B{summary_row}'] = value
        ws[f'B{summary_row}'].font = Font(bold=True)
        summary_row += 1
    
    # Adjust column widths
    column_widths = {
        'A': 8,   # S.No
        'B': 25,  # Student Name
        'C': 15,  # Roll Number
        'D': 30,  # Department
        'E': 35,  # Event Name
        'F': 15,  # Event Date
        'G': 12,  # Status
        'H': 18,  # Attendance Proof
        'I': 18,  # Certificate
        'J': 25,  # Pending Action
    }
    
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width
    
    # Save to BytesIO
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    
    return excel_file


def send_monthly_report_to_faculty(app, db, Student, ODRequest, Faculty, ProofStatus, mail):
    """
    Generate and send monthly OD report to all active faculty members
    """
    with app.app_context():
        print("📊 Starting monthly OD report generation...")
        
        # Generate Excel report
        excel_file = generate_monthly_od_report(db, Student, ODRequest, Faculty, ProofStatus, mail)
        
        # Get all active faculty
        faculty_members = Faculty.query.filter_by(is_active=True).all()
        
        if not faculty_members:
            print("⚠️ No active faculty found")
            return
        
        # Get current month and year
        now = datetime.now()
        month_name = now.strftime("%B %Y")
        
        # Email content
        subject = f"Monthly OD Report - {month_name}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #1F4E78, #366092); padding: 30px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 24px;">KGiSL Institute of Technology</h1>
                <h2 style="margin: 10px 0 0 0; font-size: 18px;">Monthly OD Report</h2>
            </div>
            
            <div style="padding: 30px; background-color: #f8f9fa;">
                <p style="font-size: 16px; color: #333;">Dear Faculty,</p>
                
                <p style="font-size: 14px; color: #555; line-height: 1.6;">
                    Please find attached the monthly On-Duty (OD) report for <strong>{month_name}</strong>. 
                    This report contains details of all approved OD requests and their proof submission status.
                </p>
                
                <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #366092;">
                    <h3 style="margin: 0 0 15px 0; color: #1F4E78;">Report Contents:</h3>
                    <ul style="margin: 0; padding-left: 20px; color: #555;">
                        <li>Student OD details (Name, Roll Number, Department)</li>
                        <li>Event information</li>
                        <li>Attendance proof submission status</li>
                        <li>Certificate submission status</li>
                        <li>Pending actions required from students</li>
                        <li>Summary statistics</li>
                    </ul>
                </div>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; border: 1px solid #ffc107; margin: 20px 0;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        <strong>📌 Note:</strong> Students with pending proofs should be reminded to submit them before the deadline.
                    </p>
                </div>
                
                <p style="font-size: 14px; color: #555;">
                    If you have any questions or need additional information, please contact the administration.
                </p>
                
                <p style="font-size: 14px; color: #555; margin-top: 30px;">
                    Best regards,<br>
                    <strong>OD Management System</strong><br>
                    KGiSL Institute of Technology
                </p>
            </div>
            
            <div style="background-color: #1F4E78; padding: 20px; text-align: center; color: white; font-size: 12px;">
                <p style="margin: 0;">This is an automated report generated by the OD Management System</p>
                <p style="margin: 5px 0 0 0;">Generated on: {now.strftime('%d-%m-%Y %I:%M %p')}</p>
            </div>
        </div>
        """
        
        # Send email to each faculty
        sent_count = 0
        failed_count = 0
        
        for faculty in faculty_members:
            try:
                # Reset file pointer for each email
                excel_file.seek(0)
                
                msg = Message(
                    subject=subject,
                    sender=app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[faculty.email],
                    html=html_content
                )
                
                # Attach Excel file
                filename = f"OD_Report_{month_name.replace(' ', '_')}.xlsx"
                msg.attach(
                    filename,
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    excel_file.read()
                )
                
                mail.send(msg)
                sent_count += 1
                print(f"✅ Report sent to {faculty.name} ({faculty.email})")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to send to {faculty.name} ({faculty.email}): {str(e)}")
        
        print(f"\n📊 Monthly Report Summary:")
        print(f"   Total Faculty: {len(faculty_members)}")
        print(f"   Successfully Sent: {sent_count}")
        print(f"   Failed: {failed_count}")
        
        return sent_count, failed_count


if __name__ == "__main__":
    # This can be run as a standalone script or scheduled as a cron job
    from main import app, db, Student, ODRequest, Faculty, ProofStatus, mail
    
    send_monthly_report_to_faculty(app, db, Student, ODRequest, Faculty, ProofStatus, mail)
