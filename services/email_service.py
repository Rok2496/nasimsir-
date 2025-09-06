import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_email = os.getenv("SMTP_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
        
        # Setup Jinja2 for email templates - fix the directory path
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'email')
        logger.info(f"Looking for email templates in: {template_dir}")
        self.env = Environment(loader=FileSystemLoader(template_dir))
    
    async def send_order_notification(self, order_data: dict, customer_data: dict):
        """Send order notification to admin and customer"""
        try:
            # Send to admin
            await self._send_admin_notification(order_data, customer_data)
            
            # Send confirmation to customer
            await self._send_customer_confirmation(order_data, customer_data)
        except Exception as e:
            logger.error(f"Failed to send email notifications: {e}")
            raise e
    
    async def _send_admin_notification(self, order_data: dict, customer_data: dict):
        """Send order notification to admin"""
        try:
            subject = f"New Order #{order_data['id']} - SmartTech Interactive Board"
            
            template = self.env.get_template('admin_order_notification.html')
            html_content = template.render(
                order=order_data,
                customer=customer_data
            )
            
            await self._send_email(
                to_email=self.recipient_email,
                subject=subject,
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"Failed to send admin notification: {e}")
            raise e
    
    async def _send_customer_confirmation(self, order_data: dict, customer_data: dict):
        """Send order confirmation to customer"""
        try:
            subject = f"Order Confirmation #{order_data['id']} - SmartTech"
            
            template = self.env.get_template('customer_order_confirmation.html')
            html_content = template.render(
                order=order_data,
                customer=customer_data
            )
            
            await self._send_email(
                to_email=customer_data['email'],
                subject=subject,
                html_content=html_content
            )
        except Exception as e:
            logger.error(f"Failed to send customer confirmation: {e}")
            raise e
    
    async def _send_email(self, to_email: str, subject: str, html_content: str):
        """Send email using SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.smtp_email
            message["To"] = to_email
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_email,
                password=self.smtp_password,
            )
            logger.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            raise e