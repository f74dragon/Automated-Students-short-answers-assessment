# Start with Python 3.9 base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg2 \
    lsb-release \
    nginx \
    supervisor \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh && \
    which ollama && ollama --version

# Ensure PATH is set correctly
ENV PATH="/usr/local/bin:$PATH"

# Create app directories
WORKDIR /app
RUN mkdir -p /app/frontend /app/backend /app/logs

# Copy backend files
COPY backend/requirements.txt /app/backend/
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app /app/backend/app

# Copy frontend files
COPY frontend/package*.json /app/frontend/
WORKDIR /app/frontend
RUN npm install

COPY frontend/public /app/frontend/public
COPY frontend/src /app/frontend/src

# Build the frontend
RUN npm run build

# Set up Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN rm /etc/nginx/sites-enabled/default || true

# Set up Supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set up scripts
COPY wait-for-postgres.sh /app/
COPY init_postgres.sh /app/
RUN chmod +x /app/wait-for-postgres.sh /app/init_postgres.sh

# Switch back to main directory
WORKDIR /app

# Create required directories for runtime
RUN mkdir -p /run/nginx /var/log/nginx /var/lib/nginx

# Expose ports
EXPOSE 80 8001

# Start Supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
