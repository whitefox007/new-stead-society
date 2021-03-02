import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_mail import Mail, Message
from flask_dropzone import Dropzone

#############################################################################
############ CONFIGURATIONS (CAN BE SEPARATE CONFIG.PY FILE) ###############
###########################################################################

# Remember you need to set your environment variables at the command line
# when you deploy this to a real website.
# export SECRET_KEY=mysecret
# set SECRET_KEY=mysecret

app = Flask(__name__)

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.sendgrid.net',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'apikey',
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER'),
    FLASKY_MAIL_SUBJECT_PREFIX = '[STEAD]'
))

mail = Mail(app)
pagedown = PageDown(app)
dropzone = Dropzone(app)

#################################
### DATABASE SETUPS ############
###############################
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'my secret key'
ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:iloveinnovation@localhost:8080/myDB'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://pzocomohbwwtnx:8977eba434c724fcead679129d73240a4c98ba465b238273e6e6e2447ee5d809@ec2-52-86-73-86.compute-1.amazonaws.com:5432/dfq6d89m6sdhul'



app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN') or 'movie.alvina@gmail.com'

# Dropzone settings
app.config['DROPZONE_UPLOAD_MULTIPLE'] = True
app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'image/*'
app.config['DROPZONE_REDIRECT_VIEW'] = 'results'

db = SQLAlchemy(app)
Migrate(app,db)


###########################
#### LOGIN CONFIGS #######
#########################

login_manager = LoginManager()

# We can now pass in our app to the login manager
login_manager.init_app(app)

# Tell users what view to go to when they need to login.
login_manager.login_view = "users.login"


###########################
#### BLUEPRINT CONFIGS #######
#########################

# Import these at the top if you want
# We've imported them here for easy reference
from stead.core.views import core
from stead.users.views import users, Permission
from stead.news_posts.views import news_posts
from stead.error_pages.handlers import error_pages
from stead.forum.views import forum
from stead.projects.views import projects

# Register the apps
app.register_blueprint(users)
app.register_blueprint(news_posts)
app.register_blueprint(core)
app.register_blueprint(error_pages)
app.register_blueprint(forum)
app.register_blueprint(projects)


