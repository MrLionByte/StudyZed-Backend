FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DJANGO_SETTINGS_MODULE=Notification.settings 

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.wsgi:application"]

EXPOSE 8000