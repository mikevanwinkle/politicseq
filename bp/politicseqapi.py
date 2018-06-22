import requests, json, feedparser, pprint, os, re
from bs4 import BeautifulSoup
from stanfordcorenlp import StanfordCoreNLP
import messager as m
import xml

BASE_URL = 'https://api.politicseq.com'
#NLP_URL = 'http://104.131.130.164'
NLP_URL = str(os.getenv('NLP_URL'))
NLP_PORT = 9000

sentiment_map = {
	'Verynegative': -1.0,
	'Negative': -0.5,
	'Positive': 0.5,
	'Verypositive': 1.0,
	'Neutral': 0
}

FEED_CLASSES = {
	"Breitbart": "entry-content",
	"FiveThirtyEight": "entry-content",
	"foxnews": "article-body",
	"FoxNews - Opinion": "article-body",
	"HotAir Main": "article-text",
	"Huffington Post - Politics": "entry__text",
	"New York Times - Paul Krugman": "story-body",
	"NYPost - Opinion": "entry-content",
	"politico": "story-text",
	"Politico - Politics": "story-text",
	#"Salon.com": {"regex": "style__postBody_.*"},
	"Salon.com": "scroll-posts",
	"Vox.com": "c-entry-content",
	"Washington Post - Opinion": "paywall"
}

FEED_ELEMENTS = {
	"Breitbart": "div",
	"FiveThirtyEight": "div",
	"foxnews": "div",
	"FoxNews - Opinion": "div",
	"HotAir Main": "div",
	"Huffington Post - Politics": "div",
	"New York Times - Paul Krugman": "a",
	"NYPost - Opinion": "div",
	"politico": "div",
	"Politico - Politics": "div",
	"Salon.com": "div",
	"Vox.com": "div",
	"Washington Post - Opinion": "article"
}

AUTHOR_CLASSES = {
	"foxnews": "author-byline",
	"Huffington Post - Politics": "author-card__link",
	"New York Times - Paul Krugman": "byline-column-link",
	"NYPost - Opinion": "author-byline",
	"politico": "byline",
	"Salon.com": "style__authorName___1Hdxd",
	"Washington Post - Opinion": "pb-byline"
}

# the element that wraps the target class in AUTHOR_CLASSES
AUTHOR_ELEMENTS = {
	"foxnews": "div",
	"Huffington Post - Politics": "a",
	"NYPost - Opinion": "div",
	"politico": "p",
	"Salon.com": "span",
	"Washington Post - Opinion": "span"
}

class PoliticsEQApi():
	def __init__(self):
		pass

	def sources(self, match=None):
		from models.source import source as source
		sources = source()
		return sources.get()

	def clean_text(self, text):
		import codecs, string
		from bs4 import UnicodeDammit
		uni = UnicodeDammit(text, ["utf-8"])
		text = uni.unicode_markup
		chars = {
			'\u201c': '"',
			'\u201d': '"',
			'\\xa0': ' ',
			'\\u2019': "'",
			'\\u2013': "-",
			'\\n': '',
			'\\t': '',
			'\\xe2\\x80\\x98': '',
			'\\xe2\\x80\\x99': '\'',
			'\\xc2': '',
			'\\xe2': ' ',
			'\\x80': '',
			'\\x9d': '',
			' \\x99': '\'',
			' \\x98': '\''
		}

		for char, repl in chars.items():
			text = text.replace(char, repl).strip()
		printable = set(string.printable)
		text = filter(lambda x: x in printable, text)
		return text

	def parse_author_from_html(self, feed_item, source):
		r = requests.get(feed_item['link'], verify=requests.certs.where(), headers={'User-agent': 'PoliticsEQ Sentiment Bot'})
		soup = BeautifulSoup(r.text, 'html.parser')
		divs = soup.findAll(AUTHOR_ELEMENTS[source['name']], {'class': AUTHOR_CLASSES[source['name']]})
		#divs = BeautifulSoup(str(divs), 'html.parser')
		authors = []
		for div in set(divs):
			authors.append({"name": self.clean_text(div.get_text())})
		return authors

	def ingest_from_feed_item(self, feed_item, source=None, update=False):
		from models.author import author
		from models.article import article
		from dateutil import parser
		import codecs
		author = author()
		articles = article()
		# if this article already exists skip it
		if update == False:
			article = articles.find_by_link(feed_item['link'])
			if article.getDict(): return article
		print "Title: {}".format(self.clean_text(feed_item['title']))
		item_auths = []
		if not 'authors' in feed_item.keys():
			feed_item['authors'] = self.parse_author_from_html(feed_item, source)
		for auth in feed_item['authors']:
			# hack to handle salon.com
			if len(auth['name'].split(',')) > 1 and '<' in auth['name'].split(',')[1]:
				# if the second substr contains < take the first ... removes links appended to byline
				# example: <a href="http://www.alternet.org/" class="gaTrackLinkEvent" data-ga-track-json=\'["source"', u' "click"', u' "Alternet"] target="_blank"\'>Alternet</a>
				auth['name'] = auth['name'].split(',')[0]
			if not author.exists(auth['name']):
				author.create({'name': auth['name']})
			item_auths.append(author.find(auth['name']))
		if len(item_auths) < 1:
			pprint.pprint(item_auths)
			author.create({'name': 'Editorial'})
			item_auths.append(author.find('Editorial'))
			m.error(" ==> Assigning to Editorial")
			return None

		item_info = {}
		# pprint.pprint(item_auths)
		# fetch the article
		r = requests.get(feed_item['link'], verify=requests.certs.where(), headers={'User-agent': 'PoliticsEQ Sentiment Bot'})
		summary = ''
		if 'summary' in feed_item.keys():
			summary = BeautifulSoup(self.clean_text(feed_item['summary']), 'html.parser')
			summary = summary.get_text()
		soup = BeautifulSoup(r.text, 'html.parser')
		match_class = FEED_CLASSES[source['name']]
		if isinstance(match_class, dict):
			match_class = re.compile(match_class['regex'])
		text = soup.findAll(FEED_ELEMENTS[source['name']], {'class': match_class})
		text = BeautifulSoup(str(text), 'html.parser')
		body = []
		for p in text.findAll('p'):
			body.append(self.clean_text(p.get_text()))
		body = "".join(body)
		print "Body: {}".format(body[:100])
		feed_item['title'] = self.clean_text(feed_item['title'])
		article = articles.find_by_title(feed_item['title'])
		if not article.getDict():
			# saving article
			a = {}
			m.info("Saving {}".format(feed_item['title']))
			# some feeds don't publish the date so we need to try and get it from the article
			# this is primarily a hack for the Washington Post
			if 'published' not in feed_item:
				bsdate = BeautifulSoup(r.text,'html.parser')
				date = bsdate.find('span', itemprop="datePublished")
				if date:
					feed_item['published'] = parser.parse(date['content'].replace('-500','')).strftime('%Y-%m-%d %H:%M')
				else:
					import datetime
					feed_item['published'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
			else:
				feed_item['published'] = parser.parse(feed_item['published']).strftime('%Y-%m-%d %H:%M')
			article = articles.new({
					'title': feed_item['title'],
					'summary': summary,
					'source': source['id'],
					'author_id': item_auths[0]['id'],
					'content': body,
					'date': feed_item['published'],
					'link': feed_item['link']
			})
			article = article.save()
			m.success("Created {}".format(article.last_id()))
			return article
		else:
			if not update: m.info("Skipping {}".format(article))
			article.update('content', body)
			article.save()
			m.success("> Updated {}".format(article.last_id()))

	def fetch_articles_from_src(self, source):
		feed = feedparser.parse(source['url'])
		return feed.entries

	def fetch_article_entities(self, text, google=True):
		if not google:
			nlp = StanfordCoreNLP(NLP_URL, port=NLP_PORT)
			n = nlp._request('sentiment,ner', text)
			entities = self.extract_entities(n)
		else:
			entities = self.google_entities(text)
			#entities = [(token['word'], token['ner']) for token in s['tokens'] if len(token['ner']) > 1]
		return entities

	def fetch_article_tone(self, text):
		from os.path import join, dirname
		creds = {
				"username": '84673387-7e43-4806-9e9b-ed1a36979206',
				"password": 'MbfCrnY6AiPJ',
				"version": '2017-09-26'
		}
		r  = requests.post("https://gateway.watsonplatform.net/tone-analyzer/api/v3/tone?version={}&input=".format(creds["version"]),
											auth=(creds["username"], creds["password"]),
											headers={"Content-type":"text/plain"},
											data=self.clean_text(text))
		print r.text

	def extract_entities(self, text):
		entities = {}
		for s in text['sentences']:
			skip_next = False
			tokens = s['tokens']
			sent = []
			for pos in range(0, len(tokens) - 1):
				sent.append(tokens[pos]['word'])
				# skip when token is not an entity
				if len(tokens[pos]['ner']) < 2 or tokens[pos]['ner'] == 'DATE':
					continue

				# skip when this token was combined with a previous token
				if skip_next:
					# reset skip value
					skip_next = False
					continue

				combined_token = ""
				next_token = tokens[pos + 1]
				if next_token['ner'] == tokens[pos]['ner']:
					combined_token = '{0} {1}'.format(tokens[pos]['lemma'], next_token['lemma'])
					# skip the next token since it was combined
					skip_next = True
				else:
					combined_token = tokens[pos]['lemma']
				if not combined_token in entities.keys():
					entities[combined_token] = {}

				entities[combined_token] = {
					'name': combined_token,
					'type': tokens[pos]['ner'],
					'sentiment': sentiment_map[s['sentiment']]
				}
		# return the complete entity hash
		return entities

	def google_entities(self, text):
		text = self.clean_text(text)
		from google.cloud import language
		from google.cloud.language import enums
		from google.cloud.language import types
		entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
									 'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')
		client = language.LanguageServiceClient()
		document = types.Document(
			content=text,
			type=enums.Document.Type.PLAIN_TEXT)
		# Detects the sentiment of the text
		result = client.analyze_entity_sentiment(document, "UTF8")
		print result
		data = {}
		for entity in result.entities:
			#print "{} {}".format(entity.name, entity.sentiment.magnitude)
			item = {
				'name': entity.name,
				'type': entity_type[entity.type],
				'magnitude': entity.sentiment.magnitude,
				'salience': entity.salience,
				'sentiment': entity.sentiment.score
			}
			data[entity.name] = item
		return data
