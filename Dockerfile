FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install dependencies using the app's requirements inside the AIDLINK folder
COPY AIDLINK/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source (only the AIDLINK app folder) into the image
COPY AIDLINK/ .

# Railway injects $PORT at runtime; default to 8000 for local docker runs
ENV PORT=8000

CMD ["sh", "-c", "gunicorn dynamic_app:app --bind 0.0.0.0:${PORT}"]

