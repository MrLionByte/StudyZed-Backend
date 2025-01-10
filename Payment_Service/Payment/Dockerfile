FROM python:3.11-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt 

COPY . /app/

EXPOSE 8000



# RUN apt-get update && \
#     apt-get install -y --no-install-recommends supervisor && \
#     pip install --no-cache-dir --upgrade pip && \
#     pip install -r requirements.txt && \
#     apt-get clean && rm -rf /var/lib/apt/lists/*

# RUN mkdir -p /etc/supervisor/conf.d

# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


# EXPOSE 8000

# CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]