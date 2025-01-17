from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


opplegg_traits = db.Table('opplegg_traits',
    db.Column('opplegg_id', db.Integer, db.ForeignKey('opplegg.id')),
    db.Column('trait_id', db.Integer, db.ForeignKey('trait.id'))
)

opplegg_user_favorites = db.Table('opplegg_user_favorites',
    db.Column('opplegg_id', db.Integer, db.ForeignKey('opplegg.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class Opplegg(db.Model):
    __tablename__ = "opplegg"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    traits = db.relationship('Trait', secondary=opplegg_traits, backref='opplegg')
    
    # Use back_populates for bidirectional relationships
    comments = db.relationship('Comment', back_populates='opplegg')

class Trait(db.Model):
    __tablename__ = 'trait'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    klasse = db.Column(db.String(100))
    forklaring = db.Column(db.String(500))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    role = db.Column(db.String(50), default='user')
    is_email_confirmed = db.Column(db.Boolean, default=False)
    opplegg = db.relationship('Opplegg')
    favorites = db.relationship('Opplegg', secondary=opplegg_user_favorites, backref='user_favorite')

    # Use back_populates to link back to the Comment relationship
    comments = db.relationship('Comment', back_populates='user')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    opplegg_id = db.Column(db.Integer, db.ForeignKey('opplegg.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Use back_populates to establish the bidirectional relationship
    opplegg = db.relationship('Opplegg', back_populates='comments')
    user = db.relationship('User', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'