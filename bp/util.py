#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import socket, os
import pprint
import messager as m
import requests
from politicseqapi import PoliticsEQApi as pol
from pprint import pprint
from celery import Celery
import hashlib
import pandas as pd

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
		articles = article.getSet(where="date >= '2018-06-21'", entities=True, avg=False)
		dfs = []
		df = None
		for article in articles:
			if len(article['entities']) < 1: continue
			qualified = [entity for entity in article['entities']
												if entity['type'] not in ['OTHER']]
												#((entity['sentiment'] >= 0.7 and entity['magnitude'] >= 0.3) or (entity['sentiment'] <= -0.6))]
			m.info("{}".format(article['title']))
			if len(qualified) < 1: continue
			df = pd.DataFrame(qualified, columns=article['entities'][0].keys())

			if df is not None:
				dfs.append(df)
			df = None

		data = pd.concat(dfs).reset_index()
		#rel = pd.concat(dfs)
		#print rel.dtypes
		#exit()
		print data[['name','sentiment']]
		cols = data.columns.drop(['name','type'])
		data[cols] = data[cols].apply(pd.to_numeric, downcast='float', errors='coerce')
		new = data.groupby('name')['sentiment'].agg(['count','mean']).sort_values(['mean','count'])
		print new

	def check(self, source_name=None):
		sources = pol.sources()
		if args.feed:
			m.info("===> Filtering for {}".format(args.feed))
			sources = [source for source in sources if source['name'] == args.feed]
		entities = {}
		for source in sources:
			m.info("===> checking source: {0}".format(source['name']))
			items = pol.fetch_articles_from_src(source)
			for item in items:
				line = "  Title: {}:\n  Url:{}\n".format(item['title'].encode('UTF-8'), item['link'])
				article = pol.ingest_from_feed_item(item, source=source, update=True)
				if article:
					celery.send_task('peq.entities', args=[article.get('id')], kwargs={})

	def cluster(self):
		# import modules & set up logging
		import gensim, logging
		logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

		sentences = [['first', 'sentence'], ['second', 'sentence']]
		# train word2vec on the two sentences
		model = gensim.models.Word2Vec(sentences, min_count=1)
		model = gensim.models.Word2Vec(iter=1)  # an empty model, no training yet

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
		db.add_column('entity', '`sentiment` DECIMAL(10,8) NULL')
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

	def google(self):
		article_id = 1604
		from models.entity import entity
		from models.article import article
		a = article()
		entity = entity()
		entities = pol.fetch_article_entities(a.find_by_id(article_id).get('content'))
		for en, ens in entities.items():
			ens['article_id'] = article_id
			print "{}".format(str(ens))
		exit()

	def tone(self):
		article_id = 1604
		from models.article import article
		a = article()
		entities = pol.fetch_article_tone(a.find_by_id(article_id).get('content'))

if __name__ == '__main__':
	util = Util()
	util.main()
