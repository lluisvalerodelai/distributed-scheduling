# Dockerfile
FROM python:3.11-slim

# Install common dependencies
RUN apt-get update && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python packages for tasks
RUN pip install --no-cache-dir \
    python-dotenv

# Set working directory
WORKDIR /node

# Copy tasks directory (required by node.py)
COPY /tasks /node/tasks
COPY /.dockerNode.env /node/.env

# Copy node script
COPY Node/node.py /node/node.py

CMD ["python", "node.py"]
