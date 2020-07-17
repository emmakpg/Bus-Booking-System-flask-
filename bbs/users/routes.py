from flask import Blueprint,render_template,redirect,url_for,flash,request,abort,jsonify
from bbs.forms import RegistrationForm, LoginForm, AddBusForm,AddSeatsForm,AddRouteForm,AvailabilityForm,UpdateAccountForm,BookingForm
from flask_security import Security, SQLAlchemyUserDatastore, login_required,roles_required, login_user,logout_user,current_user
from flask_security.utils import hash_password, verify_password
from bbs import app,db,mail
from bbs.models import User,Role,Availability,Buses,Booking,Seats,BookingSchema,SeatSchema
from bbs.users.utils import save_picture,generate_ticket_no
from flask_mail import Message



users = Blueprint('users',__name__)

user_datastore = SQLAlchemyUserDatastore(db,User,Role)
security = Security(app,user_datastore)

#Adds admin role to main@main
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


@users.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.trips'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user_datastore.create_user(name =form.name.data,username=form.username.data,
        email=form.email.data,phone=form.phone.data,password=hash_password(form.password.data))
        db.session.commit()
        flash(f'{form.name.data}, Your account has been created. Kindly Login.','success')
        return redirect(url_for('main.home'))
    return render_template('/users/register.html',title='Register',form=form)

@users.route('/Login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and verify_password(form.password.data,user.password):
            login_user(user,remember=form.remember.data)
            if user.has_role('admin'):
               return redirect(url_for('myadmin.dashboard')) 
            else:
               flash(f'{user.username}, Login Successful!','success')  
               next_page = request.args.get('next')
               return redirect(next_page) if next_page else redirect(url_for('main.home')) 
               
        else:
            flash('Unsuccessful. Kindly enter correct username and password','danger')
    return render_template('/users/login.html',title='Login',form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))



@users.route('/account',methods=['GET','POST'])
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
        return redirect(url_for('users.account'))
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    image_file = url_for('static',filename='profile_pics/'+ current_user.image_file)
    return render_template('/users/account.html',title='Account',image_file=image_file, form=form)

@users.route('/#buses')
def user_buses():
    buses = Buses.query.all()
    return render_template('/users/buses.html',buses=buses,title='Buses')

def sendbooking_mail(email,ticket_no,seat):
    message = Message(subject='BBS-Bus Booking Details',sender='BBS',recipients=[email])
    #message.html = f'<p>This is your booking number: {ticket_no}</p><p><strong>Seat:</strong>{seat}</p>'  
    message.html = render_template('/users/mail.html',ticket_no=ticket_no,seat=seat)               
    mail.send(message)

@users.route('/booking-#<int:available_id>',methods =['GET','POST'])
def booking(available_id):
    available = Availability.query.get_or_404(available_id)
    if not current_user.is_authenticated:
        abort(403)
    else:
        form = BookingForm()
        seats = Seats.query.all()
        booked_buses = db.session.query(Booking).filter(Booking.bus_id==available.bus_id).all()
        
        booking_schema = BookingSchema(many=True)
        booked_seats = booking_schema.dump(booked_buses)
        booked_seats = [ ls["seat"] for ls in booked_seats]
        
        seat_schema = SeatSchema(many=True)
        all_seats = seat_schema.dump(seats)
        all_seats = [ ls["id"] for ls in all_seats]
        remaining_seat = [ seat for seat in all_seats if seat not in booked_seats]
       
        form.seat.choices = [(seat.id,seat.name) for seat in \
                            [ db.session.query(Seats).filter(Seats.id==seat_id).first() for seat_id in remaining_seat ]]
      
        if len(form.seat.choices)==0:
                flash('We are Sorry. Bus for this Trip is occupied.','danger')
        ticket_number = generate_ticket_no(available.date)
        
        if form.validate_on_submit():
            booking = Booking(customer_id=current_user.id, ticket_number=ticket_number,seat_id=form.seat.data,bus_id=available.bus.id,route_id=available.route.id,
                      phone=form.phone.data,date=available.date,email=form.email.data,time=available.time)
            db.session.add(booking)
            db.session.commit()
            flash('Booking Completed!','success')
            sendbooking_mail(form.email.data,ticket_number,form.seat.data)
            return redirect(url_for('main.home'))
        elif request.method=='GET':
            form.ticket_number.data = ticket_number
            form.name.data = current_user.name
            form.email.data = current_user.email
            form.phone.data = current_user.phone
            form.bus_route_time.data =  f"{available.bus.name}: {available.route.name}: GHC{available.route.amount} "
            form.date.data = f"{available.time}: {available.date}"
    return render_template('/users/booking.html',title='Booking',form=form)



@users.route('/mybookings-<int:user_id>',)
def mybookings(user_id):
    if not  current_user.is_authenticated:
        abort(403)
    else:
         mybookings = db.session.query(Booking).filter(Booking.customer_id==user_id).order_by(Booking.date_booked.asc())
    
    return render_template('/users/mybookings.html',mybookings=mybookings)

@users.route('/cancel_booking<int:book_id>')
def cancel_booking(book_id):
    if current_user:
        booking = Booking.query.get_or_404(book_id)
        bookname = f"{booking.bus.name}: {booking.route.name}"
        db.session.delete(booking)
        db.session.commit()
        flash(f'Your Booking for {bookname} trip deleted','success')
        return redirect(url_for('users.mybookings', user_id=current_user.id))


