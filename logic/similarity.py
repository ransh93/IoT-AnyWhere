import logic.constants as constants

class similarity_component():
    def __init__(self, match_type, is_similar,similarity_score, similarity_type):
        self.match_type = match_type
        self.is_similar = is_similar
        self. similarity_score = similarity_score
        self.similarity_type = similarity_type
        pass


class similarity_vector():
    def __init__(self):
        self.similarity_components = []
        self.primary_similarity_type = None  # Domain_based is the important one
        self.is_vector_similar = False  # does one of the components is True

    def add_component(self, similarity_comp):
        self.similarity_components.append(similarity_comp)

    def determine_vector_similarity_status(self):
        for sim_component in self.similarity_components:
            if sim_component.is_similar and sim_component.similarity_type == constants.DOMAIN_BASED_SIMILARITY:
                self.is_vector_similar = True
                self.primary_similarity_type = constants.DOMAIN_BASED_SIMILARITY
                break
            elif sim_component.is_similar and sim_component.similarity_type == constants.IP_BASED_SIMILARITY:
                self.is_vector_similar = True
                self.primary_similarity_type = constants.IP_BASED_SIMILARITY
                break
            elif sim_component.is_similar:
                self.is_vector_similar = True
                self.primary_similarity_type = sim_component.similarity_type

