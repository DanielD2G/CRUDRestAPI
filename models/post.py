from db import db
from sqlalchemy.sql import func


class PostModel(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20))
    created = db.Column(db.DateTime, default=func.now())
    updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    status = db.Column(db.Boolean())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=False, nullable=False)
    user = db.relationship("UserModel", back_populates="posts")