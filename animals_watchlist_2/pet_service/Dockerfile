# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY add.py .

# Expose the port your Flask app runs on
EXPOSE 5006

# Command to run the service
CMD ["python", "add.py"]
