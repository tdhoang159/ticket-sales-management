from app.models import Category, Event, User, Gender, Ticket, TicketDetail, SeatType
from app import app, db
import hashlib
import datetime
import cloudinary.uploader
from sqlalchemy import and_, func, case
from flask_login import current_user
from datetime import datetime


def load_categories():
    return Category.query.order_by('id').all()


def load_provinces():
    provinces = db.session.query(Event.province).distinct().all()
    return [p[0] for p in provinces if p[0] is not None]


def load_events(cate_id=None, kw=None, page=1, cate_ids=None, price_min=None, price_max=None, datetime_from=None,
                datetime_to=None, province=None, ticket_types=None):
    query = Event.query

    # Lọc theo nhiều loại sự kiện
    if cate_ids:
        query = query.filter(Event.category_id.in_(cate_ids))

    if ticket_types == ["vip"]:  # chỉ VIP
        if price_min: query = query.filter(Event.vip_price >= price_min)
        if price_max: query = query.filter(Event.vip_price <= price_max)

    elif ticket_types == ["normal"]:  # chỉ thường
        if price_min: query = query.filter(Event.normal_price >= price_min)
        if price_max: query = query.filter(Event.normal_price <= price_max)

    else:  # cả 2 hoặc không chọn gì
        conds = []
        if price_min:
            conds.append(Event.normal_price >= price_min)
        if price_max:
            conds.append(Event.vip_price <= price_max)
        if conds:
            query = query.filter(and_(*conds))

    # Lọc theo thời gian
    if datetime_from:
        query = query.filter(Event.datetime >= datetime_from)
    if datetime_to:
        query = query.filter(Event.datetime <= datetime_to)

    # Lọc theo địa điểm
    if province:
        query = query.filter(Event.province == province)

    if (kw):
        query = query.filter(Event.name.contains(kw))

    if (cate_id):
        query = query.filter(Event.category_id == cate_id)

    page_size = app.config.get("PAGE_SIZE")
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all()


def count_events(cate_id=None, kw=None, cate_ids=None, price_min=None, price_max=None, datetime_from=None,
                 datetime_to=None, province=None, ticket_types=None):
    query = Event.query

    # Lọc theo nhiều loại sự kiện
    if cate_ids:
        query = query.filter(Event.category_id.in_(cate_ids))

    if ticket_types == ["vip"]:  # chỉ VIP
        if price_min: query = query.filter(Event.vip_price >= price_min)
        if price_max: query = query.filter(Event.vip_price <= price_max)

    elif ticket_types == ["normal"]:  # chỉ thường
        if price_min: query = query.filter(Event.normal_price >= price_min)
        if price_max: query = query.filter(Event.normal_price <= price_max)

    else:  # cả 2 hoặc không chọn gì
        conds = []
        if price_min:
            conds.append(Event.normal_price >= price_min)
        if price_max:
            conds.append(Event.vip_price <= price_max)
        if conds:
            query = query.filter(and_(*conds))

    # Lọc theo thời gian
    if datetime_from:
        query = query.filter(Event.datetime >= datetime_from)
    if datetime_to:
        query = query.filter(Event.datetime <= datetime_to)

    # Lọc theo địa điểm
    if province:
        query = query.filter(Event.province == province)

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

    new_user = User(name=name, phone=phone, email=email, gender=gender_confirm, dob=dob_confirm, username=username,
                    password=password_confirm, avatar=avatar_confirm)
    db.session.add(new_user)
    db.session.commit()


def add_ticket(cart):
    if cart:
        t = Ticket(user=current_user)
        db.session.add(t)

        for c in cart.values():
            event_id = c['id']
            # Nếu có vé thường
            if c['normal_quantity'] > 0:
                d_normal = TicketDetail(
                    quantity=c['normal_quantity'],
                    unit_price=c['normal_price'],
                    ticket=t,
                    event_id=event_id,
                    seat_type=SeatType.NORMAL
                )
                db.session.add(d_normal)

            # Nếu có vé VIP
            if c['vip_quantity'] > 0:
                d_vip = TicketDetail(
                    quantity=c['vip_quantity'],
                    unit_price=c['vip_price'],
                    ticket=t,
                    event_id=event_id,
                    seat_type=SeatType.VIP
                )
                db.session.add(d_vip)

        db.session.commit()


def revenue_stats_by_events():
    return ((
                db.session.query(
                    Event.id,
                    Event.name,
                    func.sum(TicketDetail.quantity * TicketDetail.unit_price),
                    func.sum(case((TicketDetail.seat_type == SeatType.VIP, TicketDetail.quantity), else_=0)),
                    func.sum(case((TicketDetail.seat_type == SeatType.NORMAL, TicketDetail.quantity), else_=0)),
                    func.sum(TicketDetail.quantity)
                )
                .join(TicketDetail, TicketDetail.event_id.__eq__(Event.id)))
            .order_by(Event.id)
            .group_by(Event.id)
            .all())


def revenue_stats_by_time(time='month', year=datetime.now().year):
    return ((db.session.query(func.extract(time, Ticket.created_date),
                              func.sum(TicketDetail.quantity * TicketDetail.unit_price))
             .join(TicketDetail, TicketDetail.ticket_id.__eq__(Ticket.id)))
            .group_by(func.extract(time, Ticket.created_date))
            .filter(func.extract('year', Ticket.created_date).__eq__(year))
            .order_by(func.extract(time, Ticket.created_date)).all())


def count_event_by_category():
    return (db.session.query(Category.id, Category.name, func.count(Event.id))
            .join(Event, Event.category_id.__eq__(Category.id))).group_by(Category.id).all()

def get_event_by_id(id):
    return Event.query.get(id)

if __name__ == '__main__':
    with app.app_context():
        print(revenue_stats_by_events())
