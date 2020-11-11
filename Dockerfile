FROM python:3.8.0-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY falcon /app/falcon
COPY apis   /app/apis

CMD ["gunicorn", "--pythonpath", "falcon", "-b", "0.0.0.0:5000", "app:app", "--reload"]

