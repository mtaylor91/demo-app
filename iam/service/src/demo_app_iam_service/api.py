from pkg_resources import get_distribution
from flask_restplus import Api

from .app import app
from .users import users_api
from .groups import groups_api
from .policies import policies_api
from .rules import rules_api


TITLE = 'Demo App IAM'

DESCRIPTION = 'Demo App - Identity and Access Management APIs'

VERSION = get_distribution('demo_app_iam_service').version


api = Api(app, title=TITLE, description=DESCRIPTION, version=VERSION)

api.add_namespace(users_api, path='/users/v1')
api.add_namespace(groups_api, path='/groups/v1')
api.add_namespace(policies_api, path='/policies/v1')
api.add_namespace(rules_api, path='/rules/v1')


__all__ = ['api']
