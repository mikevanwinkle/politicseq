#!/usr/bin/python
import argparse
import socket, os
import pprint
import messager as m
import requests
from politicseqapi import PoliticsEQApi as pol
from pprint import pprint
from celery import Celery

env=os.environ
CELERY_BROKER_URL=env.get('CELERY_BROKER_URL','redis://:mikeisawesome@0.0.0.0:6379'),
CELERY_RESULT_BACKEND=env.get('CELERY_RESULT_BACKEND','redis://:mikeisawesome@0.0.0.0:6379')

celery= Celery('celery.tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

# parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("command", help="Command {info|run|build|stop|port}")
parser.add_argument('--feed', type=str, help="Restrict operation by feed")
#parser.add_argument("site", nargs='?', help="The site to operate on")
parser.add_argument('--force', help="Force the operatoin")
args = parser.parse_args()
pol = pol()

class Util():
  def __init__(self):
    pass

  def _load_db(self):
    import db
    return db.Db()

  def main(self):
    result = getattr(self, args.command)()

  def sources(self):
    from models.source import source as source
    sources = source()
    for source in sources.get():
      print source

  def tasks(self):
    from models.article import article
    article = article()
    articles = article.getAll(with_enitities=True)
    for item in articles:
      if len(item['entities']) < 1:
        task = celery.send_task('peq.entities', args=[item['id']], kwargs={})

  def entities(self):
    from models.article import article
    from models.entity import entity
    m.info('Articles without entities')
    article = article()
    articles = article.getAll(with_enitities=True, avg=True)
    for article in articles:
      m.info("{}".format(article['title']))
      if len(article['entities']) > 0:
        ens = [entity for entity in article['entities'] if entity['type'] in ['ORGANIZATION', 'PERSON']]
        for en in ens:
          print "-> {} = {}".format(en['name'], en['sentiment'])

  def check(self, source_name=None):
    sources = pol.sources()
    if args.feed:
      sources = [source for source in sources if source['name'] == args.feed]
    entities = {}
    for source in sources:
      m.info("-" * 50)
      m.info("checking source: {0}".format(source['name']))
      m.info("-" * 50)
      items = pol.fetch_articles_from_src(source)
      for item in items:
        line = "  Title: {}:\n  Url:{}\n".format(item['title'].encode('UTF-8'), item['link'])
        pol.ingest_from_feed_item(item, source=source, update=False)

  def createdb(self):
    import db

  def create_sources(self):
    import db
    from models.source import source as source
    source = source()
    db = db.Db()
    r = requests.get('https://politicseq.com/api/feeds?feeds', verify=requests.certs.where())
    sources = r.json()
    for feed in sources:
      source.insert(feed)
    results = db.query("SELECT * FROM source")
    pprint(results)

  def list_sources(self):
    from models.source import source as source
    source = source()
    pprint(source.get())

  def add_column(self):
    import db
    db = db.Db()
    db.add_column('article', '`link` VARCHAR(255) NOT NULL')
    db.save()

  def create_table(self):
    db = self._load_db()
    db.query("CREATE TABLE stat (\
              `id` BIGINT unsigned NOT NULL AUTO_INCREMENT,\
              `stat_key` VARCHAR(50) NOT NULL,\
              `stat_value` FLOAT(10,2) NOT NULL,\
              `stat_type` VARCHAR(20) NULL,\
              `stat_date` datetime DEFAULT CURRENT_TIMESTAMP,\
              `article_id` BIGINT unsigned NOT NULL,\
              PRIMARY KEY (`id`)\
              ) ENGINE=innodb DEFAULT CHARSET=utf8;")
    db.save()


if __name__ == '__main__':
  util = Util()
  util.main()
