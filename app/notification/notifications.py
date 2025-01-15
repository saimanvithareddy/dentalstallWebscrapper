from abc import ABC, abstractmethod
from typing import Dict
from abc import ABC, abstractmethod
from typing import Dict
import smtplib
from email.mime.text import MIMEText
import logging

class NotificationStrategy(ABC):
    @abstractmethod
    def notify(self, message: str) -> None:
        pass

class ConsoleNotification(NotificationStrategy):
    def notify(self, message: str) -> None:
        print(f"Scraping Notification: {message}")

class EmailNotification(NotificationStrategy):
    def __init__(self, smtp_settings: Dict):
        self.smtp_server = smtp_settings['smtp_server']
        self.smtp_port = smtp_settings['smtp_port']
        self.sender_email = smtp_settings['sender_email']
        self.sender_password = smtp_settings['sender_password']
        self.recipients = smtp_settings['recipients']

    def notify(self, message: str) -> None:
        try:
            # Create message
            msg = MIMEText(message)
            msg['Subject'] = 'Web Scraping Update'
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                
            logging.info(f"Email notification sent to {', '.join(self.recipients)}")
        except Exception as e:
            logging.error(f"Failed to send email notification: {str(e)}")