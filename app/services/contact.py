import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
from app.models import ContactInquiry
from app.services.db import get_db

def handle_contact_submission(name: str, email: str, subject: str, message: str, ip_address: str = None):
    """
    Persists inquiry in database and attempts SMTP dispatch if credentials exist.
    Returns: (success: bool, delivered_via_email: bool, error_message: str)
    """
    db = get_db()
    
    inquiry = ContactInquiry(
        name=name.strip(),
        email=email.strip().lower(),
        subject=subject.strip(),
        message=message.strip(),
        ip_address=ip_address,
        status="new",
        email_delivered=False
    )
    
    db.session.add(inquiry)
    db.session.commit()
    
    smtp_host = current_app.config.get("SMTP_HOST")
    smtp_user = current_app.config.get("SMTP_USER")
    smtp_pass = current_app.config.get("SMTP_PASSWORD")
    recipient = current_app.config.get("CONTACT_RECIPIENT_EMAIL")
    
    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[Critical Save Inquiry] {inquiry.subject}"
            msg["From"] = smtp_user
            msg["To"] = recipient
            msg["Reply-To"] = inquiry.email
            
            body = (
                f"New inquiry received from website:\n\n"
                f"Sender: {inquiry.name} <{inquiry.email}>\n"
                f"Subject: {inquiry.subject}\n"
                f"IP: {inquiry.ip_address}\n\n"
                f"Message:\n{inquiry.message}\n"
            )
            msg.attach(MIMEText(body, "plain", "utf-8"))
            
            port = current_app.config.get("SMTP_PORT", 587)
            server = smtplib.SMTP(smtp_host, port, timeout=10)
            if current_app.config.get("SMTP_USE_TLS", True):
                server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [recipient], msg.as_string())
            server.quit()
            
            inquiry.email_delivered = True
            db.session.commit()
            return True, True, ""
        except Exception as e:
            inquiry.delivery_error = str(e)
            db.session.commit()
            return True, False, f"Inquiry logged in studio queue, but SMTP dispatch encountered an error: {e}"
            
    # If no SMTP configured, inquiry is safely queued in DB
    return True, False, "Inquiry safely stored in database queue. SMTP credentials not configured."
