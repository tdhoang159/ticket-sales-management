import hashlib
import hmac
import urllib
import uuid
import math

from flask import render_template, request, redirect, session, jsonify
from app import app, dao, login, utils
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlencode
from app.models import UserRole
from app.vnpay import VNPAY
from flask import flash

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
    page_size = app.config.get("PAGE_SIZE_HOME", 8)

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
        ticket_cart[id]['normal_quantity'] += normal_quantity
        ticket_cart[id]['vip_quantity'] += vip_quantity
    else:
        ticket_cart[id] = {
            "id": id,
            "event_name": event_name,
            "vip_price": vip_price,
            "vip_quantity": vip_quantity,
            "normal_price": normal_price,
            "normal_quantity": normal_quantity
        }

    session['ticket_cart'] = ticket_cart
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
    if not ticket_cart:
        return jsonify({'status': 400, 'message': 'Giỏ vé rỗng!'})

    cart_stats = utils.stats_cart(ticket_cart)
    amount = int(cart_stats['total_amount']) * 100  # VNPAY yêu cầu đơn vị VNĐ * 100

    vnp = VNPAY(
        app.config['VNPAY_TMN_CODE'],
        app.config['VNPAY_HASH_SECRET_KEY'],
        app.config['VNPAY_PAYMENT_URL'],
        app.config['VNPAY_RETURN_URL']
    )

    vnp.add_param('vnp_Version', '2.1.0')
    vnp.add_param('vnp_Command', 'pay')
    vnp.add_param('vnp_TmnCode', app.config['VNPAY_TMN_CODE'])
    vnp.add_param('vnp_Amount', str(amount))
    vnp.add_param('vnp_CurrCode', 'VND')
    vnp.add_param('vnp_TxnRef', str(uuid.uuid4()))  # Mã giao dịch unique
    vnp.add_param('vnp_OrderInfo', f'Thanh toan don hang cua {session["_user_id"]}')
    vnp.add_param('vnp_OrderType', 'other')
    vnp.add_param('vnp_Locale', 'vn')
    vnp.add_param('vnp_ReturnUrl', app.config['VNPAY_RETURN_URL'])
    vnp.add_param('vnp_IpAddr', request.remote_addr)
    vnp.add_param('vnp_CreateDate', datetime.now().strftime('%Y%m%d%H%M%S'))

    payment_url = vnp.get_payment_url()
    return jsonify({'status': 200, 'payment_url': payment_url})

@app.route('/vnpay_return')
def vnpay_return():
    inputData = dict(request.args)
    vnp_SecureHash = inputData.pop('vnp_SecureHash', None)

    sortedData = sorted(inputData.items())
    queryString = urllib.parse.urlencode(sortedData)

    hashValue = hmac.new(
        bytes(app.config['VNPAY_HASH_SECRET_KEY'], 'utf-8'),
        queryString.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()

    if hashValue == vnp_SecureHash:
        if inputData['vnp_ResponseCode'] == '00':
            # Thanh toán thành công -> lưu vé
            dao.add_ticket(session.get('ticket_cart'))
            session.pop('ticket_cart', None)
            return render_template("layout/payment_success.html", data=inputData)
        else:
            return render_template("layout/payment_fail.html", data=inputData)
    else:
        return "Sai chữ ký hash!"

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

@app.route("/profile", methods=["get", "post"])
@login_required
def profile():
    error_message = None
    success_message = None
    success_updateInfo_message=None
    show_change_password = False

    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "update_info":
            # Form cập nhật thông tin
            name = request.form.get("name")
            phone = request.form.get("phone")
            email = request.form.get("email")
            dob = request.form.get("dob")
            gender = request.form.get("gender")
            avatar = request.files.get("avatar")

            dao.update_user_info(
                user_id=current_user.id,
                name=name,
                phone=phone,
                email=email,
                dob=dob,
                gender=gender,
                avatar=avatar
            )
            success_updateInfo_message = "Cập nhật thông tin thành công!"
            show_change_password = False

        elif form_type == "change_password":
            # Form đổi mật khẩu
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            show_change_password = True
            if not dao.check_password(current_user.username, current_password):
                error_message = "Mật khẩu cũ không chính xác!"
            elif new_password != confirm_password:
                error_message = "Mật khẩu xác nhận không khớp!"
            else:
                dao.change_password(current_user.id, new_password)
                success_message = "Đổi mật khẩu thành công!"

    return render_template(
        "layout/profile.html",
        user=current_user,
        error_message=error_message,
        success_message=success_message,
        success_updateInfo_message=success_updateInfo_message,
        show_change_password = show_change_password
    )

@app.route("/my-tickets")
@login_required
def my_tickets():
    page = request.args.get("page", 1, type=int)
    page_size = app.config.get("PAGE_SIZE_MY_TICKETS", 5)

    events, total = dao.get_events_by_user(current_user.id, page=page)

    return render_template("layout/my_tickets.html",
                           events=events,
                           pages=math.ceil(total / page_size),
                           current_page=page)


@app.route("/my-tickets/<int:event_id>")
@login_required
def my_tickets_details(event_id):
    event = dao.get_event_by_id(event_id)
    tickets = dao.get_tickets_by_user_and_event(current_user.id, event_id)
    return render_template("layout/my_ticket_details.html", event=event, tickets=tickets)


@app.route('/login-organizer', methods=['get', 'post'])
def login_organizer_process():
    login_error_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        auth_user = dao.auth_user(username=username, password=password, role=UserRole.ORGANIZER)
        if auth_user:
            login_user(auth_user)
            return redirect('/organizer/dashboard')
        else:
            login_error_message = "Sai tên đăng nhập hoặc mật khẩu!"

    return render_template("layout/login_organizer.html", login_error_message=login_error_message)


@app.route('/organizer/dashboard')
@login_required
def organizer_dashboard():
    if current_user.user_role != UserRole.ORGANIZER:
        return "Bạn không có quyền truy cập!", 403

    events = dao.get_events_by_organizer(current_user.id)
    return render_template("organizer/dashboard.html", events=events)


# Thêm sự kiện mới
@app.route('/organizer/events/create', methods=['get', 'post'])
@login_required
def create_event():
    if current_user.user_role != UserRole.ORGANIZER:
        return "Bạn không có quyền truy cập!", 403

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        datetime_str = request.form.get('datetime')
        vip_price = request.form.get('vip_price', type=float)
        normal_price = request.form.get('normal_price', type=float)
        vip_quantity = request.form.get('vip_quantity', type=int)
        normal_quantity = request.form.get('normal_quantity', type=int)
        address_detail = request.form.get('address_detail')
        province = request.form.get('province')
        category_id = request.form.get('category_id')
        banner = request.files.get('banner')

        event_datetime = datetime.fromisoformat(datetime_str)

        dao.add_event(name, description, event_datetime, vip_price, normal_price,
                      vip_quantity, normal_quantity, address_detail, province,
                      banner, category_id, current_user.id)

        return redirect('/organizer/dashboard')

    return render_template('organizer/create_event.html', categories=dao.load_categories(), provinces=dao.load_provinces())


# Cập nhật sự kiện
@app.route('/organizer/events/<int:event_id>/update', methods=['get', 'post'])
@login_required
def update_event(event_id):
    if current_user.user_role != UserRole.ORGANIZER:
        return "Bạn không có quyền!", 403

    event = dao.get_event_by_id(event_id)
    if not event or event.organizer_id != current_user.id:
        return "Không tìm thấy sự kiện hoặc bạn không có quyền!", 404

    if request.method == 'POST':
        dao.update_event(
            event_id=event_id,
            organizer_id=current_user.id,
            name=request.form.get('name'),
            description=request.form.get('description'),
            datetime=datetime.fromisoformat(request.form.get('datetime')),
            vip_price=request.form.get('vip_price', type=float),
            normal_price=request.form.get('normal_price', type=float),
            vip_quantity=request.form.get('vip_quantity', type=int),
            normal_quantity=request.form.get('normal_quantity', type=int),
            address_detail=request.form.get('address_detail'),
            province=request.form.get('province'),
            banner=request.files.get('banner'),
            category_id=request.form.get('category_id')
        )
        return redirect('/organizer/dashboard')

    return render_template('organizer/update_event.html', event=event, categories=dao.load_categories())


# Xoá sự kiện
@app.route('/organizer/events/<int:event_id>/delete', methods=['post'])
@login_required
def delete_event(event_id):
    if current_user.user_role != UserRole.ORGANIZER:
        return "Bạn không có quyền!", 403

    success = dao.delete_event(event_id, current_user.id)
    if not success:
        return "Không thể xoá sự kiện!", 404

    return redirect('/organizer/dashboard')

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
