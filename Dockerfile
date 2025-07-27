  GNU nano 6.2                         Dockerfile                                  
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install boto3 --no-cache-dir
RUN pip install Pillow --no-cache-dir

COPY stage_one.py .

CMD ["python", "stage_one.py"]
=======
FROM python:3.13-slim-bookworm

# Set working directory
WORKDIR /app

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY remove_color.py .

# Create directories and set permissions
RUN mkdir -p /app/inputs /app/outputs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set default environment variables
ENV INPUT_DIR=/app/inputs
ENV OUTPUT_DIR=/app/outputs
