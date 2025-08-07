# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip && \
    pip install torch PyQt6 numpy scikit-learn pandas matplotlib seaborn

# Expose port (if needed for API)
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the main application
CMD ["python", "main.py"]
