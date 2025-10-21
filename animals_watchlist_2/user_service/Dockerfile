FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy service code and frontend
COPY . .

EXPOSE 5005

CMD ["python", "login.py"]
