from flask import render_template, request, redirect, session, jsonify
from app import app, dao, login, utils
import math
from datetime import datetime
from flask_login import login_user, logout_user, login_required
from urllib.parse import urlencode
from app.models import UserRole, Comment


@app.route("/")
def index(): 
    # Loại sự kiện (danh sách checkbox  list)
    cate_ids = request.args.getlist("event_type")

     # Giá vé
    price_min = request.args.get("price_min")
    price_max = request.args.get("price_max")

    # Thời gian
    datetime_from = request.args.get("datetime_from")
    datetime_to = request.args.get("datetime_to")
    if datetime_from:
        datetime_from = datetime.fromisoformat(datetime_from)
    if datetime_to:
        datetime_to = datetime.fromisoformat(datetime_to)

    # Địa điểm
    province = request.args.get("location")

    #Lọc theo loại sự kiện
    cate_id = request.args.get("category_id")

    #Tìm kiếm sự kiện theo tên
    kw = request.args.get("kw")

    #Trang đang đứng
    current_page = request.args.get("page", 1)

    #Số event hiện trên 1 trang
    page_size = app.config.get("PAGE_SIZE", 8)

    ticket_type = request.args.getlist('ticket_type')

    #Event trả về
    events = dao.load_events(cate_id=cate_id, kw=kw, page=int(current_page), cate_ids=cate_ids, price_min=price_min, price_max=price_max, datetime_from=datetime_from, datetime_to=datetime_to, province=province, ticket_types=ticket_type)

    #Đếm tổng số event trong 1 request để tính tổng số trang
    total = dao.count_events(cate_id=cate_id, kw=kw, cate_ids=cate_ids, price_min=price_min, price_max=price_max, datetime_from=datetime_from, datetime_to=datetime_to, province=province, ticket_types=ticket_type)

    params = []
    for key in request.args:
        if key == "page":
            continue
        for v in request.args.getlist(key):   # hỗ trợ checkbox (key lặp)
            if v is None or v == "":
                continue
            params.append((key, v))
    base_qs = urlencode(params)

    return render_template("index.html", events = events, 
                           pages = math.ceil(total/ page_size), 
                           current_page=int(current_page), cate_id=cate_id, kw=kw, base_qs=base_qs)


@app.route("/login", methods=['get', 'post'])
def login_process(): 
    login_error_message = None
    if(request.method.__eq__('POST')):
        username = request.form.get('username')
        password = request.form.get('password')
        auth_user = dao.auth_user(username=username, password=password)

        if(auth_user):
            login_user(auth_user)
            next = request.args.get('next')
            return redirect(next if next else '/')
        else:
            login_error_message = "Sai tên đăng nhập hoặc mật khẩu! Vui lòng đăng nhập lại."

    return render_template("layout/login.html", login_error_message=login_error_message)

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)

@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/')

@app.route("/register", methods=['get', 'post'])
def register_process():
    error_message = None
    if(request.method.__eq__('POST')):
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        gender = request.form.get('gender')  # giá trị là "MALE", "FEMALE", "OTHER"
        dob = request.form.get('dob')  # yyyy-mm-dd
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        avatar = request.files.get('avatar')
        if(password.__eq__(confirm_password)):
            duplicate_user_error = dao.get_user_by_username(username)
            if(duplicate_user_error): 
                error_message = "Tên đăng nhập này đã được sử dụng ở 1 tài khoản khác"
            else:
                dao.add_user(name=name, phone=phone, email=email, gender=gender, dob=dob, username=username, password=password, avatar=avatar)
                return redirect('/login')
        else:
            error_message = "Mật khẩu không khớp. Vui lòng nhập lại!"

    return render_template("layout/register.html", error_message=error_message)

@app.route('/login-admin', methods=['post'])
def login_admin_process():
    login_error_message = None
    username = request.form.get('username')
    password = request.form.get('password')
    auth_user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)

    if(auth_user):
        login_user(auth_user)
        return redirect('/admin')
    else:
        login_error_message = "Sai tên đăng nhập hoặc mật khẩu! Vui lòng đăng nhập lại."

@app.route('/api/ticket-cart', methods=['post'])
def add_to_ticket_cart():
    ticket_cart = session.get('ticket_cart')
    if not ticket_cart:
        ticket_cart = {}

    id = str(request.json.get('id'))
    event_name = request.json.get('event_name')
    vip_price = request.json.get('vip_price')
    vip_quantity = request.json.get('vip_quantity')
    normal_price = request.json.get('normal_price')
    normal_quantity = request.json.get('normal_quantity')

    if id in ticket_cart:
        ticket_cart[id]['normal_quantity'] += 1;
    else:
        ticket_cart[id] = {
            "id": id,
            "event_name": event_name,
            "vip_price": vip_price,
            "vip_quantity": 0,
            "normal_price": normal_price,
            "normal_quantity": 1
        }

    session['ticket_cart'] = ticket_cart
    print(ticket_cart)

    return jsonify(utils.stats_cart(ticket_cart))

@app.context_processor
def common_response():
    return {
        'categories': dao.load_categories(),
        'provinces': dao.load_provinces(),
        'cart_stats': utils.stats_cart(session.get('ticket_cart'))
    }

@app.route('/ticket-cart')
def ticket_cart():
    return render_template("layout/ticket-cart.html")

@app.route('/api/ticket-cart/<event_id>', methods=['put'])
def update_ticket_cart(event_id):
    ticket_cart = session.get('ticket_cart')
    if ticket_cart and event_id in ticket_cart:
        item = ticket_cart[event_id]


        vip_quantity = request.json.get('vip_quantity')
        normal_quantity = request.json.get('normal_quantity')

        if vip_quantity is not None:
            item['vip_quantity'] = int(vip_quantity)
        if normal_quantity is not None:
            item['normal_quantity'] = int(normal_quantity)

        ticket_cart[event_id] = item
        session['ticket_cart'] = ticket_cart

    return jsonify(utils.stats_cart(ticket_cart))

@app.route('/api/ticket-cart/<event_id>', methods=['delete'])
def delete_ticket_cart(event_id):
    ticket_cart = session.get('ticket_cart')
    if event_id in ticket_cart:
        del ticket_cart[event_id]
    if ticket_cart:
        session['ticket_cart'] = ticket_cart
    else:
        session.pop('ticket_cart')

    return jsonify(utils.stats_cart(ticket_cart))

@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    ticket_cart = session.get('ticket_cart')

    try:
        dao.add_ticket(ticket_cart)
    except:
        return jsonify({'status': 500})
    else:
        del session['ticket_cart']
        return jsonify({'status': 200})

@app.route('/event/<int:event_id>')
def event_details(event_id):
    return render_template("layout/event_details.html",
                           event=dao.get_event_by_id(event_id),
                           comments = dao.load_comments(event_id))

@app.route('/api/event/<int:event_id>/comments', methods=['post'])
@login_required
def add_comment(event_id):
    content = request.json.get('content')
    c = dao.add_comment(content=content, event_id=event_id)

    return jsonify({
        "content": c.content,
        "created_date": c.created_date,
        "user": {
            "avatar": c.user.avatar
        }
    })
if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
