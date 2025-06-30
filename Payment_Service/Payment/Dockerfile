FROM python:3.12-slim-bookworm

RUN pip install --no-cache-dir --upgrade pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY run.py requirements.txt /app/

RUN chmod +x /app/run.py && \
    pip install -r requirements.txt

COPY . /app

COPY start.sh /start.sh
RUN chmod +x /start.sh

RUN mkdir -p /app/logs

EXPOSE 8008

CMD ["/start.sh"]