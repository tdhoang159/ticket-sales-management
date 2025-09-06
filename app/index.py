from flask import render_template, request, redirect
from app import app, dao, login
import math
from flask_login import login_user, logout_user

@app.route("/")
def index(): 
    cates = dao.load_categories()
    cate_id = request.args.get("category_id")
    kw = request.args.get("kw")
    current_page = request.args.get("page", 1)
    events = dao.load_events(cate_id=cate_id, kw=kw, page=int(current_page))
    page_size = app.config.get("PAGE_SIZE", 8)
    total = dao.count_events(cate_id=cate_id, kw=kw)

    return render_template("index.html", categories = cates, events = events, 
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

if __name__ == '__main__':
    from app import admin
    app.run(debug=True)
