FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/base.txt /app/requirements/base.txt
RUN pip install --upgrade pip && \
    pip install -r requirements/base.txt

# Copy project
COPY . /app/

# Make entrypoint executable
RUN chmod +x /app/docker-entrypoint.sh

# Run entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
