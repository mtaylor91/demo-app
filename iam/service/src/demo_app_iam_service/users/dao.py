from sqlalchemy.sql import select

from ..db import user_table, user_group_table, user_policy_table


class User(object):
    def __init__(self, email, groups=None, policies=None):
        self.email = email
        self.groups = groups
        self.policies = policies


class UsersDAO(object):
    def __init__(self, session):
        self.session = session

    def get(self, email):
        user = self.session.execute(
            select([user_table.c.email])
            .where(user_table.c.email == email)
        ).first()

        if not user:
            return None

        groups = map(
            lambda user_group: user_group['group'],
            self.session.execute(
                select([user_group_table.c.group])
                .where(user_group_table.c.user == email)
            )
        )

        policies = map(
            lambda user_policy: user_policy['policy'],
            self.session.execute(
                select([user_policy_table.c.policy])
                .where(user_policy_table.c.user == email)
            )
        )

        return User(
            email=user['email'],
            groups=list(groups),
            policies=list(policies)
        )

    def list(self):
        session = self.session

        rows = session.execute(
            select([
                user_table.c.email,
                user_group_table.c.group,
                user_policy_table.c.policy,
            ]).select_from(
                user_table
                .outerjoin(user_group_table,
                           user_table.c.email == user_group_table.c.user)
                .outerjoin(user_policy_table,
                           user_table.c.email == user_policy_table.c.user)
            ).order_by(
                user_table.c.email,
                user_group_table.c.group,
                user_policy_table.c.policy,
            )
        )

        user = None
        users = []

        for row in rows:
            email = row['email']
            group = row['group']
            policy = row['policy']

            if user is None or email != user.email:
                user = User(email=email)
                user.groups = []
                user.policies = []
                users.append(user)

            if group is not None and group not in user.groups:
                user.groups.append(row['group'])

            if policy is not None and policy not in user.policies:
                user.policies.append(row['policy'])

        return users

    def update(self, email, groups=None, policies=None):
        exists = self.session.execute(
            user_table.select().where(user_table.c.email == email)
        ).first()

        if not exists:
            self.session.execute(
                user_table.insert().values(email=email)
            )

        if groups is not None:
            self.session.execute(user_group_table.delete()
                                 .where(user_group_table.c.user == email))
            for group in groups:
                self.session.execute(
                    user_group_table.insert()
                    .values(user=email, group=group)
                )

        if policies is not None:
            self.session.execute(user_policy_table.delete()
                                 .where(user_policy_table.c.user == email))
            for policy in policies:
                self.session.execute(
                    user_policy_table.insert()
                    .values(user=email, policy=policy)
                )

        return self.get(email)

    def delete(self, email):
        self.session.execute(user_policy_table.delete()
                             .where(user_policy_table.c.user == email))
        self.session.execute(user_group_table.delete()
                             .where(user_group_table.c.user == email))
        self.session.execute(user_table.delete()
                             .where(user_table.c.email == email))


__all__ = ['UsersDAO']
