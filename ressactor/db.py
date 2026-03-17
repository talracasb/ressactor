from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

class User(db.Model):
  __tablename__ = "users"

  id: Mapped[int] = mapped_column(primary_key=True)
  username: Mapped[str] = mapped_column(unique=True)
  password: Mapped[str]

  comments: Mapped[List["Comment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
  votes: Mapped[List["Vote"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Post(db.Model):
  __tablename__ = "posts"

  id: Mapped[int] = mapped_column(primary_key=True)
  rss_id: Mapped[str] = mapped_column(unique=True)

  comments: Mapped[List["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")

class Comment(db.Model):
  __tablename__ = "comments"

  id: Mapped[int] = mapped_column(primary_key=True)
  content: Mapped[str]

  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
  post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))

  user: Mapped["User"] = relationship(back_populates="comments")
  post: Mapped["Post"] = relationship(back_populates="comments")

  votes: Mapped[List["Vote"]] = relationship(back_populates="comment", cascade="all, delete-orphan")

class Vote(db.Model):
  __tablename__ = "votes"

  id: Mapped[int] = mapped_column(primary_key=True)

  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
  comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"))

  value: Mapped[bool] = mapped_column()

  user: Mapped["User"] = relationship(back_populates="votes")
  comment: Mapped["Comment"] = relationship(back_populates="votes")

  __table_args__ = (
    UniqueConstraint("user_id", "comment_id"),
  )