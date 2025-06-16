FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create empty .env file if it doesn't exist
RUN touch .env

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8181"]
