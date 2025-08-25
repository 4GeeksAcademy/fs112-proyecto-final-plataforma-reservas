import os
from flask_admin import Admin
from .models import db, User, Space, Booking, Payment
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='WEPLACEIT Admin', template_mode='bootstrap3')

    class UserView(ModelView):
        column_list  = ('id', 'is_active', 'email', 'username', 'first_name', 'last_name', 'password', 'created_at')
        form_columns = (      'is_active', 'email', 'username', 'first_name', 'last_name', 'password'              )


    class SpaceView(ModelView):
        column_list  = ('id', 'owner_id', 'title', 'address', 'description', 'price_per_day', 'capacity', 'created_at', 'updated_at')
        form_columns = (      'owner_id', 'title', 'address', 'description', 'price_per_day', 'capacity'                            )

    class BookingView(ModelView):
        column_list  = ('id', 'guest_id', 'space_id', 'check_in', 'check_out', 'total_days', 'status', 'total_price', 'created_at')
        form_columns = (      'guest_id', 'space_id', 'check_in', 'check_out', 'total_days', 'status', 'total_price',             )

    class PaymentView(ModelView):
        column_list  = ('id', 'booking_id', 'amount', 'currency', 'payment_method', 'paid_at')
        form_columns = (      'booking_id', 'amount', 'currency', 'payment_method',          )


    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view( UserView    ( User,    db.session))
    admin.add_view( SpaceView   ( Space,   db.session))
    admin.add_view( BookingView ( Booking, db.session))
    admin.add_view( PaymentView ( Payment, db.session))


    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))
