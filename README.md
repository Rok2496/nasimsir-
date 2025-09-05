# SmartTech E-commerce Backend

A complete FastAPI backend for an Interactive Smart Board e-commerce website with AI chatbot integration.

## Features

- 🛒 **Product Management**: Complete product catalog with images and videos
- 📝 **Order System**: Customer order processing with notifications
- 🤖 **AI Chatbot**: Multi-language customer support using OpenRouter API
- 📧 **Email Notifications**: Automated email notifications to customers and admin
- 📱 **Telegram Integration**: Real-time order notifications via Telegram
- 👨‍💼 **Admin Dashboard**: Complete admin panel for managing orders and products
- 🔐 **Authentication**: JWT-based admin authentication
- 🗄️ **Database**: PostgreSQL with SQLAlchemy ORM

## Product: SmartTech Interactive Smart Board RK3588

### Specifications
- **OS**: Android 12
- **RAM**: 16GB
- **Storage**: 256GB
- **Camera**: 48MP AI camera with facial recognition
- **Audio**: 8 microphones array, 2.1 channel audio
- **Security**: NFC support, Fingerprint scanner
- **Sizes**: 65", 75", 86", 98", 100", 105", 110"
- **Contact**: 01678-134547

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL Database
Make sure PostgreSQL is running and create a database named 'sir':
```sql
CREATE DATABASE sir;
```

### 3. Configure Environment
Update the `.env` file with your actual OpenRouter API key:
```
OPENROUTER_API_KEY=your_actual_openrouter_api_key_here
```

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Run the Application
```bash
python main.py
```

The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## API Endpoints

### Public Endpoints
- `GET /` - Welcome message with product info
- `GET /health` - Health check
- `GET /api/products/` - Get all products
- `GET /api/products/{id}` - Get specific product
- `POST /api/orders/` - Create new order
- `POST /api/chat/` - Chat with AI assistant
- `GET /api/chat/history/{session_id}` - Get chat history

### Admin Endpoints (Requires Authentication)
- `POST /api/admin/login` - Admin login
- `POST /api/admin/register` - Register new admin
- `GET /api/admin/me` - Get current admin info
- `GET /api/orders/` - Get all orders
- `PUT /api/orders/{id}` - Update order status
- `DELETE /api/orders/{id}` - Delete order
- `POST /api/products/` - Create new product
- `PUT /api/products/{id}` - Update product
- `GET /api/dashboard/stats` - Dashboard statistics

### File Upload
- `POST /api/upload/image` - Upload product image
- `POST /api/upload/video` - Upload product video

## Default Admin Credentials
- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the default password after first login!

## AI Chatbot Features

The AI chatbot can:
- Answer product questions in any language
- Help customers with purchase decisions
- Provide technical specifications
- Guide customers through the ordering process
- Handle customer support inquiries

## Order Process

1. Customer fills out order form with personal information
2. System creates customer record and order
3. Automatic notifications sent via:
   - Email to customer (confirmation)
   - Email to admin (new order notification)
   - Telegram message to admin
4. Admin can manage orders through dashboard

## Email Templates

Professional HTML email templates included:
- Customer order confirmation
- Admin order notification

## File Structure

```
├── main.py                 # FastAPI application
├── models.py              # Database models
├── schemas.py             # Pydantic schemas
├── database.py            # Database configuration
├── routes.py              # API routes
├── auth.py                # Authentication system
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── services/
│   ├── email_service.py   # Email notifications
│   ├── telegram_service.py # Telegram notifications
│   └── chatbot_service.py # AI chatbot
├── templates/email/       # Email templates
├── static/
│   ├── images/           # Product images
│   └── videos/           # Product videos
└── README.md
```

## Environment Variables

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
RECIPIENT_EMAIL=your_email@gmail.com

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Database
DATABASE_URL=postgresql://postgres:password@localhost/sir

# OpenRouter API (for chatbot)
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

## Production Deployment

### Deploying to Render (Free Tier)

1. Fork this repository to your GitHub account
2. Sign up for a free account at [Render](https://render.com)
3. Click "New+" and select "Web Service"
4. Connect your GitHub repository
5. Set the following:
   - Name: `smarttech-backend`
   - Region: Choose the closest to your users
   - Branch: `main` (or your default branch)
   - Root Directory: `backend`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `bash start.sh`
6. Add environment variables in the "Advanced" section:
   - `SECRET_KEY`: A random secret key for security
   - `JWT_SECRET_KEY`: A random JWT secret key
   - `OPENROUTER_API_KEY_1`: Your OpenRouter API key
   - `OPENROUTER_API_KEY_2`: Your secondary OpenRouter API key (optional)
   - `OPENROUTER_API_KEY_3`: Your fallback OpenRouter API key (optional)
   - `SMTP_EMAIL`: Your Gmail address for sending emails
   - `SMTP_PASSWORD`: Your Gmail app password
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID
7. Click "Create Web Service"
8. Render will automatically provision a free PostgreSQL database
9. After deployment, update your frontend to use the new backend URL

### Manual Deployment Steps

1. Update CORS settings in `main.py`
2. Set `DEBUG=False` in `.env`
3. Use a production WSGI server like Gunicorn
4. Set up SSL/TLS certificates
5. Configure environment variables securely
6. Set up database backups

## Support

For technical support or questions:
- **Phone**: 01678-134547
- **Email**: Contact through the website
- **AI Chatbot**: Available 24/7 on the website

---

**SmartTech** - Adapting the Future with Interactive Smart Board Solutions