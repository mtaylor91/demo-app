from sqlalchemy.sql import select, and_

from ..db import user_policy_table, group_policy_table, user_group_table, \
    rule_table


class Rule(object):
    def __init__(self, policy, user=None, group=None,
                 effect=None, action=None, resource=None,
                 precedence=None):
        self.policy = policy
        self.user = user
        self.group = group
        self.effect = effect
        self.action = action
        self.resource = resource
        self.precedence = precedence


class RulesDAO(object):
    def __init__(self, session):
        self.session = session

    def list(self, user=None, group=None):
        if user is not None:
            # Select the union of the user policy rules
            # and group policy rules for the given user.
            query = select([
                user_group_table.c.user,
                group_policy_table.c.group,
                rule_table.c.policy,
                rule_table.c.effect,
                rule_table.c.action,
                rule_table.c.resource,
                rule_table.c.precedence,
            ]).where(and_(
                user_group_table.c.user == user,
                user_group_table.c.group == group_policy_table.c.group,
                group_policy_table.c.policy == rule_table.c.policy
            )).union(
                select([
                    user_policy_table.c.user,
                    None,
                    rule_table.c.policy,
                    rule_table.c.effect,
                    rule_table.c.action,
                    rule_table.c.resource,
                    rule_table.c.precedence,
                ]).where(and_(
                    user_policy_table.c.user == user,
                    user_policy_table.c.policy == rule_table.c.policy
                ))
            )
        elif group is not None:
            # Select the group's policy rules
            query = select([
                group_policy_table.c.group,
                rule_table.c.policy,
                rule_table.c.effect,
                rule_table.c.action,
                rule_table.c.resource,
                rule_table.c.precedence,
            ]).where(and_(
                group_policy_table.c.group == group,
                group_policy_table.c.policy == rule_table.c.policy
            ))
        else:
            # Select all rules
            query = select([
                rule_table.c.policy,
                rule_table.c.effect,
                rule_table.c.action,
                rule_table.c.resource,
                rule_table.c.precedence,
            ])

        # Execute query and transform result rows into Rule objects
        policy_rules = map(
            lambda row: Rule(
                user=('user' in row and row['user']) or None,
                group=('group' in row and row['group']) or None,
                policy=row['policy'],
                effect=row['effect'],
                action=row['action'],
                resource=row['resource'],
                precedence=row['precedence']
            ),
            self.session.execute(query)
        )

        # Reify the Rule list map
        return list(policy_rules)

    def create(self, **kwargs):
        policy = kwargs['policy']
        precedence = kwargs.get('precedence', 0)
        resource = kwargs['resource']
        action = kwargs['action']
        effect = kwargs['effect']

        rule = self.session.execute(
            rule_table.select().where(and_(
                rule_table.c.effect == effect,
                rule_table.c.action == action,
                rule_table.c.resource == resource,
                rule_table.c.precedence == precedence,
                rule_table.c.policy == policy
            ))
        ).first()

        if rule is None:
            self.session.execute(
                rule_table.insert().values(
                    effect=effect,
                    action=action,
                    resource=resource,
                    precedence=precedence,
                    policy=policy
                )
            )


__all__ = ['RulesDAO']
