FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to access shared 'core' module
COPY . .

# Command to run the main processing consumer
CMD ["python", "-m", "src.processing.core_consumer"]