from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'f53ea08e09456124882957a823012505'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bbs.db'
app.config['SECURITY_PASSWORD_SALT'] = '8a81b43d01df901937f1c81cbf80fbbb'
db = SQLAlchemy(app)
#login_manager = LoginManager(app)

from bbs import routes