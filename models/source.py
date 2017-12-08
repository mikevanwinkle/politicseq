import db

class source(): 
	def __init__(self):
		self.db = db.Db()
	
	def insert(self):
		self.db.query("REPLACE INTO source (`name`, `url`, `type`) VALUES('{}','{}','{}')".format('test','test', 'test'))
