from flask_restplus import Namespace, Resource, fields

from ..db import db
from ..policies.api import policy_rule
from .dao import RulesDAO


api = Namespace('rules', description='Rule Management')


rule = api.inherit('Rule', policy_rule, {
    'policy': fields.String(required=True),
    'user': fields.String(readonly=True),
    'group': fields.String(readonly=True)
})


@api.route('/')
class Rules(Resource):
    '''List policy rules'''
    @api.doc('list_policy_rules')
    @api.marshal_list_with(rule, skip_none=True)
    def get(self):
        session = db.session
        rules = RulesDAO(session)
        results = rules.list()
        session.commit()
        return results

    '''Create policy rule'''
    @api.doc('create_policy_rule')
    @api.expect(rule)
    @api.marshal_with(rule)
    def post(self):
        session = db.session
        rules = RulesDAO(session)
        result = rules.create(**api.payload)
        session.commit()
        return result


@api.route('/user/<string:user>')
class UserRules(Resource):
    '''Get rules matching the request parameters'''
    @api.doc('list_user_policy_rules')
    @api.marshal_list_with(rule, skip_none=True)
    def get(self, user):
        session = db.session
        rules = RulesDAO(session)
        results = rules.list(user=user)
        session.commit()
        return results


@api.route('/group/<string:group>')
class GroupRules(Resource):
    @api.doc('list_group_policy_rules')
    @api.marshal_list_with(rule, skip_none=True)
    def get(self, group):
        session = db.session
        rules = RulesDAO(session)
        results = rules.list(group=group)
        session.commit()
        return results


__all__ = ['api', 'rule', 'Rules', 'UserRules', 'GroupRules']
