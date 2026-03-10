# Use official Python runtime
FROM python:3.11-slim

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevent buffering
ENV PYTHONUNBUFFERED=1

# Django settings module
ENV DJANGO_SETTINGS_MODULE=cofig.settings

# Default port (Back4App injects $PORT at runtime)
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies including SQLCipher for encrypted SQLite
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libsqlcipher-dev \
    sqlcipher \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Directory for static files (collected at runtime)
RUN mkdir -p /app/staticfiles

# Copy and set up the runtime entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose default port
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

