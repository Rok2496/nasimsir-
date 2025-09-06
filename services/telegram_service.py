import httpx
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Log initialization
        logger.info(f"TelegramService initialized with bot token: {self.bot_token[:10]}... and chat_id: {self.chat_id}")
    
    async def send_order_notification(self, order_data: dict, customer_data: dict):
        """Send order notification to Telegram"""
        try:
            message = self._format_order_message(order_data, customer_data)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": "HTML"
                    }
                )
                response.raise_for_status()
                logger.info("Telegram notification sent successfully")
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")
            raise e
    
    def _format_order_message(self, order_data: dict, customer_data: dict) -> str:
        """Format order data for Telegram message"""
        return f"""
🛒 <b>New Order Received!</b>

📋 <b>Order Details:</b>
• Order ID: #{order_data['id']}
• Product: {order_data['product_name']}
• Quantity: {order_data['quantity']}
• Total: ${order_data['total_price']:.2f}
• Status: {order_data['status']}

👤 <b>Customer Information:</b>
• Name: {customer_data['full_name']}
• Email: {customer_data['email']}
• Phone: {customer_data['phone']}
• Address: {customer_data.get('address', 'N/A')}
• City: {customer_data.get('city', 'N/A')}

📝 <b>Special Requirements:</b>
{order_data.get('special_requirements', 'None')}

🚚 <b>Delivery Address:</b>
{order_data.get('delivery_address', 'Same as customer address')}

📅 <b>Order Date:</b> {order_data['order_date']}
        """.strip()