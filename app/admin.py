from app.models import Category, Event, User, UserRole, Organizer
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from app import app, db, dao
from flask_login import current_user, logout_user
from flask import redirect

class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)
    
class MyAdminIndexView(AdminIndexView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        from flask import request

        time_type = request.args.get('time_type', 'month')  # month | quarter | year
        time_value = request.args.get('time_value')  # ví dụ: 1, 2, 3...
        organizer_id = request.args.get('organizer_id')  # lọc theo Organizer

        stats = dao.revenue_stats_by_event_and_organizer(time=time_type)

        # lọc tiếp trong python (cũng có thể filter ở query dao luôn)
        if time_value:
            stats = [s for s in stats if str(int(s.time)) == time_value]
        if organizer_id:
            stats = [s for s in stats if str(s.organizer_id) == organizer_id]

        organizers = Organizer.query.all()

        return self.render(
            'admin/statistic.html',
            stats=stats,
            time_type=time_type,
            time_value=time_value,
            organizer_id=organizer_id,
            organizers=organizers
        )
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        return "Bạn không có quyền truy cập trang này"

class CategoryView(AdminView):
    column_list = ['name', 'events']


class EventView(AdminView):
    column_list = ['id', 'name', 'normal_price', 'vip_price']
    column_searchable_list = ['name']
    column_filters = ['id', 'name', 'normal_price', 'vip_price']
    column_editable_list = ['name']
    can_export = True

class HomeView(BaseView):
    @expose('/')
    def index(self):
        return redirect('/')
    
# class StatisticView(BaseView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/statistic.html',
#                            revenue_stats_by_events = dao.revenue_stats_by_events(),
#                            revenue_stats_by_time = dao.revenue_stats_by_time())
#
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)

admin = Admin(app=app, name="OU Ticket Box Management", template_mode='bootstrap4', index_view=MyAdminIndexView())
admin.add_view(CategoryView(Category, db.session, name="Danh mục sự kiện"))
admin.add_view(EventView(Event, db.session, name="Sự kiện"))
admin.add_view(AdminView(User, db.session, name="Người dùng"))
admin.add_view(AdminView(Organizer, db.session, name="Nhà tổ chức sự kiện"))
# admin.add_view(StatisticView(name='Thống kê'))
admin.add_view(HomeView(name='Trở về Trang Chủ'))
