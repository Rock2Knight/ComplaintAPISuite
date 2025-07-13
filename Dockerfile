FROM python:3.12.9-alpine3.21

WORKDIR /app

COPY requirements.txt .
RUN pip3 cache purge && \
    pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=.

CMD ["python3", "-u", "./app/main.py"]