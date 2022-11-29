from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

from blocklist import blocklist
from models import UserModel
from schemas import PlainUserSchema, UserUpdateSchema, LoginUserSchema, UserSchema
from db import db
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import pbkdf2_sha256

blp = Blueprint("users", __name__, description="Operations on users")


# Create a User
@blp.route("/register")
class CreateUser(MethodView):

    @blp.arguments(PlainUserSchema)
    @blp.response(201, PlainUserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="A user with that username already exists")

        user_data["password"] = pbkdf2_sha256.hash(user_data["password"])
        user = UserModel(**user_data)
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify("message : User Created Successfully"), 201
        except SQLAlchemyError:
            abort(500, message="An error occurred while loading the user into the Database")


@blp.route("/user/<int:user_id>")
class User(MethodView):
    # Read a single user
    @blp.response(200, PlainUserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    # Updates a user
    @jwt_required()
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, PlainUserSchema)
    def put(self, user_data, user_id):
        user = UserModel.query.get_or_404(user_id)
        if user:
            if user.id == get_jwt_identity():
                user.username = user_data["username"]
                user.password = user_data["password"]
                user.fullname = user_data["fullname"]
                user.photo = user_data["photo"]
                try:
                    db.session.add(user)
                    db.session.commit()
                    return jsonify("message : User Updates Successfully"), 201
                except SQLAlchemyError:
                    abort(500, message="An error occurred while loading the user into the Database")
            else:
                abort(401, message="Can't Delete other users")
        else:
            abort(404, message="User Not Found")

    # Deletes a user
    @jwt_required()
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        if user.id == get_jwt_identity():
            try:
                db.session.delete(user)
                db.session.commit()
                return {"message": "User Deleted"}, 200
            except SQLAlchemyError:
                abort(500, message="An error occurred while loading the user")

        else:
            abort(401, message="Can't Delete other users")


# Get a list of all users
@blp.route("/users")
class Users(MethodView):
    @blp.response(201, PlainUserSchema(many=True))
    def get(self):
        return UserModel.query.all()


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(LoginUserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}

        abort(401, message="Invalid Credentials")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(selfself):
        jti = get_jwt()["jti"]
        blocklist.append(jti)
        return {"message":"Logged out"}
