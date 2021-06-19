class MudGeneralization(object):
    def __init__(self, identical_rules, first_non_similar_from_rules, first_non_similar_to_rules,
                 second_non_similar_from_rules, second_non_similar_to_rules, generalized_from_rules, generalized_to_rules):
        self.identical_from_rules = []
        self.identical_to_rules = []
        self.non_similar_from_rules = []
        self.non_similar_to_rules = []
        self.generalized_from_rules = []
        self.generalized_to_rules = []

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
        self.create_generalized_rules(generalized_from_rules)
        self.create_generalized_rules(generalized_to_rules)

        # TODO: make a list of all similarities based so it will be easier to test if we have both domain and protocol+port similarity (in similarity)
        # TODO: we have a problem when a rule is also domain similar to something and also protocol+port similar

    def create_generalized_rules(self, generalized_from_rules):
        pass


