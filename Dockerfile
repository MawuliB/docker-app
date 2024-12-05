# # Single stage Dockerfile for a Flask application
# FROM python:3.13-alpine

# # Set the working directory in the container
# WORKDIR /app

# # Copy only the necessary files to the container
# COPY requirements.txt .

# # Install dependencies (use --no-cache-dir to reduce image size)
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the application code to the container
# COPY . .

# # Expose port 5000 for the application
# EXPOSE 5000

# # Command to run the application
# CMD ["python", "main.py"]

# #end of Dockerfile

# Stage 1: Build environment
FROM python:3.13-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production-ready image
FROM python:3.13-alpine

# Set the working directory
WORKDIR /app

# Copy only the installed dependencies from the builder stage
COPY --from=builder /install /usr/local

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 5000

# Command to run the application
CMD ["python", "main.py"]
