from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, timedelta


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
    is_temp_password = db.Column(db.Boolean, default=False)
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
    created_at = db.Column(db.DateTime, default=datetime.now() + timedelta(hours=2))
    
    # Use back_populates to establish the bidirectional relationship
    opplegg = db.relationship('Opplegg', back_populates='comments')
    user = db.relationship('User', back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.id}>'
    
class OppleggSimilarity(db.Model):
    __tablename__ = 'opplegg_similarity'
    id = db.Column(db.Integer, primary_key=True)
    opplegg1_id = db.Column(db.Integer, db.ForeignKey('opplegg.id'), nullable=False)
    opplegg2_id = db.Column(db.Integer, db.ForeignKey('opplegg.id'), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)  # Percentage similarity

    opplegg1 = db.relationship('Opplegg', foreign_keys=[opplegg1_id])
    opplegg2 = db.relationship('Opplegg', foreign_keys=[opplegg2_id])

class ApprovedEmail(db.Model):
    __tablename__ = 'approved_emails'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(100))
    last_seen = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    visit_count = db.Column(db.Integer, default=1)
    user_type = db.Column(db.String(50))

    def __repr__(self):
        return f"<Visitor {self.ip} ({self.user_type}) - {self.visit_count} visits>"