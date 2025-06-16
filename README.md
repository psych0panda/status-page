# Status Page

A real-time status monitoring page for you services. This service provides a web interface to monitor the health of various components of the system.

## Features

- Real-time status monitoring of all services
- Visual status indicators with animations
- Status history tracking
- Auto-refresh every 30 seconds
- REST API endpoint for programmatic status checks

## Components Monitored (example)

- API Server
- Telegram Bot
- Database
- Whisper ASR Service
...

## Setup

1. Create a `.env` file with the following variables:
```env
APP_URL=http://youhost:8000/health
BOT_URL=http://youhost:8888/health
DB_URL=postgresql://postgres:postgres@db:5432/database
WHISPER_URL=http://youhost:9000/health
GRAFANA_URL=http://youhost:3000/health
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the service:
```bash
uvicorn main:app --host 0.0.0.0 --port 9080
```

## API Endpoints

- `GET /`: Web interface for status monitoring
- `GET /api/status`: JSON API endpoint for service status

## Docker

The service is configured to run in Docker. Use the provided Dockerfile to build the image:

```bash
docker build -t service-status .
```

## Development

The service is built with:
- FastAPI for the backend
- Jinja2 for templating
- TailwindCSS for styling
- aiohttp for async HTTP requests
- asyncpg for database connectivity 