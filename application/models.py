# db model classes
from . import db


class Role(db.Model):
    """docstring for Role"""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role {0}>'.format(self.name)


class User(db.Model):
    """docstring for User"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    address = db.Column(db.String)
    email = db.Column(db.String)

    def __repr__(self):
        return '<User {0}>'.format(self.username)
