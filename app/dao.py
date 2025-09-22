from app.models import Category, Event, User, Gender, Ticket, TicketDetail, SeatType, Comment
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

    page_size = app.config.get("PAGE_SIZE_HOME")
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
        dob_confirm = datetime.strptime(dob, "%Y-%m-%d").date()

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
        # Tạo ticket (1 giao dịch mua)
        t = Ticket(user=current_user)
        db.session.add(t)
        #db.session.flush()  # để lấy id ngay

        for c in cart.values():
            event_id = c['id']
            event = Event.query.get(event_id)

            # Nếu có vé thường
            if c['normal_quantity'] > 0:
                for i in range(c['normal_quantity']):
                    d_normal = TicketDetail(
                        unit_price=c['normal_price'],
                        ticket=t,
                        event_id=event_id,
                        seat_type=SeatType.NORMAL,
                        checked_in=False  # mặc định chưa check-in
                    )
                    db.session.add(d_normal)
                event.normal_quantity -= c['normal_quantity']

            # Nếu có vé VIP
            if c['vip_quantity'] > 0:
                for i in range(c['vip_quantity']):
                    d_vip = TicketDetail(
                        unit_price=c['vip_price'],
                        ticket=t,
                        event_id=event_id,
                        seat_type=SeatType.VIP,
                        checked_in=False
                    )
                    db.session.add(d_vip)
                event.vip_quantity -= c['vip_quantity']

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

def load_comments(event_id):
    return Comment.query.filter(Comment.event_id.__eq__(event_id)).order_by(-Comment.id).all()

def add_comment(content, event_id):
    c = Comment(content=content, event_id=event_id, user=current_user)
    db.session.add(c)
    db.session.commit()

    return c

def update_user_info(user_id, name, phone, email, dob, gender, avatar=None):
    u = User.query.get(user_id)
    if u:
        u.name = name
        u.phone = phone
        u.email = email

        if dob:
            u.dob = datetime.strptime(dob, "%Y-%m-%d").date()

        if gender == "MALE":
            u.gender = Gender.MALE
        elif gender == "FEMALE":
            u.gender = Gender.FEMALE
        else:
            u.gender = Gender.OTHER

        if avatar:
            result = cloudinary.uploader.upload(avatar)
            u.avatar = result.get("secure_url")

        db.session.commit()


def check_password(username, password):
    password = str(hashlib.md5(password.encode("utf-8")).hexdigest())
    u = User.query.filter(User.username == username,
                          User.password == password).first()
    return u is not None


def change_password(user_id, new_password):
    u = User.query.get(user_id)
    if u:
        u.password = str(hashlib.md5(new_password.encode("utf-8")).hexdigest())
        db.session.commit()

def get_events_by_user(user_id, page=1):
    subq = (
        db.session.query(
            TicketDetail.event_id.label('event_id'),
            func.max(Ticket.created_date).label('last_purchase')
        )
        .join(Ticket, Ticket.id == TicketDetail.ticket_id)
        .filter(Ticket.user_id == user_id)
        .group_by(TicketDetail.event_id)
        .subquery()
    )

    base_query = (
        db.session.query(Event)
        .join(subq, Event.id == subq.c.event_id)
        .order_by(subq.c.last_purchase.desc())
    )

    page_size = app.config.get("PAGE_SIZE_MY_TICKETS")
    total = base_query.count()

    events = (
        base_query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return events, total


def get_tickets_by_user_and_event(user_id, event_id):
    # Lấy chi tiết vé user mua cho 1 event
    return (db.session.query(TicketDetail)
            .join(Ticket, Ticket.id == TicketDetail.ticket_id)
            .filter(Ticket.user_id == user_id, TicketDetail.event_id == event_id)
            .order_by(Ticket.created_date.desc())
            .all())

def get_events_by_organizer(organizer_id):
    return Event.query.filter(Event.organizer_id == organizer_id).all()

def add_event(name, description, datetime, vip_price, normal_price,
              vip_quantity, normal_quantity, address_detail, province, banner, category_id, organizer_id):
    banner_confirm = None
    if (banner):
        result = cloudinary.uploader.upload(banner)
        banner_confirm = result.get('secure_url')
    e = Event(
        name=name,
        description=description,
        datetime=datetime,
        vip_price=vip_price,
        normal_price=normal_price,
        vip_quantity=vip_quantity,
        normal_quantity=normal_quantity,
        address_detail=address_detail,
        province=province,
        banner=banner_confirm,
        category_id=category_id,
        organizer_id=organizer_id
    )
    db.session.add(e)
    db.session.commit()
    return e

def update_event(event_id, organizer_id, **kwargs):
    e = Event.query.filter_by(id=event_id, organizer_id=organizer_id).first()
    if not e:
        return None

    for key, value in kwargs.items():
        if key == 'banner' and value:  # Nếu có file banner mới
            # upload file lên Cloudinary
            upload_result = cloudinary.uploader.upload(value)
            setattr(e, key, upload_result['secure_url'])
        elif key != 'banner':  # các trường khác
            setattr(e, key, value)

    db.session.commit()
    return e

def delete_event(event_id, organizer_id):
    e = Event.query.filter_by(id=event_id, organizer_id=organizer_id).first()
    if e:
        db.session.delete(e)
        db.session.commit()
        return True
    return False
if __name__ == '__main__':
    with app.app_context():
        print(revenue_stats_by_events())
