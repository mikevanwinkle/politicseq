FROM ubuntu:14.04

RUN apt-get update -y --fix-missing
RUN apt-get install -y python-pip python-dev build-essential libssl-dev libffi-dev

ENV CELERY_BROKER_URL redis://:mikeisawesome@redis:6379/0
ENV CELERY_RESULT_BACKEND redis://:mikeisawesome@redis:6379/0
ENV C_FORCE_ROOT true

WORKDIR /opt/bp
RUN ls -l .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# run the worker
#ENTRYPOINT ['celery']
#CMD ['-A','tasks', 'worker','--loglevel=info']
ENTRYPOINT celery flower -A tasks --loglevel=info --broker='redis://:mikeisawesome@redis:6379/0'
