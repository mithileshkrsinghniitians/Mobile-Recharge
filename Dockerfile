# Use official Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy backend code
COPY backend/ ./backend

# Copy static folder (IMPORTANT ⭐⭐⭐⭐⭐)
COPY static/ ./static

# Expose port
EXPOSE 8080

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--chdir", "backend", "app:app"]
