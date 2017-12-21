import db
from pprint import pprint

class article():
	def __init__(self, article={}):
		self.db = db.Db()
		self.article = {}

	def exists(self, title):
		if not self.find(title):
			return False
		return True

	def find_by_id(self, article_id):
		query = "SELECT * FROM article WHERE 1 = 1 AND id = {id}".format(id=article_id)
		self.db.query(query)
		article = self.db.cursor.fetchone()
		self.article = self.toDict(article)
		return self

	def toDict(self, article):
		""" Need better logic here """
		if article == None: return None
		return {
			'id': article[0],
			'title': article[1],
			'summary': article[2],
			'source': article[3],
			'author_id': article[4],
			'content': article[5],
			'date': article[6],
			'link': article[7]
		}

	def getDict(self):
		return self.article

	def get(self, key=None):
		if key:
			return self.article[key]
		return self.article

	def update(self, key, value):
		self.article[key] = value

	def find_by_title(self, title=None):
		self.db.query("SELECT * FROM article WHERE title = '{}'".format(title))
		article = self.db.cursor.fetchone()
		self.article = self.toDict(article)
		return self

	def create(self, article):
		try:
			query = "REPLACE INTO article (`title`, `summary`, `source`, `author_id`, `content`, `date`, `link`) VALUES(%s,%s,%s,%s,%s,%s,%s)"
			cursor = self.db.cursor
			cursor.execute(query, (article['title'],
															article['summary'][:255],
															article['source'],
															article['author_id'],
															article['content'],
															article['date'],
															article['link']
														))
		except self.db.mysql.connector.Error as err:
			print(cursor.statement)
			print("Something went wrong: {}".format(err))

	def new(self, article={}):
		self.article = {}
		self.article['title'] = article['title'] if article['title'] else ''
		self.article['summary'] = article['summary'] if article['summary'] else ''
		self.article['source'] =  article['source'] if article['source'] else ''
		self.article['author_id'] = article['author_id'] if article['author_id'] else ''
		self.article['content'] = article['content'] if article['content'] else ''
		self.article['date'] = article['date'] if article['date'] else ''
		self.article['link'] = article['link'] if article['link'] else ''
		return self

	def save(self):
		self.create(self.article)
		self.db.save()
		return self

	def last_id(self):
		self.db.cursor.fetchall
		return self.db.cursor.lastrowid

	def getAll(self, with_enitities=False):
		self.db.query("SELECT * FROM article WHERE 1=1")
		articles = self.db.cursor.fetchall()
		data = []
		pprint(articles)
		for article in articles:
			obj = self.article = self.toDict(article)
			obj['entities'] = self.entities()
			data.append(obj)
		return data

	def entities(self):
		from models.entity import entities
		entities = entities()
		return entities.forArticle(self.article.get('id'))
