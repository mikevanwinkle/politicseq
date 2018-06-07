FROM ubuntu:16.04

RUN apt-get update -y --fix-missing
RUN apt-get install -y python-pip python-dev build-essential libssl-dev libffi-dev openssl
RUN python --version
ENV CELERY_BROKER_URL redis://:mikeisawesome@redis:6379/0
ENV CELERY_RESULT_BACKEND redis://:mikeisawesome@redis:6379/0
ENV C_FORCE_ROOT true
ENV DB_HOST mysql

ADD . /opt/bp
WORKDIR /opt/bp
RUN pip install --upgrade pip
RUN pip install cryptography Cython
RUN pip install -r requirements.txt

# run the worker
#ENTRYPOINT ['celery']
#CMD ['-A','tasks', 'worker','--loglevel=info']
