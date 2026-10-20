FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ templates/

EXPOSE 5678

CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && gunicorn --bind 0.0.0.0:5678 app:app"]

