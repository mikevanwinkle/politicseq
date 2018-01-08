import db
from pprint import pprint

class author():
	def __init__(self):
		self.db = db.Db()

	def exists(self, name):
		if not self.find(name):
			return False
		return True

	def find(self, name=None):
		author = self.db.query('SELECT * FROM author WHERE name = "{}"'.format(name.encode("utf-8")))
		author = author.fetchone()
		if author == None: return False
		return {
			'id': author[0],
			'name': author[1],
			'first_name': author[2],
			'last_name': author[3]
		}

	def create(self, author):
		try:
			if 'first_name' not in author.keys():
				author['first_name'] = ''
			if 'last_name' not in author.keys():
				author['last_name'] = ''
			query = "INSERT INTO author (`name`, `first_name`, `last_name`) VALUES(%s,%s,%s)"
			cursor = self.db.cursor
			cursor.execute(query, (author['name'].encode("utf-8"), author['first_name'].encode("utf-8"), author['last_name'].encode("utf-8")))
		except self.db.mysql.connector.Error as err:
			print(cursor.statement)
			print("Something went wrong: {}".format(err))
