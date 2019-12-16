from ..db import policy_table, rule_table, \
    user_policy_table, group_policy_table


class Policy(object):
    def __init__(self, name, users=None, groups=None, rules=None):
        self.name = name
        self.users = users
        self.groups = groups
        self.rules = rules


class PoliciesDAO(object):
    def __init__(self, session):
        self.session = session

    def get(self, name):
        session = self.session

        policy = session.execute(
            policy_table.select()
            .where(policy_table.c.name == name)
        ).first()

        if not policy:
            return None

        users = map(
            lambda row: row['user'],
            session.execute(
                user_policy_table.select()
                .where(user_policy_table.c.policy == name)
            )
        )

        groups = map(
            lambda row: row['group'],
            session.execute(
                group_policy_table.select()
                .where(group_policy_table.c.policy == name)
            )
        )

        rules = map(
            lambda row: {
                'effect': row['effect'],
                'action': row['action'],
                'resource': row['resource'],
                'precedence': row['precedence']
            },
            session.execute(
                rule_table.select()
                .where(rule_table.c.policy == name)
            )
        )

        return Policy(
            name=policy['name'],
            users=list(users),
            groups=list(groups),
            rules=list(rules)
        )

    def list(self):
        return list(map(
            lambda policy: Policy(
                name=policy['name'],
                users=None,
                groups=None,
                rules=None
            ),
            self.session.execute(policy_table.select())
        ))

    def update(self, name, rules=None, users=None, groups=None):
        session = self.session

        policy = session.execute(
            policy_table
            .select()
            .where(policy_table.c.name == name)
        ).first()

        if not policy:
            session.execute(
                policy_table
                .insert()
                .values(name=name)
            )

        if rules is not None:
            session.execute(rule_table.delete()
                            .where(rule_table.c.policy == name))
            for rule in rules:
                rule['policy'] = name
                session.execute(rule_table.insert().values(**rule))

        if users is not None:
            session.execute(user_policy_table.delete()
                            .where(user_policy_table.c.policy == name))
            for user in users:
                session.execute(user_policy_table.insert()
                                .values({'user': user, 'policy': name}))

        if groups is not None:
            session.execute(group_policy_table.delete()
                            .where(group_policy_table.c.policy == name))
            for group in groups:
                session.execute(group_policy_table.insert()
                                .values({'group': group, 'policy': name}))

        return self.get(name)

    def delete(self, name):
        session = self.session
        session.execute(rule_table.delete()
                        .where(rule_table.c.policy == name))
        session.execute(user_policy_table.delete()
                        .where(user_policy_table.c.policy == name))
        session.execute(group_policy_table.delete()
                        .where(group_policy_table.c.policy == name))
        session.execute(policy_table.delete()
                        .where(policy_table.c.name == name))


__all__ = ['PoliciesDAO']
