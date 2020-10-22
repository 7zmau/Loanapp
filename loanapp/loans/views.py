from flask import Blueprint, request, jsonify, make_response, redirect
from loanapp.loans.models import Loan, Application
from loanapp.users.models import User
from loanapp.users.views import token_required
from loanapp.loanapplib.gir import get_interest_rate
from loanapp.loanapplib.emi import calculate_emi
from loanapp import db
from datetime import datetime


loans_blp = Blueprint("loans", __name__, url_prefix="/loans")

@loans_blp.route("/get-interest-rates", methods=["GET"])
def get_interest_rates():
    try:
        tenure = int(request.get_json()["tenure"])
    except:
        return jsonify({"message": "Input is 'tenure' in months"}), 400

    if tenure <= 5:
        return jsonify({"interest_rate": 10}), 200
    elif tenure > 5 and tenure <= 24:
        return jsonify({"interest_rate": 12}), 200
    else:
        return jsonify({"interest_rate": 15}), 200


@loans_blp.route("/get-loan-info", methods=["GET"])
def get_loan_info():
    try:
        principal = int(request.get_json()["amount"])
        tenure = int(request.get_json()["tenure"])
    except:
        return jsonify({"message": "Input is 'amount' and 'tenure'"}), 400

    interest_rate = get_interest_rate(tenure)
    emi = calculate_emi(principal, interest_rate, tenure)
    total = round(emi * tenure, 2)
    interest = round(total - principal, 2)

    output = {
        "principal": principal,
        "tenure": tenure,
        "interest": interest,
        "interest_rate": interest_rate,
        "emi": emi,
        "total": total,
    }

    return jsonify({"loan_info": output})


@loans_blp.route("/", methods=["POST"])
@token_required
def loan_request(current_user):

    if not current_user.agent:
        return jsonify({"message": "Cannot perform the action."})

    try:
        application_id = request.get_json()['application_id']
        user_id = request.get_json()['user_id']
    except:
        return jsonify({"message": "Invalid input."}), 400

    userappl = Application.query.filter_by(
        id=application_id,
        user_id=user_id
    ).first()

    if not userappl:
        return jsonify({"message": "Invalid application."})

    principal = userappl.amount
    tenure = userappl.tenure

    interest_rate = get_interest_rate(tenure)
    emi = calculate_emi(principal, interest_rate, tenure)
    total = round(emi * tenure, 2)
    interest = round(total - principal, 2)

    new_loan_request = Loan(
        principal=principal,
        tenure=tenure,
        interest=interest,
        interest_rate=interest_rate,
        emi=emi,
        total=total,
        user_id=user_id
    )
    new_loan_request.setLoanState("NEW")

    db.session.add(new_loan_request)
    db.session.commit()

    return jsonify({"message": "New loan requested."})


@loans_blp.route("/", methods=["GET"])
@token_required
def get_all_loans(current_user):

    if not current_user.agent or not current_user.admin:
        loans = Loan.query.filter_by(user_id=current_user.id)
        if not loans:
            return jsonify({"loans": []})
    else:
        loans = Loan.query.all()

    output = []

    for loan in loans:
        loan_data = {}
        loan_data["id"] = loan.id
        loan_data["user_id"] = loan.user_id
        loan_data["principal"] = loan.principal
        loan_data["tenure"] = loan.tenure
        loan_data["interest"] = loan.interest
        loan_data["interest_rate"] = loan.interest_rate
        loan_data["emi"] = loan.emi
        loan_data["total"] = loan.total
        loan_data["loan_state"] = loan.loan_state
        loan_data["request_date"] = loan.request_date
        loan_data["start_date"] = loan.start_date
        output.append(loan_data)

    return jsonify({"loans": output})


@loans_blp.route("/", methods=["PUT"])
@token_required
def approve_loan(current_user):
    if not current_user.admin:
        return jsonify({"message": "Cannot perform the action."})

    try:
        loan_id = request.get_json()["loan_id"]
        user_id = request.get_json()["user_id"]
    except:
        return jsonify({"message": "Invalid input"}), 400

    loan = Loan.query.filter_by(id=loan_id, user_id=user_id).first()

    if not loan:
        return jsonify({"message": "Invalid loan ID."})

    if loan.loan_state == "NEW":
        loan.loan_state = "APPROVED"
        loan.start_date = datetime.utcnow()

        db.session.commit()
        message = "Loan " + str(loan.id) + " approved."

        return jsonify({"message": message})

    elif loan.loan_state == "APPROVED":
        return jsonify({"message": "Loan already approved."})

    return jsonify({"message": "Cannot approve loan."})


@loans_blp.route("/request-agent", methods=["POST"])
@token_required
def loan_request_user(current_user):

    data = request.get_json()

    new_loan = Application(
        user_id=current_user.id, amount=data["amount"], tenure=data["tenure"]
    )
    db.session.add(new_loan)
    db.session.commit()

    return jsonify({"message": "Agent will send a loan request soon."})


@loans_blp.route("/view-requests", methods=["GET"])
@token_required
def view_requests(current_user):

    if not current_user.agent:
        return jsonify({"message": "Cannot perform this action."})

    applications = Application.query.all()

    output = []

    for application in applications:
        application_data = {}
        application_data["application_id"] = application.id
        application_data["user_id"] = application.user_id
        application_data["amount"] = application.amount
        application_data["tenure"] = application.tenure
        application_data["request_date"] = application.request_date
        output.append(application_data)

    return jsonify({"applications": output})


@loans_blp.route("/edit/<int:loan_id>", methods=["PUT"])
@token_required
def edit_loan(current_user, loan_id):

    if not current_user.agent:
        return jsonify({"message": "Cannot perform this action."})

    loan = Loan.query.get(loan_id)

    if not loan:
        return jsonify({"message": "Invalid loan ID."})
    if loan.loan_state == 'APPROVED':
        return jsonify({"message": "Cannot edit loan."})

    try:
        principal = request.get_json()['amount']
        tenure = request.get_json()['tenure']

        interest_rate = get_interest_rate(tenure)
        emi = calculate_emi(principal, interest_rate, tenure)
        total = round(emi * tenure, 2)
        interest = round(total - principal, 2)

        loan.principal = principal
        loan.tenure = tenure
        loan.interest = interest
        loan.interest_rate = interest_rate
        loan.emi = emi
        loan.total = total
        loan.request_date = datetime.utcnow()

        db.session.commit()

        message = "Loan " + str(loan_id) + " updated."
        return jsonify({"message": message})

    except:

        message = "There was an error processing your request."
        return jsonify({"message": message})
