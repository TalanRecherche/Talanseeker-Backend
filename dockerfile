FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install -r requirements.txt

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["uvicorn", "app.start_app:app", "--host", "0.0.0.0", "--port", "80"]
