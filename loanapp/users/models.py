from loanapp import db
from loanapp.loans.models import Application, Loan

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    password = db.Column(db.String(80))
    applications = db.relationship('Application', backref='user', lazy='dynamic', foreign_keys='Application.user_id')
    loans = db.relationship('Loan', backref='user', lazy='dynamic', foreign_keys='Loan.user_id')
    admin = db.Column(db.Boolean, default=False)
    agent = db.Column(db.Boolean, default=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def setAdmin(self):
        self.admin = True

    def setAgent(self):
        self.agent = True

    def __repr__(self):
        return '<User %r>' % self.id
