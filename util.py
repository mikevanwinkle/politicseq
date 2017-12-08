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

  def main(self):
    result = getattr(self, args.command)()

  def sources(self):
    sources = pol.sources()
    pprint(sources)
    
  def check(self):
    sources = pol.sources()
    entities = {}
    for sname, sdata in sources.items(): 
      m.info("checking source: {0}".format(sdata['name']))
      items = pol.fetch_articles_from_src(sdata)
      for item in items:
        m.success(" - {}: {}".format(item['title'].encode('UTF-8'), item['link']))
        entities = pol.fetch_article_entities(item['link'])
        for name,entity in entities.items():
          pprint(entity)
  
  def createdb(self):
    import db

  def create_sources(self): 
    import db
    from models.source import source as source
    db = db.Db()
    for (id, name, url, type) in db.query("SELECT * from source;"):
      pprint(name)

    
    
  
if __name__ == '__main__':
  util = Util()
  util.main()
