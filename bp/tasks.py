import os, sys, json
sys.path.append(os.getcwd())
import time
from celery import Celery
from models.article import article
from politicseqapi import PoliticsEQApi
from pprint import pprint

env=os.environ
CELERY_BROKER_URL=env.get('CELERY_BROKER_URL','redis://:mikeisawesome@0.0.0.0:6379'),
CELERY_RESULT_BACKEND=env.get('CELERY_RESULT_BACKEND','redis://:mikeisawesome@0.0.0.0:6379')

celery= Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

peq = PoliticsEQApi()

@celery.task(name='mytasks.add')
def add(x, y):
    time.sleep(1) # lets sleep for a while before doing the gigantic addition task!
    return x + y

@celery.task(name='peq.entities', autoretry_for=(Exception,))
def article_entities(article_id):
    from models.entity import entity
    a = article()
    entity = entity()
    entities = peq.fetch_article_entities(a.find_by_id(article_id).get('content'))
    for name, en in entities.items():
        en['article_id'] = article_id
        print "{}".format(str(en))
        entity.new(en)
        entity.save()
    entity.commit()
