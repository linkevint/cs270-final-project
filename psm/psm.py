from owlready2 import *

onto = get_ontology('file://../ontology/restaurants.owl').load()
print(onto.Business)
