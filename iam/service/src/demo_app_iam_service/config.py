

CONFIG = {
    'SQLALCHEMY_TRACK_MODIFICATIONS': bool,
    'SQLALCHEMY_DATABASE_URI': str,
    'SQLALCHEMY_ECHO': bool,
    'ERROR_404_HELP': bool,
}


DEFAULTS = {
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'postgres://postgres@localhost:5432',
    'SQLALCHEMY_ECHO': False,
    'ERROR_404_HELP': False,
}


__all__ = ['CONFIG', 'DEFAULTS']
