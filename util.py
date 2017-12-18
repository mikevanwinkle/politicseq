#!/usr/bin/python
import argparse
import socket, os
import pprint
import messager as m
import requests
from politicseqapi import PoliticsEQApi as pol
from pprint import pprint

# parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument("command", help="Command {info|run|build|stop|port}")
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
    
  def check(self):
    sources = pol.sources()
    entities = {}
    for source in sources: 
      m.info("checking source: {0}".format(source['name']))
      items = pol.fetch_articles_from_src(source)
      for item in items:
        m.success(" - {}: {}".format(item['title'].encode('UTF-8'), item['link']))
        pol.ingest_from_feed_item(item, source=source)
        #entities = pol.fetch_article_entities(item['link'])
        #for name,entity in entities.items():
          #pprint(entity)
  
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
