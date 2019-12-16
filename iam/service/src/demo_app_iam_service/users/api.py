from flask_restplus import Namespace, Resource, fields
from flask import abort

from ..db import db
from .dao import UsersDAO


api = Namespace('users', description='User Management')


user = api.model('User', {
    'email': fields.String(required=True),
    'groups': fields.List(fields.String(required=True)),
    'policies': fields.List(fields.String(required=True)),
})


@api.route('/')
class Users(Resource):
    '''List all users visible to the caller'''
    @api.doc('list_users')
    @api.marshal_list_with(user, skip_none=True)
    def get(self):
        session = db.session
        users = UsersDAO(session)
        results = users.list()
        session.commit()
        return results

    '''Create a new user'''
    @api.doc('create_user')
    @api.expect(user)
    @api.marshal_with(user, code=201)
    def post(self):
        session = db.session
        users = UsersDAO(session)
        data = api.payload
        email = data.pop('email')
        user = users.update(email, **data)
        session.commit()
        return user, 201


@api.route("/<string:email>")
class User(Resource):
    '''Get user'''
    @api.doc('get_user')
    @api.marshal_with(user)
    def get(self, email):
        session = db.session
        users = UsersDAO(session)
        user = users.get(email) or abort(404)
        session.commit()
        return user

    '''Update user'''
    @api.doc('update_user')
    @api.expect(user)
    @api.marshal_with(user)
    def patch(self, email):
        session = db.session
        users = UsersDAO(session)
        user = users.get(email) or abort(404)
        data = api.payload
        data.pop('email')
        user = users.update(email, **data)
        session.commit()
        return user

    '''Delete user'''
    @api.doc('delete_user')
    @api.marshal_with(user)
    def delete(self, email):
        session = db.session
        users = UsersDAO(session)
        user = users.get(email) or abort(404)
        users.delete(user)
        session.commit()
        return user


__all__ = ['api', 'Users', 'User', 'user']
