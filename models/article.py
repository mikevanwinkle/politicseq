import db
from pprint import pprint

class article(): 
	def __init__(self):
		self.db = db.Db()

	def exists(self, title):
		if not self.find(title): 
			return False
		return True

	def find_by_title(self, title=None):
		article = self.db.query("SELECT * FROM article WHERE title = '{}'".format(title))
		article = article.fetchone()
		if article == None: return False
		return self.article_to_dict(article)

	def article_to_dict(self, article):
		""" Need better logic here """
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

	def create(self, article):
		try:
			query = "INSERT INTO article (`title`, `summary`, `source`, `author_id`, `content`, `date`, `link`) VALUES(%s,%s,%s,%s,%s,%s,%s)"
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
		self.article['content'] = article['author_id'] if article['author_id'] else ''
		self.article['date'] = article['date'] if article['date'] else ''
		self.article['link'] = article['link'] if article['link'] else ''
		return self

	def save(self):
		self.create(self.article)
		self.db.save()
