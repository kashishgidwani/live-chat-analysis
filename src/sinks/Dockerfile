FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# You can specify which consumer to run via the docker-compose command
# This is a placeholder
CMD ["echo", "sinks container built successfully"] 