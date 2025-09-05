from app.models import Category, Event, User
from app import app
import hashlib


def load_categories(): 
    return Category.query.order_by('id').all()


def load_events(cate_id=None, kw=None, page=1): 
    query = Event.query

    if(kw):
        query = query.filter(Event.name.contains(kw))

    if(cate_id): 
        query = query.filter(Event.category_id == cate_id)

    page_size = app.config.get("PAGE_SIZE")
    start = (page - 1)* page_size
    query = query.slice(start, start + page_size)

    return query.all()

def count_events():
    return Event.query.count()

def auth_user(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username), 
                             User.password.__eq__(password)).first()

def get_user_by_id(id):
    return User.query.get(id)
