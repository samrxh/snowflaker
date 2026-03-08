# Use Python
FROM python:3.9-slim

# Set the folder inside the container
WORKDIR /app

# Copy the list of libraries and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your main.py into the container
COPY . .

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]