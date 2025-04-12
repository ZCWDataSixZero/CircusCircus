FROM python:3.9-slim

EXPOSE 5010

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY forum /app
COPY config.py /app
CMD cd ./forum; export FLASK_DEBUG=1; flask run --host=0.0.0.0
