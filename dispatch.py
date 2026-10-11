import smtplib
import csv
from email.message import EmailMessage
import time
import datetime
import random
import os
import glob

# Try to import schedule, install if not available
try:
    import schedule
except ImportError:
    print("Installing required library: schedule")
    os.system("pip install schedule")
    import schedule

# ========== YOUR SETTINGS (CHANGE THESE) ==========
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "hided_emil@gmail.com"  # CHANGE THIS
SENDER_PASSWORD = "hided"  # CHANGE THIS (no spaces)

# Email settings
USE_HTML = True
SUBJECT = "Automated Email Dispatch"

# Delay settings (seconds)
MIN_DELAY = 3
MAX_DELAY = 7

# ========== FEATURE 6: MULTIPLE ATTACHMENTS (OPTIONAL) ==========
SEND_ATTACHMENTS = False  # Set to True ONLY when you need attachments

# List files here - only used if SEND_ATTACHMENTS = True
ATTACHMENT_FILES = [
    # "report.pdf",      # Uncomment when needed
    # "invoice.pdf",     # Uncomment when needed
]

# ========== FEATURE 7: TEMPLATES FROM FILES ==========
TEMPLATE_FOLDER = "templates"
TEMPLATE_NAME = "newsletter"  # Change to: "welcome", "newsletter", "invoice", etc.

# ========== FEATURE 8: GROUP SENDING ==========
FILTER_DEPARTMENT = "Sales"  # Change to specific department like "Sales"

# ========== FEATURE 9: SCHEDULE SENDING ==========
SCHEDULE_TIME = None  # Set to "09:00" to enable scheduling
SCHEDULE_DAY = None   # Set to "monday", "tuesday", etc.

# ================================================

# Default HTML template
DEFAULT_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #0066cc, #004499); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #888; }}
        .highlight {{ color: #0066cc; font-weight: bold; }}
        .time {{ color: #28a745; font-size: 14px; }}
        hr {{ border: none; border-top: 2px solid #0066cc; margin: 20px 0; }}
        .department {{ background: #e7f3ff; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Automated Email Dispatch</h2>
        </div>
        <div class="content">
            <h2>Hello <span class="highlight">{name}</span>!</h2>
            <p>This is an <b>automated email</b> from your dispatch system.</p>
            
            <div class="department">
                <strong>Department:</strong> {department}
            </div>
            
            <p>Your automated report has been generated successfully.</p>
            <p class="time"><strong>Sent at:</strong> {current_time}</p>
            <hr>
            <p>This is an automated message - no reply needed.</p>
        </div>
        <div class="footer">
            <p>2026 Automated Email System</p>
        </div>
    </div>
</body>
</html>
"""

def load_html_template():
    """Feature 7: Load HTML template from file"""
    template_path = os.path.join(TEMPLATE_FOLDER, f"{TEMPLATE_NAME}.html")
    
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"[TEMPLATE] Loaded: {template_path}")
        return content
    else:
        print(f"[TEMPLATE] Using default template")
        return DEFAULT_HTML_TEMPLATE

def attach_multiple_files(msg):
    """Feature 6: Attach multiple files ONLY if enabled"""
    if not SEND_ATTACHMENTS:
        return 0
    
    attached_count = 0
    
    for file_path in ATTACHMENT_FILES:
        if not file_path:
            continue
            
        if os.path.exists(file_path):
            try:
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext == '.pdf':
                    maintype = "application"
                    subtype = "pdf"
                elif file_ext in ['.jpg', '.jpeg']:
                    maintype = "image"
                    subtype = "jpeg"
                elif file_ext == '.png':
                    maintype = "image"
                    subtype = "png"
                else:
                    maintype = "application"
                    subtype = "octet-stream"
                
                with open(file_path, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype=maintype,
                        subtype=subtype,
                        filename=os.path.basename(file_path)
                    )
                attached_count += 1
                print(f"   Attached: {file_path}")
            except Exception as e:
                print(f"   WARNING: Could not attach {file_path}: {e}")
        else:
            print(f"   WARNING: File not found: {file_path}")
    
    return attached_count

def log_result(message):
    """Write results to log.txt and print to console"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} - {message}\n")
    print(f"{timestamp} - {message}")

def send_email(recipient, name, department):
    """Send email with optional attachments"""
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient
    msg["Subject"] = f"{SUBJECT} - {name}"
    
    current_time = datetime.datetime.now().strftime("%I:%M %p on %B %d, %Y")
    
    html_template = load_html_template()
    
    template_vars = {
        "name": name,
        "department": department,
        "current_time": current_time
    }
    
    html_body = html_template.format(**template_vars)
    msg.set_content(f"Hello {name},\n\nThis is an automated email. Please enable HTML to view properly.\n\nDepartment: {department}\nSent at: {current_time}")
    msg.add_alternative(html_body, subtype="html")
    
    if SEND_ATTACHMENTS:
        attached = attach_multiple_files(msg)
        if attached > 0:
            log_result(f"[ATTACH] {attached} file(s) attached for {name}")
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        log_result(f"[SUCCESS] Sent to {name} ({recipient}) - Dept: {department}")
        return True
    except Exception as e:
        log_result(f"[FAILED] {name} ({recipient}) - Error: {str(e)}")
        return False

def filter_by_group(recipients):
    """Feature 8: Filter recipients by department"""
    if FILTER_DEPARTMENT == "All":
        return recipients
    
    filtered = []
    for row in recipients:
        if row["department"] == FILTER_DEPARTMENT:
            filtered.append(row)
    
    print(f"\n[FILTER] Sending only to '{FILTER_DEPARTMENT}' department")
    print(f"[FILTER] Found {len(filtered)} recipients out of {len(recipients)} total")
    return filtered

def send_batch_emails():
    """Main function to send all emails"""
    print("\n" + "="*60)
    print("AUTOMATED EMAIL DISPATCHER (PROFESSIONAL EDITION)")
    print("="*60)
    print(f"HTML Mode: {'ON' if USE_HTML else 'OFF'}")
    
    if SEND_ATTACHMENTS:
        print(f"Attachments: ENABLED - {len(ATTACHMENT_FILES)} file(s) configured")
    else:
        print(f"Attachments: DISABLED")
    
    print(f"Template: {TEMPLATE_NAME}")
    print(f"Department Filter: {FILTER_DEPARTMENT}")
    print(f"Random Delay: {MIN_DELAY}-{MAX_DELAY} seconds")
    if SCHEDULE_TIME:
        print(f"Scheduled: {SCHEDULE_TIME}")
    print("="*60 + "\n")
    
    try:
        with open("emails.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            all_recipients = list(reader)
            
            recipients = filter_by_group(all_recipients)
            total_emails = len(recipients)
            success_count = 0
            
            if total_emails == 0:
                print(f"WARNING: No recipients found for department '{FILTER_DEPARTMENT}'")
                return
            
            for index, row in enumerate(recipients, 1):
                name = row["name"]
                email = row["email"]
                department = row["department"]
                
                print(f"\n[{index}/{total_emails}] Sending to: {name} ({department})")
                success = send_email(email, name, department)
                
                if success:
                    success_count += 1
                
                if index < total_emails:
                    wait_time = random.randint(MIN_DELAY, MAX_DELAY)
                    print(f"   Waiting {wait_time} seconds before next email...")
                    time.sleep(wait_time)
            
            print("\n" + "="*60)
            print(f"COMPLETE! Success: {success_count}/{total_emails} emails sent")
            print(f"Failed: {total_emails - success_count} emails")
            print(f"Detailed log saved to 'log.txt'")
            print("="*60)
            
    except FileNotFoundError:
        print("ERROR: emails.csv not found!")
        print("   Create emails.csv with columns: name,email,department")
    except Exception as e:
        print(f"Unexpected error: {e}")

def setup_templates_folder():
    """Create templates folder with example templates"""
    if not os.path.exists(TEMPLATE_FOLDER):
        os.makedirs(TEMPLATE_FOLDER)
        print(f"[SETUP] Created '{TEMPLATE_FOLDER}' folder")
        
        templates_examples = {
            "default": DEFAULT_HTML_TEMPLATE,
            "welcome": """
<!DOCTYPE html>
<html>
<body>
<h2>Welcome {name}!</h2>
<p>Thank you for joining our {department} team.</p>
<p>We're excited to have you on board!</p>
<p>Sent at: {current_time}</p>
</body>
</html>
""",
            "newsletter": """
<!DOCTYPE html>
<html>
<body>
<h2>Monthly Newsletter - {current_time}</h2>
<p>Hello {name},</p>
<p>Here's what's happening in {department} department this month...</p>
<hr>
<p>Thanks for reading!</p>
</body>
</html>
""",
            "invoice": """
<!DOCTYPE html>
<html>
<body>
<h2>Invoice for {name}</h2>
<p>Department: {department}</p>
<p>Please find your invoice attached.</p>
<p>Due date: End of month</p>
</body>
</html>
"""
        }
        
        for name, content in templates_examples.items():
            filepath = os.path.join(TEMPLATE_FOLDER, f"{name}.html")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[SETUP] Created template: {filepath}")

def run_scheduled():
    """Run scheduled dispatch"""
    print(f"\n[SCHEDULE] Running scheduled dispatch at {datetime.datetime.now()}")
    send_batch_emails()

def setup_schedule():
    """Setup automated schedule"""
    if not SCHEDULE_TIME:
        return False
    
    if SCHEDULE_DAY:
        if SCHEDULE_DAY == "monday":
            schedule.every().monday.at(SCHEDULE_TIME).do(run_scheduled)
        elif SCHEDULE_DAY == "tuesday":
            schedule.every().tuesday.at(SCHEDULE_TIME).do(run_scheduled)
        elif SCHEDULE_DAY == "wednesday":
            schedule.every().wednesday.at(SCHEDULE_TIME).do(run_scheduled)
        elif SCHEDULE_DAY == "thursday":
            schedule.every().thursday.at(SCHEDULE_TIME).do(run_scheduled)
        elif SCHEDULE_DAY == "friday":
            schedule.every().friday.at(SCHEDULE_TIME).do(run_scheduled)
        elif SCHEDULE_DAY == "saturday":
            schedule.every().saturday.at(SCHEDULE_TIME).do(run_scheduled)
        elif SCHEDULE_DAY == "sunday":
            schedule.every().sunday.at(SCHEDULE_TIME).do(run_scheduled)
        print(f"[SCHEDULE] Will send emails every {SCHEDULE_DAY} at {SCHEDULE_TIME}")
    else:
        schedule.every().day.at(SCHEDULE_TIME).do(run_scheduled)
        print(f"[SCHEDULE] Will send emails daily at {SCHEDULE_TIME}")
    
    return True

def main():
    # Setup templates folder if needed
    setup_templates_folder()
    
    # Show attachment status
    print("\n" + "="*50)
    print("ATTACHMENT STATUS")
    print("="*50)
    if SEND_ATTACHMENTS:
        print(f"Attachments: ENABLED")
        if ATTACHMENT_FILES:
            print(f"  Files to send: {[f for f in ATTACHMENT_FILES if f]}")
        else:
            print(f"  WARNING: No files listed in ATTACHMENT_FILES")
    else:
        print(f"Attachments: DISABLED")
        print(f"  To enable attachments, set SEND_ATTACHMENTS = True")
    print("="*50 + "\n")
    
    # Ask user about schedule - using local variables to avoid global issue
    local_schedule_time = SCHEDULE_TIME
    local_schedule_day = SCHEDULE_DAY
    
    if not local_schedule_time:
        schedule_choice = input("\nDo you want to schedule this script? (y/n): ").lower()
        if schedule_choice == 'y':
            time_input = input("Enter time (HH:MM, e.g., 09:00): ")
            day_input = input("Enter day (monday/tuesday/etc.) or press Enter for daily: ").lower()
            
            local_schedule_time = time_input
            local_schedule_day = day_input if day_input else None
    
    # Setup and run using local variables
    if local_schedule_time:
        # Store in the global variables for the schedule function to use
        globals()['SCHEDULE_TIME'] = local_schedule_time
        globals()['SCHEDULE_DAY'] = local_schedule_day
        
        if setup_schedule():
            print(f"\n[SCHEDULE] Script is running. Press Ctrl+C to stop.")
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n[SCHEDULE] Stopped by user")
    else:
        send_batch_emails()

if __name__ == "__main__":
    main()