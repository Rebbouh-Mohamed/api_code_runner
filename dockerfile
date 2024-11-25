FROM python:3.9-slim

# Install required system dependencies for compilers
RUN apt-get update && apt-get install -y \
    gcc g++ openjdk-11-jdk php-cli nodejs dotnet-sdk-6.0 && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy the current app directory to the container
COPY ./api.py /app
# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Expose the port FastAPI will run on
EXPOSE 5000

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
