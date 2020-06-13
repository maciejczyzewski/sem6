import json
import arrow
import datetime
import urllib, hashlib
from passlib.hash import pbkdf2_sha256
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired,
)
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# FIXME: get from Config?
SECRET_KEY = "omgomgomg"

association_table = db.Table(
    'association', db.Model.metadata,
    db.Column('match_id', db.Integer, db.ForeignKey('match.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(120), nullable=False)

    verified = db.Column(db.Boolean, default=False)
    recovery = db.Column(db.String(120))
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    tiers = db.relationship('Tier', backref=db.backref('user', lazy=True))

    matches = db.relationship("Match",
                              secondary=association_table,
                              backref="users")
    tournaments = db.relationship('Tournament',
                            backref=db.backref('owner', lazy=True))

    def __repr__(self):
        return '<User %r>' % self.email

    def hash_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=60000):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({"user_id": self.id})

    def get_avatar(self, size=40):
        gravatar_url = "https://www.gravatar.com/avatar/" + hashlib.md5(
            self.email.lower().encode('utf-8')).hexdigest() + "?"
        gravatar_url += urllib.parse.urlencode({'s': str(size)})
        return gravatar_url

    def get_member(self):
        return arrow.get(self.date_created).humanize()

    # FIXME: function to calculate points???

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = (User.query.filter(User.id == data["user_id"]).first())
        return user


class Tournament(db.Model):
    __tablename__ = "tournament"
    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    title = db.Column(db.String(120), unique=True, nullable=False)
    date_start = db.Column(db.DateTime, nullable=False)
    date_deadline = db.Column(db.DateTime, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    location = db.Column(db.String(120))
    max_users = db.Column(db.Integer, nullable=False)
    readme = db.Column(db.Text)
    ladder = db.Column(db.Text)  # ID match-y jako drzewo [0 [1]]

    tiers = db.relationship('Tier',
                            backref=db.backref('tournament', lazy=True),
                            order_by='Tier.date_created', lazy='dynamic')
    matches = db.relationship('Match',
                              backref=db.backref('tournament', lazy=True))

    def get_date_start(self):
        return arrow.get(self.date_start).humanize()

    def get_date_deadline(self):
        return arrow.get(self.date_deadline).humanize()

    def get_ladder(self):
        if self.ladder:
            return json.loads(self.ladder)
        else:
            return {"teams": None, "results": None}

class Match(db.Model):
    __tablename__ = "match"
    id = db.Column(db.Integer, primary_key=True)

    match_id = db.Column(db.Integer, nullable=False)
    next_match_id = db.Column(db.Integer)
    flag = db.Column(db.Integer, nullable=False)

    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

    user_id_1 = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_id_2 = db.Column(db.Integer, db.ForeignKey('user.id'))

    results = db.Column(db.Text)
    results_by_user_id_1 = db.Column(db.Text)
    results_by_user_id_2 = db.Column(db.Text)

    def get_user_1(self):
        if self.user_id_1:
            return User.query.filter(User.id == self.user_id_1).first()
        else:
            return None

    def get_user_2(self):
        if self.user_id_2:
            return User.query.filter(User.id == self.user_id_2).first()
        else:
            return None

    def get_tournament(self):
        return Tournament.query.filter(Tournament.id == self.tournament_id).first()

class Tier(db.Model):
    __tablename__ = "tier"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))

    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    license = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def get_tournament(self):
        return Tournament.query.filter(Tournament.id == self.tournament_id).first()
