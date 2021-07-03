import copy
import logic.constants as constants
from logic.mud_generator import MudGenerator


class MudGeneralization(object):
    def __init__(self, identical_rules, first_non_similar_from_rules, first_non_similar_to_rules,
                 second_non_similar_from_rules, second_non_similar_to_rules, generalized_from_rules, generalized_to_rules):
        self.identical_from_rules = []
        self.identical_to_rules = []
        self.non_similar_from_rules = []
        self.non_similar_to_rules = []
        self.generalized_from_rules = []
        self.generalized_to_rules = []
        self.from_rules = []
        self.to_rules = []

        # identical rules from/to separation
        for identical_rule in identical_rules:
            if identical_rule.rule_type == "from":
                self.identical_from_rules.append(identical_rule)
            else:
                self.identical_to_rules.append(identical_rule)

        # create combined non similar from and to rules
        self.non_similar_from_rules = first_non_similar_from_rules + second_non_similar_from_rules
        self.non_similar_to_rules = first_non_similar_to_rules + second_non_similar_to_rules

        # create generalized similar from and to rules
        self.create_generalized_rules(generalized_from_rules, "from")
        self.create_generalized_rules(generalized_to_rules, "to")

        self.from_rules = self.identical_from_rules + self.non_similar_from_rules + self.generalized_from_rules
        self.to_rules = self.identical_to_rules + self.non_similar_to_rules + self.generalized_to_rules

        # TODO: address the url and system info parameters to put the real ones
        mud_generator = MudGenerator(1, 'https://lighting.example.com/lightbulb2000', 48, True,
                          'The BMS Example Light Bulb')
        mud_generator.generate_mud(self.from_rules, self.to_rules)


    def create_generalized_rules(self, rules_to_generalize, direction):
        for base_rule,relations_rules in rules_to_generalize.items():
            domain_based_similarity_existence = self.check_domain_based_similarity_existence(relations_rules)
            for relations_rule in relations_rules:
                rule = relations_rule[0]
                similarity_vector = relations_rule[1]
                if similarity_vector.primary_similarity_type == constants.PORT_PROTOCOL_BASED_SIMILARITY and domain_based_similarity_existence:
                    self.add_generalized_rule(relations_rule[0], direction)  # added only the rule and not the similarity vector
                elif similarity_vector.primary_similarity_type == constants.PORT_PROTOCOL_BASED_SIMILARITY:
                    self.add_generalized_rule(relations_rule[0], direction)
                    self.add_generalized_rule(base_rule, direction)
                elif similarity_vector.primary_similarity_type == constants.IP_BASED_SIMILARITY and domain_based_similarity_existence:
                    self.add_generalized_rule(relations_rule[0],direction)
                elif similarity_vector.primary_similarity_type == constants.IP_BASED_SIMILARITY:
                    self.add_generalized_rule(relations_rule[0], direction)
                    self.add_generalized_rule(base_rule, direction)
                elif similarity_vector.primary_similarity_type == constants.DOMAIN_BASED_SIMILARITY:
                    if constants.PORT_PROTOCOL_BASED_SIMILARITY in similarity_vector.get_all_vector_similarity_types():
                        new_rule = copy.deepcopy(rule)
                        generalized_domain = base_rule.get_generalized_domain() # TODO: been tired
                        new_rule.set_dns_to_generalized_domain(generalized_domain) # set the new domain
                        self.add_generalized_rule(new_rule, direction)
                    else:
                        new_rule1 = copy.deepcopy(rule)
                        new_rule2 = copy.deepcopy(base_rule)
                        generalized_domain = base_rule.get_generalized_domain() # TODO: been tired
                        new_rule1.set_dns_to_generalized_domain(generalized_domain)  # set the new domain
                        new_rule2.set_dns_to_generalized_domain(generalized_domain)  # set the new domain
                        self.add_generalized_rule(new_rule1, direction)
                        self.add_generalized_rule(new_rule2, direction)


    def check_domain_based_similarity_existence(self, relations_rules):
        for relations_rule in relations_rules:
            similarity_vector = relations_rule[1]
            if constants.DOMAIN_BASED_SIMILARITY in similarity_vector.get_all_vector_similarity_types():
                return True

    def add_generalized_rule(self, rule, direction):
        if direction == "from":
            self.add_generalized_rule_logic(rule, self.generalized_from_rules)
        else:
            self.add_generalized_rule_logic(rule, self.generalized_to_rules)

    def add_generalized_rule_logic(self, new_rule, rules):
        for rule in rules:
            if new_rule.compare(rule) and not rule.compare(new_rule):
                # take out rule and add new_rule instead
                rules.remove(rule)
                rules.append(new_rule)
                return
            elif new_rule.compare(rule) and rule.compare(new_rule):
                # do nothing its the same rule
                return
            elif not new_rule.compare(rule) and rule.compare(new_rule):
                # do nothing / add nothing
                return
            '''
            elif not new_rule.compare(rule) and not rule.compare(new_rule):
                # its a new rule so you can add it
                rules.append(new_rule)
                return
            '''
        rules.append(new_rule)
