FROM python:3.8-slim-buster

ENV http_proxy=
ENV HTTP_PROXY=
ENV ftp_proxy=
ENV FTP_PROXY=
ENV https_proxy=
ENV HTTPS_PROXY=
ENV socks_proxy=
ENV SOCKS_PROXY=
ENV no_proxy="localhost,127.0.0.1,.mbrd.ru,.mtsbank.ru"
ENV NO_PROXY="localhost,127.0.0.1,.mbrd.ru,.mtsbank.ru"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "app.py"]
