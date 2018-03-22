FROM ubuntu:16.04

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

ENV CELERY_BROKER_URL redis://:mikeisawesome@redis:6379/0
ENV CELERY_RESULT_BACKEND redis://:mikeisawesome@redis:6379/0
ENV C_FORCE_ROOT true

# copy source code
COPY . .

# install requirements
RUN pip install celery redis==2.10.5 flower docker jinja2==2.8 pyyaml

# run the worker
#ENTRYPOINT ['celery']
#CMD ['-A','tasks', 'worker','--loglevel=info']
ENTRYPOINT celery flower -A tasks --loglevel=info --broker='redis://:mikeisawesome@redis:6379/0'
