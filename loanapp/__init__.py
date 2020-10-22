from os import environ, path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = path.abspath(path.dirname(__file__))

app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(basedir, 'data.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SECRET_KEY = 'dev'
)

db = SQLAlchemy(app)

from loanapp.users.views import users_blp
from loanapp.loans.views import loans_blp

app.register_blueprint(users_blp)
app.register_blueprint(loans_blp)
