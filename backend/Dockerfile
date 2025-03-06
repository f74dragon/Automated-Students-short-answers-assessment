# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the backend directory contents into the container
# COPY backend/ /app/
COPY . /app/

# Copy the llm directory into the container
# COPY llm/ /app/llm/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Add the app directory to Python path
ENV PYTHONPATH=/app

# Expose port 8001 for the FastAPI app
EXPOSE 8001

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
