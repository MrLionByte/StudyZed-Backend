FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV DJANGO_SETTINGS_MODULE=Notification.settings 

WORKDIR /app

COPY run.py requirements.txt /app/

RUN chmod +x /app/run.py && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir -p /celery-worker && \
    chmod -R 777 /celery-worker

COPY . /app

EXPOSE 8007

CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8007 & python manage.py consume_messages"]
