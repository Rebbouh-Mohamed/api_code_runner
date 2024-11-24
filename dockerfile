FROM ubuntu:latest

# Install various compilers and interpreters
RUN apt-get update && apt-get install -y \
    python3 \
    default-jdk \
    php \
    gcc \
    g++ \
    nodejs \
    curl \
    python3-flask  # Install Flask using apt \
    mysql \

# Copy the code execution server script
COPY code_exec_server.py /code_exec_server.py

# Expose port for communication
EXPOSE 5000

# Start the Flask server
CMD ["python3", "/code_exec_server.py"]
