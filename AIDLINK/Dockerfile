FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Note: index.html should be copied from root when building
# Build from project root: docker build -f AIDLINK/Dockerfile --build-arg INDEX_HTML=../index.html -t aidlink .
# Or ensure index.html is in AIDLINK/ before building

ENV PORT=8000

CMD ["gunicorn", "dynamic_app:app", "--bind", "0.0.0.0:${PORT}"]

