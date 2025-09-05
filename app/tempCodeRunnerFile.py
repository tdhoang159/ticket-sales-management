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
    total = dao.count_events()

    return render_template("index.html", categories = cates, events = events, 
                           pages = math.ceil(total/ page_size), current_page=int(current_page))


@app.route("/login", methods=['get', 'post'])
def login_process(): 
    if(request.method.__eq__('POST')):
        username = request.form.get('username')
        password = request.form.get('password')
        auth_user = dao.auth_user(username=username, password=password)

        if(auth_user):
            login_user(auth_user)
            return redirect('/')

    return render_template("layout/login.html")

@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)

@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
