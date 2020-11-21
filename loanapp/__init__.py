from os import environ, path, makedirs
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from loanapp import commands

app = Flask(__name__, instance_relative_config=True)

try:
    makedirs(app.instance_path)
except OSError:
    pass

app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(app.instance_path, 'data.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SECRET_KEY = 'dev'
)

db = SQLAlchemy(app)
Migrate(app, db)

from loanapp.users.views import users_blp
from loanapp.loans.views import loans_blp

app.register_blueprint(users_blp)
app.register_blueprint(loans_blp)

app.cli.add_command(commands.create_admin_command)
app.cli.add_command(commands.init_database)
