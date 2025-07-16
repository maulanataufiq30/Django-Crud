# app/Dockerfile
FROM python:3.9
ENV PYTHONUNBUFFERED 1

WORKDIR /app
# Copy script wait-for-it
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh
RUN mkdir -p /app/staticfiles
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .