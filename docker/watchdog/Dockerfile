FROM python:3.11-slim

WORKDIR /app
COPY watchdog/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY watchdog/main.py .

CMD ["python", "main.py"]