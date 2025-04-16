FROM python:3.12-slim-bookworm

RUN pip install --no-cache-dir --upgrade pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY run.py requirements.txt /app/

RUN chmod +x /app/run.py && \
    pip install -r requirements.txt 

COPY . /app

EXPOSE 8000

CMD ["bash", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8008 & python manage.py consume_messages"]
