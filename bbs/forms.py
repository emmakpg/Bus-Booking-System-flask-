from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,IntegerField, BooleanField,TextAreaField,SelectField,TextField
from flask_wtf.file import FileField, FileAllowed
from wtforms_components import read_only
from flask_security import current_user
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired,Length,Email, EqualTo,ValidationError
from bbs.models import User

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(),Length(min=3,max=40)])
    username = StringField('Username', validators=[DataRequired(),Length(min=4,max=20)])
    email = StringField('Email', validators=[DataRequired(),Email()])
    phone = IntegerField('Phone', validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=5,max=15)])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose another one.')
    
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('email already exists. Please choose another one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=4,max=20)])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AddBusForm(FlaskForm):
    name = StringField('Bus Name', validators=[DataRequired(),Length(min=3,max=40)])
    number_plate = StringField('Number Plate', validators=[DataRequired()])
    description = TextAreaField('Short Description',validators=[DataRequired()])
    picture = FileField('Add Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Add Bus')

class AddSeatsForm(FlaskForm):
    name = StringField('Seat Name', validators=[DataRequired()])
    submit = SubmitField('Add Seat')

class AddRouteForm(FlaskForm):
    name = StringField('Route Name', validators=[DataRequired(),Length(min=3,max=40)])
    time = SelectField('Time',choices=[('Day','Day'),('Night','Night')])
    amount = IntegerField('Amount',validators=[DataRequired()])
    submit = SubmitField('Add Route')

class AvailabilityForm(FlaskForm):
    bus = SelectField('Bus',coerce=int)
    route = SelectField('Route',coerce=int) 
    date = DateField('Date(dd-mm-yyyy)',format='%Y-%m-%d')
    time = SelectField('Time',choices=[('Day','Day'),('Night','Night')])
    status = SelectField('Status',choices=[('available','Available'),('unavailable','Not Available')])
    submit = SubmitField('Add')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[Length(min=2,max=20)])
    email = StringField('Email',validators=[Email()])
    phone = IntegerField('Phone')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists. Please choose another one.')
    
    def validate_email(self,email):
         if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                 raise ValidationError('email already exists. Please choose another one.')

    
class BookingForm(FlaskForm):
    ticket_number = TextField('Ticket No.')
    name = TextField('Name')
    email = TextField('Email')
    phone = TextField('Phone')
    bus_route_time = TextField('Bus')
    seat = SelectField('Select Seat',coerce=int)
    date = TextField('Departure Date & Time')
    submit = SubmitField('Book')

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        read_only(self.ticket_number)
        read_only(self.name)
        read_only(self.date)
        read_only(self.bus_route_time)

class ReportForm(FlaskForm):
    date = DateField('Daily Report',format='%Y-%m-%d',validators=[DataRequired()])
    month = SelectField('Monthly Report',choices=[('-01','January'),('-02','February'),('-03','March'),
                                        ('-04','April'),('-05','May'),('-06','June'),('-07','July'),('-08','August'),
                                        ('-09','September'),('-10','October'),('-11','November'),('-12','December')])
    submit = SubmitField('Query')
    week = IntegerField('Weekly Report',validators=[DataRequired()],render_kw={"placeholder":"Insert Week Number"})