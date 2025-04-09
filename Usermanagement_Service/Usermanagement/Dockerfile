FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY run.py requirements.txt requirements-dev.txt /app/
RUN chmod +x /app/run.py && \
    pip install -r requirements.txt -r requirements-dev.txt
COPY . /app
EXPOSE 8000
CMD ["python", "/app/run.py"]