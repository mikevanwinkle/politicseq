import db
from pprint import pprint

class entities():
  def __init__(self):
	  self.db = db.Db()

  def forArticle(self, article_id, avg=False):
    q = "SELECT * FROM `entity` WHERE `article_id` = {id};".format(id=article_id)
    if avg:
      q = "SELECT name, type, AVG(sentiment), AVG(salience), AVG(magnitude) FROM `entity` WHERE `article_id` = {id} GROUP BY name, type;".format(id=article_id)
    self.db.query(q)
    results = self.db.cursor.fetchall()
    data = []
    for result in results:
      en = entity()
      data.append(en.toDict(result))
    return data


class entity():
  def __init__(self, entity={}):
    self.db = db.Db()
    self.fields = ['id','name','article_id','type','sentiment','salience','magnitude']
    self.entity = {}
    return None

  def find_by_name_article_id(self, name, article_id):
    self.db.query("SELECT * FROM entity WHERE name = '{name}' AND article_id = {article_id}".format(name=name, article_id=article_id))
    entity = self.db.cursor.fetchone()
    self.entity = self.toDict(entity)
    return self

  def toDict(self,entity):
    d = {}
    for x in range(0, len(self.fields)):
      d[self.fields[x]] = entity[x]
    return d

  def new(self, entity):
    for field in self.fields:
      if field in entity.keys():
        self.entity[field] = entity[field]
    return self

  def create(self, entity):
    try:
      query = "INSERT INTO entity (`name`, `article_id`, `type`, `sentiment`, `salience`, `magnitude`) VALUES(%s,%s,%s,%s,%s,%s)"
      cursor = self.db.cursor
      cursor.execute(query, ( entity['name'],
															entity['article_id'],
															entity['type'],
															entity['sentiment'],
                              entity['salience'],
                              entity['magnitude']
														))
    except self.db.mysql.connector.Error as err:
			print(cursor.statement)
			print("Something went wrong: {}".format(err))

  def save(self):
    self.create(self.entity)
    self.entity = {}
    return self

  def commit(self):
    self.db.save()

  def last_id(self):
		self.db.cursor.fetchall
		return self.db.cursor.lastrowid
