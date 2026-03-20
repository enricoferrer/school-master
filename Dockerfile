FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Copy entrypoint script
COPY entrypoint.py /entrypoint.py
RUN chmod +x /entrypoint.py
EXPOSE 8000
ENTRYPOINT ["python", "/entrypoint.py"]