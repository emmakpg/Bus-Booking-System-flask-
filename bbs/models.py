from flask import abort
from datetime import datetime
from bbs import db,ma
from flask_security import UserMixin,RoleMixin
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
#from flask_marshmallow import  Marshmallow



# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

class Controller(ModelView):
    def is_accessible(self):
        if current_user.has_role('admin'):
            return current_user.is_authenticated
        else:
            return abort(403)
    def not_authenticated(self): 
        abort(403)


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer,db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer,db.ForeignKey('role.id'))
)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.Integer(), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,default='default.jpg')
    password = db.Column(db.String(60),nullable=False)
    active = db.Column(db.Boolean)
    bookings = db.relationship('Booking', backref='customer')
    roles = db.relationship('Role',secondary='roles_users', backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f"User('{self.name}','{self.username}','{self.email}','{self.phone}','{self.image_file}')"

class Role(db.Model,RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(255))

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'),nullable=False)    
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'),nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(60), nullable=False)
    amount = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.String(60), nullable=False)
    #buses = db.relationship('Buses', backref='availability')
    
   
    def __repr__(self):
        return f"Availability('{self.bus_id}','{self.route_id}','{self.date}','{self.time}','{self.amount}','{self.status}')"



class Buses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    number = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    image_file = db.Column(db.String(60), nullable=False,default='default_bus.jpg')
    bookings = db.relationship('Booking', backref='bus')
    availability = db.relationship('Availability', backref='bus')
   
    
    def __repr__(self):
        return f"Bus('{self.name}','{self.number}','{self.description}','{self.image_file}')"

#Buses.availability = db.relationship(Availability,primaryjoin=Availability.bus_id==Buses.id)
  

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    time = db.Column(db.String(60), nullable=False)
    amount = db.Column(db.Integer(), nullable=False)
    availability = db.relationship('Availability', backref='route')
    booking = db.relationship('Booking', backref='route')

    def __repr__(self):
        return f"Route('{self.name}','{self.time}','{self.amount}')"

class Seats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(5), unique=True, nullable=False)
    bookings = db.relationship('Booking', backref='seat')

    def __repr__(self):
        return f"('{self.name}')"

now = datetime.utcnow()

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(60), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'),nullable=False)    
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'),nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'),nullable=False)
    phone = db.Column(db.Integer(), nullable=False)
    date_booked = db.Column(db.String(120), nullable=False,default=now.strftime('%Y-%m-%d'))
    email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.String(60), nullable=False)
  
    def __repr__(self):
        return f"('{self.customer_id}','{self.phone}','{self.email}','{self.seat_id}',\
                '{self.route_id}','{self.date_booked}','{self.date}','{self.time}')"

class BookingSchema(ma.ModelSchema):
     class Meta:
        model = Booking

class SeatSchema(ma.ModelSchema):
     class Meta:
        model = Seats
       



    