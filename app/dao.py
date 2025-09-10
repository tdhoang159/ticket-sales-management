from app.models import Category, Event, User, Gender
from app import app, db
import hashlib
import datetime
import cloudinary.uploader


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

def count_events(cate_id=None, kw=None):
    query = Event.query

    if kw:
        query = query.filter(Event.name.contains(kw))

    if cate_id:
        query = query.filter(Event.category_id == cate_id)

    return query.count()

def auth_user(username, password, role=None):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username),  
                           User.password.__eq__(password))
    if (role):
        u = u.filter(User.user_role.__eq__(role))
    return u.first()

def get_user_by_id(id):
    return User.query.get(id)

def get_user_by_username(username):
    return User.query.filter(User.username.__eq__(username)).first()

def add_user(name, phone, email, gender, dob, username, password, avatar=None):
    password_confirm = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    gender_confirm = None
    if gender == "MALE":
        gender_confirm = Gender.MALE
    elif gender == "FEMALE":
        gender_confirm = Gender.FEMALE
    elif gender == "OTHER":
        gender_confirm = Gender.OTHER

    dob_confirm = None
    if dob:
        dob_confirm = datetime.datetime.strptime(dob, "%Y-%m-%d").date()

    avatar_confirm = None
    if (avatar):
        result = cloudinary.uploader.upload(avatar)
        avatar_confirm = result.get('secure_url')

    new_user = User(name=name, phone=phone, email=email, gender=gender_confirm, dob=dob_confirm, username=username, password=password_confirm, avatar=avatar_confirm)
    db.session.add(new_user)
    db.session.commit()
