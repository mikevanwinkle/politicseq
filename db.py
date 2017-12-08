#!bin/python2.7
import mysql.connector,os
from mysql.connector import errorcode

class Db:
	class __Connection:
		def __init__(self):
			self.host = os.environ['DB_HOST']
			self.db = os.environ['DB_NAME']
			self.user = os.environ['DB_USER']
			self.password = os.environ['DB_PASS']
			self.connection = mysql.connector.connect(host=self.host, database=self.db, user=self.user, password=self.password)
			self.cursor = self.connection.cursor()

	connection = None
	def __init__(self):
		if not Db.connection:
			Db.connection = Db.__Connection()

	def __getattr__(self, name):
		return getattr(self.connection, name)

	def query(self, query):
		self.cursor.execute(query)
		return self.cursor