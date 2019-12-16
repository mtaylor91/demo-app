from flask import Flask
from os import environ

from .config import CONFIG, DEFAULTS


def create(config):
    app = Flask(__name__)
    configure(app, config)
    return app


def configure(app, config):
    app.config.update({
        name: transform(resolve(config, name))
        for name, transform in CONFIG.items()
    })


def resolve(config, name):
    value = config.get(name)
    if value:
        return value
    else:
        if name in DEFAULTS:
            return DEFAULTS[name]
        else:
            raise RuntimeError("Undefined config parameter: " + name)


app = create(environ)


__all__ = ['app']
