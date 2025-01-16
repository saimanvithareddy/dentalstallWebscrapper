# dentalstallWebscrapper
A webscrapper for dental stall target website to scrape the information using fastapi store and and send notifications.

# Web Scraper API

A FastAPI-based web scraping service that extracts product information from e-commerce websites with caching, storage, and notification capabilities.

## Features

- Product data scraping (name, price, images)
- Redis-based caching
- Multiple storage strategies (JSON file storage implemented)
- Notification system (Console and Email notifications)
- Token-based authentication
- Configurable proxy support
- Page limit controls
- Retry mechanism for failed requests

## Prerequisites

- Python 3.8+
- Redis server
- SMTP server access (for email notifications)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with the following variables:
```env
# API Settings
API_TOKEN=your_api_token_here
BASE_URL=https://your-target-website.com
STORAGE_PATH=./data/products.json

# Redis Settings
REDIS_URL=redis://localhost:6379

# Email Settings (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@example.com
SENDER_PASSWORD=your-app-specific-password
NOTIFICATION_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

## Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── cache/
│   │   └── cache.py
│   ├── notification/
│   │   └── notifications.py
│   ├── scraper/
│   │   └── scraper.py
│   └── storage/
│       └── storage.py
├── requirements.txt
├── .env
└── README.md
```

## Usage

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. The API will be available at `http://localhost:8000`

3. Access the API documentation at `http://localhost:8000/docs`

### API Endpoints

- `GET /`: Health check endpoint
- `GET /test`: Test endpoint to verify setup
- `POST /scrape`: Main scraping endpoint

Example request to scrape products:
```bash
curl -X POST "http://localhost:8000/scrape" \
     -H "api-token: your_api_token_here" \
     -H "Content-Type: application/json" \
     -d '{"page_limit": 5, "proxy": "http://proxy-server:port"}'
```

## Dependencies

```text
fastapi==0.95.0
uvicorn==0.21.1
pydantic==1.10.7
python-multipart==0.0.6
python-dotenv==0.21.1
beautifulsoup4==4.11.2
requests==2.31.0
redis==4.5.1
httpx==0.24.1
```
