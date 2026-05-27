import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_email_alert(target_url: str, label: str) -> bool:
    """Connects via SMTP over TLS to securely send content modification alert emails."""
    # Load parameters from environment variables
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    to_email = os.getenv("ALERT_EMAIL_TO")

    # Guard clause checking if parameters are present
    if not all([smtp_host, smtp_port, smtp_user, smtp_pass, to_email]):
        print("[!] Email Alert skipped: SMTP credentials incomplete.")
        return False

    # Structure the standard MIME mail message
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = f"SecureScraper Alert: Change Detected in {label}"

    body = f"SecureScraper has detected a content change at the following target:\n\nLabel: {label}\nURL: {target_url}\n\nPlease check the dashboard or target page for updates."
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Open standard secure socket layer connection
        server = smtplib.SMTP(smtp_host, int(smtp_port), timeout=10)
        server.starttls() # Secure the connection using Transport Layer Security
        server.login(smtp_user, smtp_pass)
        server.send_mail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[!] Failed to dispatch email alert: {e}")
        return False