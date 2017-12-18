import requests, json, feedparser, pprint, os
from bs4 import BeautifulSoup
from stanfordcorenlp import StanfordCoreNLP
import messager as m
import xml

BASE_URL = 'https://api.politicseq.com'
#NLP_URL = 'http://104.131.130.164' 
NLP_URL = str(os.getenv('NLP_URL'))
NLP_PORT = 9000
nlp = StanfordCoreNLP(NLP_URL, port=NLP_PORT)
sentiment_map = {
  'Verynegative': -1.0,
  'Negative': -0.5,
  'Positive': 0.5,
  'Verypositive': 1.0,
  'Neutral': 0
}

feed_classes = {
  "Breitbart": "the-article"
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
    chars = {
      '\u201c': '"',
      '\u201d': '"',
      '\\xa0': ' ',
      '\\u2019': "'",
      '\\u2013': "-"
    }

    for char, repl in chars.items():
      text = text.replace(char, repl)
    printable = set(string.printable)
    text = filter(lambda x: x in printable, text)
    return text


  def ingest_from_feed_item(self, feed_item, source=None):
    from models.author import author
    from models.article import article
    from dateutil import parser
    import codecs
    author = author()
    articles = article()
    item_auths = []
    for auth in set(feed_item['authors']):
      if not author.exists(auth['name']):
        author.create({'name': auth['name']})
      item_auths.append(author.find(auth['name']))
    item_info = {}
    r = requests.get(feed_item['link'], verify=requests.certs.where())
    summary = BeautifulSoup(self.clean_text(feed_item['summary']), 'html.parser')
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.findAll('article', {'class': feed_classes[source['name']]})
    text = BeautifulSoup(str(text), 'html.parser')
    body = []
    for p in text.findAll('p'):
      body.append(self.clean_text(p.get_text()))
    body = "".join(body)
    feed_item['title'] = self.clean_text(feed_item['title'])
    article = articles.find_by_title(feed_item['title'])
    if not article:
      # saving article
      a = {}
      m.info("Saving {}".format(feed_item['title']))
      articles.new({
          'title': feed_item['title'],
          'summary': summary.get_text(),
          'source': source['id'],
          'author_id': item_auths[0]['id'],
          'content': body,
          'date': parser.parse(feed_item['published']).strftime('%Y-%m-%d %H:%M:%S'), #Fri, 15 Dec 2017 21:21:18 +0000,
          'link': feed_item['link']
      })
      article_id = articles.save()
      m.success("Created {}".format(article_id))
    else:
      m.info("Skipping {}".format(article['title']))

  def fetch_articles_from_src(self, source):
    feed = feedparser.parse(source['url'])
    return feed.entries
  
  def fetch_article_entities(self, article_url):
    r = requests.get(article_url, verify=requests.certs.where())
    soup = BeautifulSoup(r.text, 'html.parser')
    ps = soup.find_all('article')
    for p in ps:
      body = p.get_text()
      #n = requests.post('{0}:{1}'.format(NLP_URL, NLP_PORT), params={'properties': str('sentiment')}, data=sent.encode('utf-8'))
      n = nlp._request('sentiment,ner', body.encode('utf-8'))
      entities = self.extract_entities(n)
      #entities = [(token['word'], token['ner']) for token in s['tokens'] if len(token['ner']) > 1]
      return entities
    
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
       