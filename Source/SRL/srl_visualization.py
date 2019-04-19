from graphviz import Digraph

import operator
import sys
sys.path.append('../COREF/')

from coref_visualization import *
from relation_extraction import *
from srl_config import *


# The structure of the relations
# relations = list of relation
# relation = list of role
# role = Class of RoleInfo

# Function: remove_invalid_relations
# 1. remove only verb
# 2. remove non-verb whose length longer than max_length_of_role
def remove_invalid_relations(relations):

    new_relations = list()
    for relation in relations:
        
        new_relation = list()
        for role in relation:
            if role.label == 'V':
                new_relation.append(role)
            elif len(role.words) <= max_length_of_role:
                new_relation.append(role)

        if len(new_relation) > 1:
            new_relations.append(new_relation)
    print(UseStyle('Removed ' + str(len(relations)-len(new_relations)) + ' invalid relations', fore='white'))
    print(UseStyle('Remaining relations number:' + str(len(new_relations)), fore='green'))
    return new_relations


def get_role_to_relations_of_interest_mappings(role_of_interest, relations):

    new_relations = dict()

    for relation in relations:
        is_interested = False
        interested_role_words = str()
        for role in relation:
            if role.label == 'ARG0' and role.words in role_of_interest:
                is_interested = True
                interested_role_words = role.words
                break
        if is_interested:
            if not interested_role_words in new_relations:
                new_relations[interested_role_words] = list()
            new_relations[interested_role_words].append(relation)
    return new_relations


def tree(relations):
    role_to_relations_of_interest_mappings = get_role_to_relations_of_interest_mappings(role_of_interest, relations)

    tree_graph = Digraph(format='png')
    tree_graph.clear()
    tree_graph.attr(rankdir='LR')
    for interested_role_name, relations_of_interest in role_to_relations_of_interest_mappings.items():
        
        print(UseStyle("add interested node: " + interested_role_name, fore='green'))
        verb_counts = dict()
        verb_to_other_roles_mappings = dict()

        other_labels = set() # record ARG-TMP and other labels
        for relation in relations_of_interest:
            other_roles = list()
            for role in relation:
                if role.label == 'V':
                    verb_role = role
                elif role.label == 'ARG1':
                    other_roles.append(role.words)
                else:
                    other_labels.add(role.label)

            if not verb_role.words in verb_counts:
                verb_counts[verb_role.words] = 1
            else:
                verb_counts[verb_role.words] += 1
            if not verb_role.words in verb_to_other_roles_mappings:
                verb_to_other_roles_mappings[verb_role.words] = dict()
            for other_role_words in other_roles:
                if not other_role_words in verb_to_other_roles_mappings[verb_role.words]:
                    verb_to_other_roles_mappings[verb_role.words][other_role_words] = 1
                else:
                    verb_to_other_roles_mappings[verb_role.words][other_role_words] += 1

        sorted_verb_counts = sorted(verb_counts.items(), key=lambda kv: kv[1], reverse=True)

        drew_verbs = set()
        for (verb_words, count) in sorted_verb_counts:
            verb_name = interested_role_name + '.' + verb_words
            if count >= min_verb_count_to_draw and count <= max_verb_count_to_draw:
                can_draw=False
                
                for other_role_words, other_role_count in verb_to_other_roles_mappings[verb_words].items():
                    if other_role_count >= min_verb_other_roles_count_to_draw and other_role_count <= max_verb_other_roles_count_to_draw:
                        can_draw=True
                        break

                if can_draw:
                    tree_graph.node(interested_role_name, interested_role_name, color='red')
                    tree_graph.node(verb_name, verb_words)
                    tree_graph.edge(interested_role_name, verb_name, label=str(count))
                    drew_verbs.add(verb_words)
                    if len(drew_verbs) >= top_ranking_verbs:
                        break

        for verb_words, other_roles_count in verb_to_other_roles_mappings.items():
            if not verb_words in drew_verbs:
                continue
            verb_name = interested_role_name + '.' + verb_words
            for other_role_words, count in other_roles_count.items():
                other_role_name = verb_name + '.' + other_role_words
                if count >= min_verb_other_roles_count_to_draw and count <= max_verb_other_roles_count_to_draw:
                    tree_graph.node(other_role_name, other_role_words)
                    tree_graph.edge(verb_name, other_role_name, label=str(count))

    return tree_graph


def get_lower(role_of_interest):
    lower_case_role_of_interest = list()
    for role in role_of_interest:
        lower_case_role_of_interest.append(role.lower())
    return lower_case_role_of_interest


def load_configurations(configurations):
    global role_of_interest,min_verb_count_to_draw, min_verb_other_roles_count_to_draw, max_verb_count_to_draw, max_verb_other_roles_count_to_draw
    global max_file_number, top_ranking_verbs, max_length_of_role, enable_coreference_resolution, coref_read_from_correct_file
    for configuration in configurations:
        label = configuration[0]
        content = configuration[1]
        if label == 'interested_roles':
            role_of_interest = content
        if label == 'min_count_to_draw':
            min_verb_count_to_draw = content
            min_verb_other_roles_count_to_draw = content
        if label == 'max_count_to_draw':
            max_verb_count_to_draw = content
            max_verb_other_roles_count_to_draw = content
        if label == 'max_file_number':
            max_file_number = content
        if label == 'top_ranking_verbs':
            top_ranking_verbs = content
        if label == 'max_length_of_role':
            max_length_of_role = content
        if label == 'enable_coreference_resolution':
            enable_coreference_resolution = content
        if label == 'coref_read_from_correct_file':
            coref_read_from_correct_file = content

    if enable_coreference_resolution == True:
        clusters = get_clusters(coref_read_from_correct_file)
        lower_case_role_of_interest = get_lower(role_of_interest) 
        for cluster in clusters:
            role_in_cluster = False
            for word in cluster:
                if word.lower() in lower_case_role_of_interest:
                    role_in_cluster = True
                    break
            if role_in_cluster == True:
                for role in cluster:
                    if not role in role_of_interest:
                        role_of_interest.append(role)

        print(role_of_interest)


# use when querying what search options we have
def show_all_arg0(relations):
    arg0 = set()
    for relation in relations:
        for role in relation:
            if role.label == 'ARG0':
                arg0.add(role.words)
    print(arg0)


def main(configurations):
    load_configurations(configurations)
    relations = get_relations_api(max_file_number)

    print(UseStyle('Loaded ' + str(len(relations)) +' relations from file', fore='green'))
    relations = remove_invalid_relations(relations)
    tree_graph = tree(relations)
    print(UseStyle('Finish', fore='green'))
    return tree_graph


if __name__ == '__main__':
    configuration = list()
    tree_graph = main(configuration)
    tree_graph.view()
