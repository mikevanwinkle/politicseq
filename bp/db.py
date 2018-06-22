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
			self.mysql = mysql
			self.connection = mysql.connector.connect(host=self.host, database=self.db, user=self.user, password=self.password)
			self.cursor = self.connection.cursor(buffered=True)

	connection = None
	def __init__(self):
		if not Db.connection:
			Db.connection = Db.__Connection()

	def __getattr__(self, name):
		return getattr(self.connection, name)

	def query(self, query):
		self.cursor.execute(query)
		return self.cursor

	def add_column(self, table_name, column):
		query = "ALTER TABLE `{}` ADD COLUMN ( {} );"
		self.query(query.format(table_name, column))

	def save(self):
		self.connection.connection.commit()

	def insert_id(self):
		self.connection.cursor.lastrowid