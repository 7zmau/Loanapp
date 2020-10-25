from flask import Blueprint, request, jsonify, make_response, redirect
from loanapp.users.models import User
from loanapp import db, app
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime

users_blp = Blueprint("users", __name__, url_prefix="/users")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            current_user = User.query.get(data["user_id"])
        except:
            return jsonify({"message": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@users_blp.route("", methods=["POST"])
def create_user():
    """ Create a user with name and password. """

    data = request.get_json()

    if User.query.filter_by(name=data["name"]).first():
        jsonify({"message": "User with that name already exists."})

    hashed_passwd = generate_password_hash(data["password"], method="sha256")
    new_user = User(name=data["name"], password=hashed_passwd)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "New user created."})


@users_blp.route("", methods=["GET"])
@token_required
def get_all_users(current_user):
    """ Get all users. Can be done by admin and agent. """

    if current_user.admin or current_user.agent:
        users = User.query.all()

        output = []

        for user in users:
            user_data = {}
            user_data["id"] = user.id
            user_data["name"] = user.name
            user_data["admin"] = user.admin
            user_data["agent"] = user.agent
            output.append(user_data)

        return jsonify({"users": output})

    return jsonify({"message": "Cannot perform the action."})


@users_blp.route("/<user_id>", methods=["GET"])
@token_required
def get_this_user(current_user, user_id):
    """ Get a particular user. Can be done by admin and agent. """

    if current_user.admin or current_user.agent:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "User does not exist."})

        user_data = {}
        user_data["id"] = user.id
        user_data["name"] = user.name
        application_ids = []
        for application in user.applications:
            application_ids.append(application.id)
        user_data["applications"] = application_ids
        loan_ids = []
        for loan in user.loans:
            loan_ids.append(loan.id)
        user_data["loans"] = loan_ids

        return jsonify({"user": user_data})

    return jsonify({"message": "Cannot perform the action."})


@users_blp.route("/<user_id>", methods=["PATCH"])
@token_required
def promote_to_agent(current_user, user_id):
    """ Promote a user to agent. Can be done by admin only. """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform the action"})

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User does not exist."})

    user.agent = True
    db.session.commit()

    message = "User: " + str(user.id) + " is now an agent."
    return jsonify({"message": message})


@users_blp.route("/<user_id>", methods=["DELETE"])
@token_required
def delete_this_user(current_user, user_id):
    """ Delete a user. Can be done by admin and agent. """

    if current_user.admin or current_user.agent:
        user = User.query.get(user_id)

        if not user:
            return jsonify({"message": "User does not exist."})

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User Deleted."})

    return jsonify({"message": "Cannot perform the action."})


@users_blp.route("/login")
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm="Login required"'},
        )

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response(
            "Could not verify.",
            401,
            {"WWW-Authenticate": 'Basic realm="Login required"'},
        )

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                "user_id": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            },
            app.config["SECRET_KEY"],
        )

        return jsonify({"token": token.decode("UTF-8")})

    return make_response(
        "Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Login required"'}
    )
