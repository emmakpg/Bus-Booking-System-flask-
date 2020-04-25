from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_login import LoginManager
from flask_admin import Admin
from flask_marshmallow import  Marshmallow

app = Flask(__name__)

app.config['SECRET_KEY'] = 'f53ea08e09456124882957a823012505'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bbs.db'
app.config['SECURITY_PASSWORD_SALT'] = '8a81b43d01df901937f1c81cbf80fbbb'
db = SQLAlchemy(app)
ma = Marshmallow(app)
super_admin = Admin(app,name='Control Panel')
#login_manager = LoginManager(app)

from bbs.main.routes import main
from bbs.users.routes import users
from bbs.admin.routes import myadmin
from bbs.errors.handler import errors

app.register_blueprint(users)
app.register_blueprint(myadmin)
app.register_blueprint(main)
app.register_blueprint(errors)