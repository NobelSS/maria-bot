FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port for the health-check web server
EXPOSE 8000

# Start the bot (unbuffered so logs appear immediately in docker logs)
CMD ["python", "-u", "main.py"]
