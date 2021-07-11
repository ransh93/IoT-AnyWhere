from muddy.maker import make_mud, make_acl_names, make_policy, make_acls, make_support_info
from muddy.models import Direction, MatchType
import json
import random


class MudGenerator(object):
    def __init__(self, version, mud_url, is_supported, cache_validity, system_info):
        self.support_info = make_support_info(version, mud_url, is_supported, cache_validity, system_info)
        self.mud_name = f'mud-{random.randint(10000, 99999)}'

        self.policies = {}
        self.from_acl = []
        self.to_acl = []
        self.acl = []

    def generate_mud(self, from_rules, to_rules, generalized_mud_name):

        # TODO: MatchType.IS_CLOUD read more about it

        if len(from_rules) == 0 or len(to_rules) == 0:
            return

        # handel from rules
        direction_initiated = Direction.FROM_DEVICE
        for rule in from_rules:
            ip_version, protocol = rule.get_ip_version_and_protocol()
            identifier = rule.get_ace_identifier()  # get domain of ip
            port = rule.get_ace_port()  # get port
            acl_names = make_acl_names(self.mud_name, ip_version, direction_initiated)
            self.policies.update(make_policy(direction_initiated, acl_names))
            if len(self.from_acl) == 0:
                self.from_acl.append(make_acls([ip_version], identifier, protocol, MatchType.IS_CLOUD, direction_initiated,
                              [port], None, acl_names))
            else:
                acl = (make_acls([ip_version], identifier, protocol, MatchType.IS_CLOUD, direction_initiated,
                              [port], None, acl_names))
                self.from_acl[0]["aces"]["ace"].append(acl["aces"]["ace"][0])


        # handel to rules
        direction_initiated = Direction.TO_DEVICE
        for rule in to_rules:
            ip_version, protocol = rule.get_ip_version_and_protocol()
            identifier = rule.get_ace_identifier()  # get domain of ip
            port = rule.get_ace_port()  # get port
            acl_names = make_acl_names(self.mud_name, ip_version, direction_initiated)
            self.policies.update(make_policy(direction_initiated, acl_names))
            if len(self.to_acl) == 0:
                self.to_acl.append(make_acls([ip_version], identifier, protocol, MatchType.IS_CLOUD, direction_initiated,
                                   [port], None, acl_names))
            else:
                acl = (make_acls([ip_version], identifier, protocol, MatchType.IS_CLOUD, direction_initiated,
                                 [port], None, acl_names))
                self.to_acl[0]["aces"]["ace"].append(acl["aces"]["ace"][0])

        self.acl = self.from_acl + self.to_acl

        # when they are None is means we have no rules and policies
        if len(self.acl) != 0 or len(self.policies) != 0:
            mud = make_mud(self.support_info, self.policies, self.acl)

            f = open(generalized_mud_name, "w")
            f.write(json.dumps(mud, indent=4))
            f.close()
