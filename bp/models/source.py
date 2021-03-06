import db, messager

class source(): 
	def __init__(self):
		self.db = db.Db()
	
	def insert(self, source):
		try:
			query = "INSERT INTO source (`name`, `url`, `type`,`publisher`,`publisher_url`) VALUES(%s,%s,%s,%s,%s)"
			cursor = self.db.cursor
			cursor.execute(query, (source['name'],source['feed_url'], source['format'], source['publisher'], source['publisher_url']))
			self.db.save()
		except self.db.mysql.connector.Error as err:
			messager.info(cursor.statement)
			messager.error("Something went wrong: {}".format(err))

	def get(self, name=None, url=None, type=None, fields='*', order='ASC', order_by='name'):
		query = "SELECT {} FROM source WHERE 1 = 1".format(fields)
		if name:
			query = "{} AND WHERE `name` = {}".format(query, name)
		if url: 
			query = "{} AND WHERE `url` = {}".format(query, url)
		if type:
			query = "{} AND WHERE `type` = {}".format(query, type)
		# order
		query = "{} ORDER BY {} {}".format(query, order_by, order)
		print query
		result = self.db.query(query)
		data = []
		for row in result.fetchall():
			data.append({
				'id': row[0],
				'name': row[1],
				'type': row[2],
				'url': row[3],
				'publisher': row[4],
				'publisher_url': row[5]
			})
		return data
