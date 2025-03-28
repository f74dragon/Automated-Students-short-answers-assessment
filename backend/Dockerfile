# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the app directory (more specific than copying everything)
COPY ./app ./app

# Add the app directory to Python path
ENV PYTHONPATH=/app

# Expose port 8001 for the FastAPI app
EXPOSE 8001

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
