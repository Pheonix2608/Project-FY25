# Use an official lightweight Python base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy project files into container
COPY . /app

# Install system dependencies (PyQt needs them)
RUN apt-get update && apt-get install -y \
    libgl1 libx11-xcb1 libfontconfig1 libxrender1 libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for FastAPI
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
