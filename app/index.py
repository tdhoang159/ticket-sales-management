from flask import render_template, request, redirect, session, jsonify
from app import app, dao, login, utils
import math
from flask_login import login_user, logout_user
from app.models import UserRole

@app.route("/")
def index(): 
    cate_id = request.args.get("category_id")
    kw = request.args.get("kw")
    current_page = request.args.get("page", 1)
    events = dao.load_events(cate_id=cate_id, kw=kw, page=int(current_page))
    page_size = app.config.get("PAGE_SIZE", 8)
    total = dao.count_events(cate_id=cate_id, kw=kw)

    return render_template("index.html", events = events, 
                           pages = math.ceil(total/ page_size), 
                           current_page=int(current_page), cate_id=cate_id, kw=kw)


@app.route("/login", methods=['get', 'post'])
def login_process(): 
    login_error_message = None
    if(request.method.__eq__('POST')):
        username = request.form.get('username')
        password = request.form.get('password')
        auth_user = dao.auth_user(username=username, password=password)

        if(auth_user):
            login_user(auth_user)
            return redirect('/')
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
        'cart_stats': utils.stats_cart(session.get('ticket_cart'))
    }

@app.route('/ticket-cart')
def ticket_cart():
    return render_template("layout/ticket-cart.html")

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
