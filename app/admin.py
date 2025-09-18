from app.models import Category, Event, User, UserRole
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from app import app, db, dao
from flask_login import current_user, logout_user
from flask import redirect

admin = Admin(app=app, name="OU Ticket Box Management", template_mode='bootstrap4')

class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)
    

class CategoryView(AdminView):
    column_list = ['name', 'events']


class EventView(AdminView):
    column_list = ['id', 'name', 'normal_price', 'vip_price']
    column_searchable_list = ['name']
    column_filters = ['id', 'name', 'normal_price', 'vip_price']
    column_editable_list = ['name']
    can_export = True

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')
    
    def is_accessible(self):
        return current_user.is_authenticated
    
class StatisticView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/statistic.html',
                           revenue_stats_by_events = dao.revenue_stats_by_events(),
                           revenue_stats_by_time = dao.revenue_stats_by_time())
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)
admin.add_view(CategoryView(Category, db.session))
admin.add_view(EventView(Event, db.session))
admin.add_view(AdminView(User, db.session))
admin.add_view(LogoutView(name='Đăng xuất'))
admin.add_view(StatisticView(name='Thống kê'))