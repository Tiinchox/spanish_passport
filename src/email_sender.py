import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

class EmailSender:
    def __init__(self, api_key, sender_email, recipient_email):
        self.api_key = api_key
        self.sender_email = sender_email
        self.recipient_email = recipient_email

    def send(self, subject, message):
        """Send email using SendGrid with proper formatting"""
        try:
            sg = SendGridAPIClient(self.api_key)
            
            # Create email components
            from_email = Email(self.sender_email)
            to_email = To(self.recipient_email)
            content = Content("text/plain", message)
            
            # Create mail object with all components
            mail = Mail(from_email, to_email, subject, content)
            
            # Send email
            response = sg.send(mail)
            logging.info(f"Email sent successfully. Status code: {response.status_code}")
            return True
        except Exception as e:
            logging.error(f"Error sending email: {e}")
            return False 