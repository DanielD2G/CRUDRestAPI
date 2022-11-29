from flask import jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from schemas import PlainPostSchema, PostUpdateSchema, PostSchema, ShowPostSchema
from models import PostModel, UserModel
from db import db
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("post", __name__, description="Operations on users")


@blp.route("/post/create")
class CreatePost(MethodView):
    # Creates a post
    @jwt_required()
    @blp.arguments(PostSchema)
    @blp.response(201, PlainPostSchema)
    def post(self, post_data):
        post = PostModel(**post_data, user_id=get_jwt_identity())
        try:
            db.session.add(post)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the Post")
        return post


@blp.route("/posts")
class Posts(MethodView):
    # Get all Posts
    @blp.response(200, ShowPostSchema(many=True))
    def get(self):
        return PostModel.query.all()


@blp.route("/posts/<int:post_id>")
class Post(MethodView):

    # Get a single post by its id
    @blp.response(200, ShowPostSchema)
    def get(self, post_id):
        post = PostModel.query.get_or_404(post_id)
        return post

    # Updates a Post
    @jwt_required()
    @blp.arguments(PostUpdateSchema)
    @blp.response(200, ShowPostSchema)
    def put(self, post_data, post_id):
        post = PostModel.query.get(post_id)
        if post:
            if post.user_id == get_jwt_identity():
                post.title = post_data["title"]
                post.description = post_data["description"]
                post.priority = post_data["priority"]
                post.status = post_data["status"]
            else:
                abort(401, message="Can't update post from other users")
        else:
            post_data["user_id"] = get_jwt_identity()
            post = PostModel(id=post_id, **post_data)
        try:
            db.session.add(post)
            db.session.commit()
            return post
        except SQLAlchemyError:
            abort(500, message="An error occurred while loading the user into the Database")

    # Deletes a post
    @jwt_required()
    def delete(self, post_id):
        post = PostModel.query.get_or_404(post_id)
        if post.user_id == get_jwt_identity():
            db.session.delete(post)
            db.session.commit()
            return jsonify("message: post deleted correctly")
        else:
            abort(401, message="Can't delete this post")


# Get all post from a single user
@blp.route("/user/<int:user_id>/posts")
class PostFromUser(MethodView):
    @blp.response(200, PlainPostSchema(many=True))
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user.posts.all()
