FROM python:3.7-slim-buster

MAINTAINER Diogo Fernandes "diogofernandescon@gmail.com"

RUN apt-get update -y && \
    apt-get -y install gcc && \
    pip install --upgrade pip

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 5000
EXPOSE 80

ENTRYPOINT [ "python3.7" ]

CMD [ "flask_run.py" ]