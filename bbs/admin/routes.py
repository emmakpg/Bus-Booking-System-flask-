from flask import Blueprint,render_template,redirect,url_for,flash,request,abort,send_file
from bbs.forms import RegistrationForm, LoginForm, AddBusForm,AddSeatsForm,AddRouteForm,AvailabilityForm,UpdateAccountForm,BookingForm,ReportForm
from flask_security import Security, SQLAlchemyUserDatastore, login_required,roles_required, login_user,logout_user,current_user
from flask_security.utils import hash_password, verify_password
from bbs import app,db,super_admin
from bbs.models import User,Role,Availability,Buses,Booking,Seats,Route,Controller,BookingSchema
from bbs.admin.utils import savebus_picture
import os
import csv
from datetime import datetime
from isoweek import Week

myadmin = Blueprint('myadmin',__name__)


super_admin.add_view(Controller(User,db.session))
super_admin.add_view(Controller(Booking,db.session))

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
dir_of_interest = os.path.join(FILE_DIR,'reports')



@myadmin.route('/dashboard')
@roles_required('admin')
def dashboard():
    bookings = db.session.query(Booking).count()
    buses = db.session.query(Buses).count()
    trips = db.session.query(Availability).filter(Availability.status=='available').count()

  
    #GRAPH WORK
    date_booked = db.session.query(Booking).filter(Booking.date_booked).order_by(Booking.date_booked.asc()).all()
    booking_schema = BookingSchema(many=True)
    date_booked = booking_schema.dump(date_booked)
    date_booked = [ ls["date_booked"][:10] for ls in date_booked ]
    date_vs_booking = { i:date_booked.count(i) for i in date_booked}
    number_of_bookings = list(date_vs_booking.values())
    date_labels = list(date_vs_booking.keys())

    #total revenue from bookings
    bookings_r = Booking.query.all()
    amount_r = [ i.route.amount for i in bookings_r]
    total_revenue = sum(amount_r)
    return render_template('/admin/admin.html',total_revenue=total_revenue,bookings_count=bookings,buses_count=buses,trips_count=trips,date_labels=date_labels,number_of_bookings=number_of_bookings)


@myadmin.route('/buses',methods=['GET','POST'])
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
        return redirect(url_for('myadmin.buses'))
    buses = Buses.query.all()
    return render_template('/admin/buses.html',buses=buses,form=form)

@myadmin.route('/routes',methods=['GET','POST'])
@roles_required('admin')
def routes():
    routes = Route.query.all()
    form = AddRouteForm()
    if form.validate_on_submit():
        route = Route(name=form.name.data,time=form.time.data,amount=form.amount.data)
        db.session.add(route)
        db.session.commit()
        flash(f'Route {form.name.data} has been added','success')
        return redirect(url_for('myadmin.routes'))
    return render_template('/admin/routes.html',routes=routes,form=form)

@myadmin.route('/seats',methods=['GET','POST'])
@roles_required('admin')
def seats():
    seats = Seats.query.all()
    form = AddSeatsForm()
    if form.validate_on_submit():
        seat = Seats(name=form.name.data)
        db.session.add(seat)
        db.session.commit()
        flash(f'Seat {form.name.data} has been added','success')
        return redirect(url_for('myadmin.seats'))
    return render_template('/admin/seats.html',seats=seats,form=form)


@myadmin.route('/bookings')
@roles_required('admin')
def bookings():
    bookings = Booking.query.all()

    #Generate CSV for bookings
    #abs_path = os.path.abspath("../"+"./BBS/bbs/reports")

    with open( dir_of_interest +'./bookings.csv','w',newline='') as f:
        out = csv.writer(f)
        out.writerow(['Ticket Number','Name','Phone','Bus','Seat','Departure Date','Time','Amount','Date Booked'])
        for booking in bookings:
            out.writerow([booking.ticket_number,booking.customer.name,booking.phone,booking.bus.name,booking.seat.name,
                    booking.date.strftime('%Y-%m-%d'),booking.route.time,booking.route.amount,booking.date_booked ])



    return render_template('/admin/bookings.html',bookings=bookings)


@myadmin.route('/availability',methods=['GET','POST'])
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
        return redirect(url_for('myadmin.availability'))
    return render_template('/admin/availability.html',availability=availability,form=form)


@myadmin.route('/#delete-<int:id>')
@roles_required('admin')
def delete(id):
    referrer = request.referrer     #gets the previous route
    
    if 'routes' in referrer:
        route = Route.query.get_or_404(id)
        db.session.delete(route)
        db.session.commit()
        return redirect(url_for('myadmin.routes'))
    elif 'booking' in referrer:
        booking = Booking.query.get_or_404(id)
        db.session.delete(booking)
        db.session.commit()
        return redirect(url_for('myadmin.bookings'))
    elif 'seats' in referrer:
        seat = Seats.query.get_or_404(id)
        db.session.delete(seat)
        db.session.commit()
        return redirect(url_for('myadmin.seats'))
    elif 'bus' in referrer:
        bus = Buses.query.get_or_404(id)
        db.session.delete(bus)
        db.session.commit()
        return redirect(url_for('myadmin.buses'))
    elif 'availability' in referrer:
        available = Availability.query.get_or_404(id)
        db.session.delete(available)
        db.session.commit()
        return redirect(url_for('myadmin.availability'))


@myadmin.route('/edit_availability-<int:id>',methods=['GET','POST'])
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
            return redirect(url_for('myadmin.availability'))
        elif request.method=='GET':
            form.bus.data = available.bus.name
            form.route.data = available.route.name
            form.date.data = available.date
            form.time.data = available.time
            form.status.data = available.status
        return render_template('/admin/edit_availability.html',form=form)
      
@myadmin.route('/edit_route-<int:id>',methods=['GET','POST'])
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
            return redirect(url_for('myadmin.routes'))
        elif request.method=='GET':
            form.name.data = route.name
            form.time.data = route.time
            form.amount.data = route.amount
        return render_template('/admin/edit_route.html',form=form)


@myadmin.route('/edit_bus-<int:id>',methods=['GET','POST'])
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
            return redirect(url_for('myadmin.buses'))
        elif request.method=='GET':
            form.name.data = bus.name
            form.number_plate.data =  bus.number
            form.description.data = bus.description
        return render_template('/admin/edit_bus.html',form=form)


@myadmin.route('/export_csv')
@roles_required('admin')
def export_csv():
    path = dir_of_interest +'\\bookings.csv'
    return send_file(path,as_attachment=True)

@myadmin.route('/export_dailybookings_csv')
@roles_required('admin')
def export_dailybookings_csv():
    path = dir_of_interest +'\\daily_bookings.csv'
    return send_file(path,as_attachment=True)

@myadmin.route('/export_weeklybookings_csv')
@roles_required('admin')
def export_weeklybookings_csv():
    path = dir_of_interest +'\\weekly_bookings.csv'
    return send_file(path,as_attachment=True)

@myadmin.route('/export_monthlybookings_csv')
@roles_required('admin')
def export_monthlybookings_csv():
    path = dir_of_interest +'\\monthly_bookings.csv'
    return send_file(path,as_attachment=True)


@myadmin.route('/reports',methods=['GET','POST'])
@roles_required('admin')
def reports():
    
    form = ReportForm()
    form1 = ReportForm()
    form2 =ReportForm()
    #GRAPH WORK
    date_booked = db.session.query(Booking).filter(Booking.date_booked).order_by(Booking.date_booked.asc()).all()
    booking_schema = BookingSchema(many=True)
    date_booked = booking_schema.dump(date_booked)
    date_booked = [ ls["date_booked"][:10] for ls in date_booked ]
    date_vs_booking = { i:date_booked.count(i) for i in date_booked}
    number_of_bookings = list(date_vs_booking.values())
    date_labels = list(date_vs_booking.keys())

    last_update_time = datetime.utcnow().strftime('%H:%M')
    #abs_path = os.path.abspath("../"+"./BBS/bbs/reports")   #path to save reports
    
    if request.method == 'POST' and 'date' in request.form:
        #flash()
        #Generate CSV for Daily bookings
        booked_today = db.session.query(Booking).filter(Booking.date_booked==form.date.data).order_by(Booking.date_booked.asc()).all()
        
        if len(booked_today) != 0:
            with open( dir_of_interest +'./daily_bookings.csv','w',newline='') as f:
             out = csv.writer(f)
             out.writerow(['Ticket Number','Name','Phone','Bus','Seat','Departure Date','Time','Amount','Date Booked'])
             for booking in booked_today:
                out.writerow([booking.ticket_number,booking.customer.name,booking.phone,booking.bus.name,booking.seat.name,
                    booking.date.strftime('%Y-%m-%d'),booking.route.time,booking.route.amount,booking.date_booked ])
            
            return redirect(url_for('myadmin.export_dailybookings_csv'))
            flash('Daily Report Exported','success') 
        else:
            flash('No Reports for day selected','info') 
    
    bookings = Booking.query.all()
    query = [ booking.date_booked for booking in bookings]

    #Generate Monthly Report
    if request.method == 'POST' and 'month' in request.form:
    
        month =  form1.month.data
        month_book_dates = [l for l in query if month in l]
    
        with open( dir_of_interest +'./monthly_bookings.csv','w',newline='') as f:
            out = csv.writer(f)
            out.writerow(['Ticket Number','Name','Phone','Bus','Seat','Departure Date','Time','Amount','Date Booked'])
            for book_date in month_book_dates:
                booking = db.session.query(Booking).filter(Booking.date_booked==book_date).order_by(Booking.date_booked.asc()).all()
                for booking in booking:
                    out.writerow([booking.ticket_number,booking.customer.name,booking.phone,booking.bus.name,booking.seat.name,
                    booking.date.strftime('%Y-%m-%d'),booking.route.time,booking.route.amount,booking.date_booked ])
        #flash('Monthly Report Exported','success')
        return redirect(url_for('myadmin.export_monthlybookings_csv'))

    #Generate Weekly Report
    if request.method == 'POST' and 'week' in request.form:
        current_wk = form2.week.data
        if current_wk <= 53:
            w = Week(2020,current_wk)
            days_wk = w.days()
            wk_n=[]
            for day in days_wk:
                wk_n.append(day.strftime('%Y-%m-%d'))
            wkdays_in_bookings = [day for day in wk_n if day in query]
            if len(wkdays_in_bookings)==0:
                flash(f'No bookings for Week {current_wk}','info')
            else:
                with open( dir_of_interest +'./weekly_bookings.csv','w',newline='') as f:
                    out = csv.writer(f)
                    out.writerow(['Ticket Number','Name','Phone','Bus','Seat','Departure Date','Time','Amount','Date Booked'])
                    for book_date in wkdays_in_bookings:
                        booking = db.session.query(Booking).filter(Booking.date_booked==book_date).order_by(Booking.date_booked.asc()).all()
                        for booking in booking:
                            out.writerow([booking.ticket_number,booking.customer.name,booking.phone,booking.bus.name,booking.seat.name,
                                booking.date.strftime('%Y-%m-%d'),booking.route.time,booking.route.amount,booking.date_booked ])
        
                return redirect(url_for('myadmin.export_weeklybookings_csv'))

        else:
            flash('Week number out of range','warning')
    


    return render_template('admin/reports.html',number_of_bookings=number_of_bookings,date_labels=date_labels,
                            last_update_time=last_update_time,form=form,form1=form1,form2=form2)

    