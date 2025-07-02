FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app/logs

WORKDIR /app
COPY run.py requirements.txt requirements-dev.txt /app/
RUN chmod +x /app/run.py && \
    pip install -r requirements.txt -r requirements-dev.txt

COPY . /app

COPY start.sh /start.sh
RUN chmod +x /start.sh

RUN mkdir -p /app/logs

EXPOSE 8005

# CMD ["bash", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8005"]
CMD ["/start.sh"]