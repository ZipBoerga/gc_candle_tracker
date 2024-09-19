FROM python:3.10-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/bot.py .
COPY app/secrets.py .

CMD ["python", "bot.py"]