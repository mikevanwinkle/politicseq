import requests, json, feedparser, pprint, os
from bs4 import BeautifulSoup
from stanfordcorenlp import StanfordCoreNLP
import messager as m

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

class PoliticsEQApi():
  def __init__(self):
    pass
  
  def sources(self, match=None):
    r = requests.get('{0}/sources'.format(BASE_URL), verify=requests.certs.where())  
    return r.json()['results']
  
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
       