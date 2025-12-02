FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system deps and supervisor (and RabbitMQ Erlang runtime)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev libpq-dev supervisor curl gnupg apt-transport-https ca-certificates \
    && apt-get install -y --no-install-recommends rabbitmq-server \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application
COPY . /app

# Place supervisor config
COPY supervisord.conf /etc/supervisord.conf

# Expose application and RabbitMQ ports
EXPOSE 8080 8001 8002 8003 5672 15672

# Default RabbitMQ retry/wait settings for consumers (configurable via env)
ENV RABBIT_INITIAL_WAIT=2 \
    RABBIT_RETRY_DELAY=5 \
    RABBITMQ_DEFAULT_USER=guest \
    RABBITMQ_DEFAULT_PASS=guest

# Enable RabbitMQ management plugin if available (best-effort)
RUN rabbitmq-plugins enable --offline rabbitmq_management || true

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf", "-n"]
