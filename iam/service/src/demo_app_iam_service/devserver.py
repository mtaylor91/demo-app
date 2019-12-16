#!/usr/bin/env python
from demo_app_iam_service.app import app
from demo_app_iam_service.db import db


DEFAULT_OPTS = {
    'debug': True
}


def main(**opts):
    db.create_all()
    app.run(**opts)


if __name__ == '__main__':
    main(**DEFAULT_OPTS)
