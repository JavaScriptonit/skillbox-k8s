FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN http_proxy= https_proxy= pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "app.py"]