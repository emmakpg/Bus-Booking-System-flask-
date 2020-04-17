from flask import Flask,render_template,url_for,redirect, flash,request,current_app,abort
from bbs.forms import RegistrationForm, LoginForm, AddBusForm,AddSeatsForm,AddRouteForm,AvailabilityForm,UpdateAccountForm,BookingForm
from flask_security import Security, SQLAlchemyUserDatastore, login_required,roles_required, login_user,logout_user,current_user
from flask_security.utils import hash_password, verify_password
from bbs import db,app
from bbs.models import User,Role,Buses,Seats,Route,Availability,Booking
import os
import secrets
from PIL import Image

user_datastore = SQLAlchemyUserDatastore(db,User,Role)
security = Security(app,user_datastore)



#Adds admin role to app
@app.before_first_request
def create_user():
    # db.drop_all()
    # db.create_all()
    admin = Role.query.filter_by(name='admin').first()
    # bus = Buses(name='Bus Name',number='B34-1234-235',description='Routed Bus',image_file='default_bus.jpg') 
    # db.session.add(bus)   
    # db.session.commit()
    if admin:
        return None
    else:
     user_datastore.create_role( name ='admin',description='Administrator')
     user_datastore.create_user(name ='Admin',username='admin',
     email='admin@demo.com',phone='0555555551',password=hash_password('admin'),roles=['admin'])
     db.session.commit()

@app.route('/')
@app.route('/home')
def home():
    if current_user.has_role('admin'):
        return redirect(url_for('admin')) 
    page = request.args.get('page',1,type=int)
    availability = db.session.query(Availability).filter(Availability.status=='available').\
                    order_by(Availability.date.asc()).paginate(page=page, per_page=4)
        
    return render_template('index.html',availability=availability)

@app.route('/trips')
def trips():
     page = request.args.get('page',1,type=int)
     availability = db.session.query(Availability).filter(Availability.status=='available').\
                    order_by(Availability.date.asc()).paginate(page=page, per_page=4)
     return render_template('index.html',availability=availability)

@app.route('/about')
def about():
    return render_template('about.html',title='About')

@app.route('/booking-#<int:available_id>',methods =['GET','POST'])
def booking(available_id):
    available = Availability.query.get_or_404(available_id)
    if not current_user.is_authenticated:
        abort(403)
    else:
        form = BookingForm()
        form.seat.choices = [(seat.id,seat.name) for seat in Seats.query.order_by('name')]
        if form.validate_on_submit():
            booking = Booking(customer_id=current_user.id,seat_id=form.seat.data,bus_id=available.bus.id,route_id=available.route.id,
                      phone=form.phone.data,date=available.date,email=form.email.data,time=available.time)
            db.session.add(booking)
            db.session.commit()
            flash('Booking Completed!','success')
            return redirect(url_for('home'))
        elif request.method=='GET':
            form.name.data = current_user.name
            form.email.data = current_user.email
            form.phone.data = current_user.phone
            form.bus_route_time.data =  f"{available.bus.name}: {available.route.name}: GHC{available.route.amount} "
            form.date.data = f"{available.time}: {available.date}"
    return render_template('/users/booking.html',title='Booking',form=form)




@app.route('/admin')
@roles_required('admin')
def admin():
    bookings = db.session.query(Booking).count()
    buses = db.session.query(Buses).count()
    trips = db.session.query(Availability).filter(Availability.status=='available').count()
  
    return render_template('/admin/admin.html',bookings_count=bookings,buses_count=buses,trips_count=trips)

@app.route('/bookings',)
def bookings():
    bookings = Booking.query.all()
    return render_template('/admin/bookings.html',bookings=bookings)

@app.route('/mybookings-<int:user_id>',)
def mybookings(user_id):
    if not  current_user.is_authenticated:
        abort(403)
    else:
         mybookings = db.session.query(Booking).filter(Booking.customer_id==user_id).order_by(Booking.date_booked.asc())
    
    return render_template('/users/mybookings.html',mybookings=mybookings)

@app.route('/cancel_booking<int:book_id>')
def cancel_booking(book_id):
    if current_user:
        booking = Booking.query.get_or_404(book_id)
        bookname = f"{booking.bus.name}: {booking.route.name}"
        db.session.delete(booking)
        db.session.commit()
        flash(f'Your Booking for {bookname} deleted','success')
        return redirect(url_for('mybookings', user_id=current_user.id))


def savebus_picture(form_picture,form_busname):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = form_busname + f_ext
    picture_path = os.path.join(current_app.root_path,'static/img',picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/buses',methods=['GET','POST'])
@roles_required('admin')
def buses():  

    form = AddBusForm()
   
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = savebus_picture(form.picture.data,form.name.data)   
        bus = Buses(name=form.name.data,number=form.number_plate.data,description=form.description.data,image_file=picture_file)
        db.session.add(bus)
        db.session.commit()
        flash(f'Bus {form.name.data} has been added','success')
        return redirect(url_for('buses'))
    buses = Buses.query.all()
    return render_template('/admin/buses.html',buses=buses,form=form)

@app.route('/routes',methods=['GET','POST'])
@roles_required('admin')
def routes():
    routes = Route.query.all()
    form = AddRouteForm()
    if form.validate_on_submit():
        route = Route(name=form.name.data,time=form.time.data,amount=form.amount.data)
        db.session.add(route)
        db.session.commit()
        flash(f'Route {form.name.data} has been added','success')
        return redirect(url_for('routes'))
    return render_template('/admin/routes.html',routes=routes,form=form)

@app.route('/seats',methods=['GET','POST'])
@roles_required('admin')
def seats():
    seats = Seats.query.all()
    form = AddSeatsForm()
    if form.validate_on_submit():
        seat = Seats(name=form.name.data)
        db.session.add(seat)
        db.session.commit()
        flash(f'Seat {form.name.data} has been added','success')
        return redirect(url_for('seats'))
    return render_template('/admin/seats.html',seats=seats,form=form)


@app.route('/availability',methods=['GET','POST'])
@roles_required('admin')
def availability():
    availability = Availability.query.all()

    form = AvailabilityForm()
    form.bus.choices = [(bus.id,bus.name) for bus in Buses.query.order_by('name')]
    form.route.choices = [(route.id,route.name) for route in Route.query.order_by('name')]
    
    if form.validate_on_submit():
        route = Route.query.filter_by(id=form.route.data).first()
       
        avail = Availability(route_id=form.route.data,bus_id=form.bus.data,date=form.date.data,
                            time=form.time.data,amount=route.amount,status=form.status.data)
        db.session.add(avail)
        db.session.commit()
        flash(f'Availability for {route.name} has been added','success')
        return redirect(url_for('availability'))
    return render_template('/admin/availability.html',availability=availability,form=form)



@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('trips'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user_datastore.create_user(name =form.name.data,username=form.username.data,
        email=form.email.data,phone=form.phone.data,password=hash_password(form.password.data))
        db.session.commit()
        flash(f'{form.name.data}, Your account has been created. Kindly Login.','success')
        return redirect(url_for('home'))
    return render_template('/users/register.html',title='Register',form=form)

@app.route('/Login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and verify_password(form.password.data,user.password):
            login_user(user,remember=form.remember.data)
            if user.has_role('admin'):
               return redirect(url_for('admin')) 
            else:
               flash(f'{user.username}, Login Successful!','success')  
               next_page = request.args.get('next')
               return redirect(next_page) if next_page else redirect(url_for('home')) 
        else:
            flash('Unsuccessful. Kindly enter correct email and password','danger')
    return render_template('/users/login.html',title='Login',form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path,'static/profile_pics',picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account',methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Account has been updated','success')
        return redirect(url_for('account'))
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    image_file = url_for('static',filename='profile_pics/'+ current_user.image_file)
    return render_template('/users/account.html',title='Account',image_file=image_file, form=form)

@app.route('/#buses')
def user_buses():
    buses = Buses.query.all()
    return render_template('/users/buses.html',buses=buses,title='Buses')


@app.route('/#delete-<int:id>')
@roles_required('admin')
def delete(id):
    referrer = request.referrer     #gets the previous route
    
    if 'routes' in referrer:
        route = Route.query.get_or_404(id)
        db.session.delete(route)
        db.session.commit()
        return redirect(url_for('routes'))
    elif 'booking' in referrer:
        booking = Booking.query.get_or_404(id)
        db.session.delete(booking)
        db.session.commit()
        return redirect(url_for('bookings'))
    elif 'seats' in referrer:
        seat = Seats.query.get_or_404(id)
        db.session.delete(seat)
        db.session.commit()
        return redirect(url_for('seats'))
    elif 'bus' in referrer:
        bus = Buses.query.get_or_404(id)
        db.session.delete(bus)
        db.session.commit()
        return redirect(url_for('buses'))
    elif 'availability' in referrer:
        available = Availability.query.get_or_404(id)
        db.session.delete(available)
        db.session.commit()
        return redirect(url_for('availability'))


@app.route('/edit_availability-<int:id>',methods=['GET','POST'])
@roles_required('admin')
def edit_availability(id):
        available = Availability.query.get_or_404(id)
        form = AvailabilityForm()
        form.submit.label.text = 'Update'
        form.bus.choices = [(bus.id,bus.name) for bus in Buses.query.order_by('name')]
        form.route.choices = [(route.id,route.name) for route in Route.query.order_by('name')]
        if form.validate_on_submit():
            available.bus_id = form.bus.data
            available.route_id = form.route.data
            available.date = form.date.data
            available.time = form.time.data
            available.status = form.status.data
            db.session.commit()
            flash('Update Done!','success')
            return redirect(url_for('availability'))
        elif request.method=='GET':
            form.bus.data = available.bus.name
            form.route.data = available.route.name
            form.date.data = available.date
            form.time.data = available.time
            form.status.data = available.status
        return render_template('/admin/edit_availability.html',form=form)
      
@app.route('/edit_route-<int:id>',methods=['GET','POST'])
@roles_required('admin')
def edit_route(id):
        route = Route.query.get_or_404(id)
        form = AddRouteForm()
        form.submit.label.text = 'Update'
        if form.validate_on_submit():
            route.name = form.name.data
            route.time = form.time.data
            route.amount = form.amount.data
            db.session.commit()
            flash('Update Done!','success')
            return redirect(url_for('routes'))
        elif request.method=='GET':
            form.name.data = route.name
            form.time.data = route.time
            form.amount.data = route.amount
        return render_template('/admin/edit_route.html',form=form)


@app.route('/edit_bus-<int:id>',methods=['GET','POST'])
@roles_required('admin')
def edit_bus(id):
        bus = Buses.query.get_or_404(id)
        form = AddBusForm()
        form.submit.label.text = 'Update'
        if form.validate_on_submit():
            bus.name = form.name.data
            bus.number = form.number_plate.data
            bus.description = form.description.data
            bus.image_file = savebus_picture(form.picture.data)
            db.session.commit()
            flash('Update Done!','success')
            return redirect(url_for('buses'))
        elif request.method=='GET':
            form.name.data = bus.name
            form.number_plate.data =  bus.number
            form.description.data = bus.description
        return render_template('/admin/edit_bus.html',form=form)