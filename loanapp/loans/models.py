from loanapp import db
from datetime import datetime

class Loan(db.Model):

    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(30), db.ForeignKey('users.id'))
    loan_state = db.Column(db.String(10))
    principal = db.Column(db.Integer)
    tenure = db.Column(db.Integer)
    interest = db.Column(db.Integer)
    interest_rate = db.Column(db.Integer)
    emi = db.Column(db.Integer)
    total = db.Column(db.Integer)
    request_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    start_date = db.Column(db.DateTime(timezone=True), default=None)

    def __init__(self, principal, tenure, interest, interest_rate, emi, total, user_id):
        self.principal = principal
        self.tenure = tenure
        self.interest = interest
        self.interest_rate = interest_rate
        self.emi = emi
        self.total = total
        self.user_id = user_id

    def setLoanState(self, loanstate):
        self.loan_state = loanstate

    def setStartDate(self):
        self.start_date = datetime.utcnow()

    def __repr__(self):
        return f"Loan id: {self.id}, principal: {self.principal}, userid: {self.user_id}"

class Application(db.Model):

    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amount = db.Column(db.Integer)
    tenure = db.Column(db.Integer)
    request_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    def __init__(self, user_id, amount, tenure):
        self.user_id = user_id
        self.amount = amount
        self.tenure = tenure

    def __repr__(self):
        return f"Application {self.id}, userid: {self.user_id}, amount: {self.amount}"
