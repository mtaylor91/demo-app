from sqlalchemy.sql import select

from ..db import group_table, group_policy_table, user_group_table


class Group(object):
    def __init__(self, name, users=None, policies=None):
        self.name = name
        self.users = users
        self.policies = policies


class GroupsDAO(object):
    def __init__(self, session):
        self.session = session

    def get(self, name):
        group = self.session.execute(
            select([group_table.c.name])
            .where(group_table.c.name == name)
        ).first()

        if not group:
            return None

        users = map(
            lambda user_group: user_group['user'],
            self.session.execute(
                select([user_group_table.c.user])
                .where(user_group_table.c.group == name)
            )
        )

        policies = map(
            lambda group_policy: group_policy['policy'],
            self.session.execute(
                select([group_policy_table.c.policy])
                .where(group_policy_table.c.group == name)
            )
        )

        return Group(
            name=group['name'],
            users=list(users),
            policies=list(policies)
        )

    def list(self):
        results = self.session.execute(
            select([
                group_table.c.name,
                user_group_table.c.user,
                group_policy_table.c.policy,
            ]).select_from(
                group_table
                .outerjoin(user_group_table,
                           group_table.c.name == user_group_table.c.group)
                .outerjoin(group_policy_table,
                           group_table.c.name == group_policy_table.c.group)
            ).order_by(
                group_table.c.name,
                user_group_table.c.user,
                group_policy_table.c.policy,
            )
        )

        group = None
        groups = []

        for result in results:
            if group is None or result['name'] != group.name:
                if group is not None:
                    groups.append(group)
                group = Group(name=result['name'])
                group.users = []
                group.policies = []

            if result['user'] is not None:
                group.users.append(result['user'])

            if result['policy'] is not None:
                group.policies.append(result['policy'])

        if group is not None:
            groups.append(group)

        return groups

    def update(self, name, users=None, policies=None):
        group = self.session.execute(
            select([group_table.c.name])
            .where(group_table.c.name == name)
        ).first()

        if not group:
            self.session.execute(
                group_table.insert().values(name=name)
            )

        if users is not None:
            self.session.execute(user_group_table.delete()
                                 .where(user_group_table.c.group == name))
            for user in users:
                self.session.execute(
                    user_group_table.insert()
                    .values(user=user, group=name)
                )

        if policies is not None:
            self.session.execute(group_policy_table.delete()
                                 .where(group_policy_table.c.group == name))
            for policy in policies:
                self.session.execute(
                    group_policy_table.insert()
                    .values(group=name, policy=policy)
                )

        return self.get(name)

    def delete(self, name):
        self.session.execute(group_policy_table.delete()
                             .where(group_policy_table.c.group == name))
        self.session.execute(user_group_table.delete()
                             .where(user_group_table.c.group == name))
        self.session.execute(group_table.delete()
                             .where(group_table.c.name == name))


__all__ = ['GroupsDAO']
