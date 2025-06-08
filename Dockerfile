FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=builder /install /usr/local

COPY app.py .
COPY static ./static/

EXPOSE 8000

CMD ["uvicorn", "app:app_asgi", "--host", "0.0.0.0", "--port", "8000"]