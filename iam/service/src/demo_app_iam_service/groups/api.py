from flask_restplus import Namespace, Resource, fields
from flask import abort

from ..db import db
from .dao import GroupsDAO


api = Namespace('groups', description='Group Management')


group = api.model('Group', {
    'name': fields.String(required=True),
    'users': fields.List(fields.String(required=True)),
    'policies': fields.List(fields.String(required=True)),
})


@api.route('/')
class Groups(Resource):
    '''List groups'''
    @api.doc('list_groups')
    @api.marshal_list_with(group)
    def get(self):
        session = db.session
        groups = GroupsDAO(session)
        results = groups.list()
        session.commit()
        return results

    '''Create group'''
    @api.doc('create_group')
    @api.expect(group)
    @api.marshal_with(group, code=201)
    def post(self):
        session = db.session
        groups = GroupsDAO(session)
        data = api.payload
        name = data.pop('name')
        group = groups.update(name, **data)
        session.commit()
        return group, 201


@api.route('/<string:name>')
class Group(Resource):
    '''Get group'''
    @api.doc('get_group')
    @api.marshal_with(group)
    def get(self, name):
        session = db.session
        groups = GroupsDAO(session)
        group = groups.get(name) or abort(404)
        session.commit()
        return group

    '''Update group'''
    @api.doc('update_group')
    @api.expect(group)
    @api.marshal_with(group)
    def patch(self, name):
        session = db.session
        groups = GroupsDAO(session)
        group = groups.get(name) or abort(404)
        data = api.payload
        'name' in data and data.pop('name')
        group = groups.update(name, **data)
        session.commit()
        return group

    '''Delete group'''
    @api.doc('delete_group')
    @api.marshal_with(group)
    def delete(self, name):
        session = db.session
        groups = GroupsDAO(session)
        group = groups.get(name)
        group is not None and groups.delete(group.name)
        session.commit()
        return group


__all__ = ['api', 'Groups', 'Group', 'group']
