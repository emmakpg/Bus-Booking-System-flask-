from flask import Blueprint,redirect,url_for,request,render_template
from flask_security import Security, SQLAlchemyUserDatastore, login_required,roles_required, login_user,logout_user,current_user
from flask_security.utils import hash_password, verify_password
from bbs.models import Role,Availability,User
from bbs import app,db

main = Blueprint('main',__name__)

@main.route('/')
def landing():
    return render_template('home.html')


@main.route('/home')
def home():
    if current_user.has_role('admin'):
        return redirect(url_for('myadmin.dashboard')) 
    page = request.args.get('page',1,type=int)
    availability = db.session.query(Availability).filter(Availability.status=='available').\
                    order_by(Availability.date.asc()).paginate(page=page, per_page=4)
        
    return render_template('index.html',availability=availability)

@main.route('/trips')
def trips():
     page = request.args.get('page',1,type=int)
     availability = db.session.query(Availability).filter(Availability.status=='available').\
                    order_by(Availability.date.asc()).paginate(page=page, per_page=4)
     return render_template('index.html',availability=availability)

@main.route('/about')
def about():
    return render_template('about.html',title='About')