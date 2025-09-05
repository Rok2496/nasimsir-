import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT"))
        self.smtp_email = os.getenv("SMTP_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
        
        # Setup Jinja2 for email templates
        self.env = Environment(loader=FileSystemLoader('templates/email'))
    
    async def send_order_notification(self, order_data: dict, customer_data: dict):
        """Send order notification to admin and customer"""
        
        # Send to admin
        await self._send_admin_notification(order_data, customer_data)
        
        # Send confirmation to customer
        await self._send_customer_confirmation(order_data, customer_data)
    
    async def _send_admin_notification(self, order_data: dict, customer_data: dict):
        """Send order notification to admin"""
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
    
    async def _send_customer_confirmation(self, order_data: dict, customer_data: dict):
        """Send order confirmation to customer"""
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
    
    async def _send_email(self, to_email: str, subject: str, html_content: str):
        """Send email using SMTP"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.smtp_email
        message["To"] = to_email
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        try:
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_email,
                password=self.smtp_password,
            )
            print(f"Email sent successfully to {to_email}")
        except Exception as e:
            print(f"Email sending failed: {e}")
            raise e