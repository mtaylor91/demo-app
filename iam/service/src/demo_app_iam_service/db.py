from flask_sqlalchemy import SQLAlchemy

from .app import app

db = SQLAlchemy(app)


user_table = db.Table(
    'user',
    db.Column('email', db.String, primary_key=True),
)


group_table = db.Table(
    'group',
    db.Column('name', db.String, primary_key=True),
)


policy_table = db.Table(
    'policy',
    db.Column('name', db.String, primary_key=True),
)


rule_table = db.Table(
    'rule',
    db.Column('effect', db.String, nullable=False),
    db.Column('action', db.String, nullable=False),
    db.Column('resource', db.String, nullable=False),
    db.Column('precedence', db.Integer, default=0, nullable=False),
    db.Column('policy', db.String, db.ForeignKey(policy_table.c.name),
              nullable=False),
)


user_group_table = db.Table(
    'user_group',
    db.Column('user', db.String, db.ForeignKey(user_table.c.email),
              nullable=False),
    db.Column('group', db.String, db.ForeignKey(group_table.c.name),
              nullable=False),
)


user_policy_table = db.Table(
    'user_policy',
    db.Column('user', db.String, db.ForeignKey(user_table.c.email),
              nullable=False),
    db.Column('policy', db.String, db.ForeignKey(policy_table.c.name),
              nullable=False),
)


group_policy_table = db.Table(
    'group_policy',
    db.Column('group', db.String, db.ForeignKey(group_table.c.name),
              nullable=False),
    db.Column('policy', db.String, db.ForeignKey(policy_table.c.name),
              nullable=False),
)


__all__ = ['db']
