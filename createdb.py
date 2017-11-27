from pony.orm import *
import os

db = Database()
db.bind(provider='mysql', host=os.environ['DB_HOST'], user=os.environ['DB_USER'], passwd=os.environ['DB_PASS'], db=os.environ['DB_NAME'])

class Source(db.Entity):
  id = PrimaryKey(int, auto=True)
  name = Required(str)
  url = Required(str)
  articles = Set(Article)

class Entity(db.Entity):
  id = PrimaryKey(int, auto=True)
  name = Required(str)

class Author(db.Entity):
  id = PrimaryKey(int, auto=True)
  name = Required(str)
  first_name = Optional(str)
  last_name = Optional(str)
  
class Article(db.Entity):
  id = PrimaryKey(int, auto=True)
  title = Required(str)
  summary = Optional(str)
  author = Set(Author)
  source = Required(Source)
  