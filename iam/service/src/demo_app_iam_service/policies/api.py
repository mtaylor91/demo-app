from flask_restplus import Namespace, Resource, fields
from flask import abort

from ..db import db
from .dao import PoliciesDAO


api = Namespace('policies', description='Policy Management')


policy_rule = api.model('PolicyRule', {
    'precedence': fields.Integer(default=0),
    'resource': fields.String(required=True),
    'action': fields.String(required=True),
    'effect': fields.String(required=True),
})


policy = api.model('Policy', {
    'name': fields.String(required=True),
    'rules': fields.List(fields.Nested(policy_rule, required=True)),
    'users': fields.List(fields.String(required=True)),
    'groups': fields.List(fields.String(required=True))
})


@api.route('/')
class Policies(Resource):
    '''List all policies'''
    @api.doc('list_policies')
    @api.marshal_list_with(policy, skip_none=True)
    def get(self):
        session = db.session
        policies = PoliciesDAO(session)
        results = policies.list()
        session.commit()
        return results

    '''Create a new policy'''
    @api.doc('create_policy')
    @api.expect(policy)
    @api.marshal_with(policy, code=201)
    def post(self):
        session = db.session
        policies = PoliciesDAO(session)
        data = api.payload
        name = data.pop('name')
        policy = policies.update(name, **data)
        session.commit()
        return policy, 201


@api.route('/<string:name>')
class Policy(Resource):
    '''Get the specified policy'''
    @api.doc('get_policy')
    @api.marshal_with(policy)
    def get(self, name):
        session = db.session
        policies = PoliciesDAO(session)
        policy = policies.get(name) or abort(404)
        session.commit()
        return policy

    '''Update the specified policy'''
    @api.doc('update_policy')
    @api.expect(policy)
    @api.marshal_with(policy)
    def patch(self, name):
        session = db.session
        policies = PoliciesDAO(session)
        policy = policies.get(name) or abort(404)
        data = api.payload
        data.pop('name')
        policy = policies.update(name, **data)
        session.commit()
        return policy

    '''Delete the specified policy'''
    @api.doc('delete_policy')
    @api.marshal_with(policy)
    def delete(self, name):
        session = db.session
        policies = PoliciesDAO(session)
        policy = policies.get(name) or abort(404)
        policies.delete(policy)
        session.commit()
        return policy


__all__ = ['api', 'Policies', 'Policy', 'policy', 'policy_rule']
