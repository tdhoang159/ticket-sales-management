from app.models import Category, Event, User
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app, db

admin = Admin(app=app, name="OU Ticket Box Management", template_mode='bootstrap4')

class CategoryView(ModelView):
    column_list = ['name', 'events']


class EventView(ModelView):
    column_list = ['id', 'name', 'normal_price', 'vip_price']
    column_searchable_list = ['name']
    column_filters = ['id', 'name', 'normal_price', 'vip_price']
    column_editable_list = ['name']
    can_export = True

admin.add_view(CategoryView(Category, db.session))
admin.add_view(EventView(Event, db.session))
admin.add_view(ModelView(User, db.session))