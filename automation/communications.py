import json
import smtplib
from email.message import EmailMessage
from utils.logger import get_logger

logger = get_logger(__name__)

class CommunicationsManager:
    def send_message(self, target_json: str) -> str:
        """
        Sends a message via the specified platform.
        Currently supports 'email' as a basic implementation.
        """
        try:
            data = json.loads(target_json)
            platform = data.get('platform', '').lower()
            contact = data.get('contact')
            text = data.get('text')
            
            if platform == 'email':
                return self._send_email(contact, text)
            else:
                return f"Platform '{platform}' is not supported yet."
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return "Failed to parse message details."

    def _send_email(self, to_email: str, text: str) -> str:
        """Simple SMTP email sender. (Mocked for safety/simplicity unless configured)"""
        # In a real scenario, we would read SMTP_SERVER, SMTP_USER, SMTP_PASS from settings.
        # For this demonstration, we'll just log it.
        logger.info(f"Mock sending email to {to_email}: {text}")
        
        # Uncomment and configure below for real email
        """
        msg = EmailMessage()
        msg.set_content(text)
        msg['Subject'] = 'Message from REETA'
        msg['From'] = "reeta@example.com"
        msg['To'] = to_email

        try:
            s = smtplib.SMTP('localhost') # Or your smtp server
            s.send_message(msg)
            s.quit()
            return f"Sent email to {to_email}."
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return "Failed to send email."
        """
        return f"Mocked: Sent email to {to_email}."
