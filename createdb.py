from pony.orm import *
import os

def load_db():
  db = Database()
  db.bind(provider='mysql', host=os.environ['DB_HOST'], user=os.environ['DB_USER'], passwd=os.environ['DB_PASS'], db=os.environ['DB_NAME'])
  return db

db = load_db()

class Source(db.Entity):
  id = PrimaryKey(int, auto=True)
  name = Required(str)
  url = Required(str)
  articles = Set(lambda: Article)

class XEntity(db.Entity):
  id = PrimaryKey(int, auto=True)
  name = Required(str)
  article = Required(lambda: Article)
  type = Required(str)
  sentiment = Required(float)

class Author(db.Entity):
  id = PrimaryKey(int, auto=True)
  name = Required(str)
  first_name = Optional(str)
  last_name = Optional(str)
  articles = Set(lambda: Article)
  
class Article(db.Entity):
  id = PrimaryKey(int, auto=True)
  title = Required(str)
  summary = Optional(str)
  author = Set(Author)
  source = Required(Source)
  entities = Set(XEntity)
