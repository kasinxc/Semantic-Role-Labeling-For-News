# In this file, we are going to read data from files 
# and then apply SRL to each data to get tuple results.


from allennlp.predictors.predictor import Predictor

import json
import os

from data_entry import *
from color_print import *
from srl_config import *


def read_data_entries_from_file(file_path):
    print("read data entries from file at path: " + file_path)

    # list of (the indices of skipped data and its line length)
    # the indices of data is 0-based
    # Trump data has different data format
    skip_data_indice = dict()
    # list of data entries
    input_data_entries = list()
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for data_index in range(len(lines)):
            line = lines[data_index]
 
            tmp = line.strip('\n').split('\t')
            data_entry = DataEntry(tmp[0], tmp[1], tmp[2])
            input_data_entries.append(data_entry)

            if len(tmp[0]) > line_length_threshold:
                skip_data_indice[data_index] = len(tmp[0])

    print("total data entries: " + str(len(input_data_entries)))
    print("skip data entries with line size > " + str(line_length_threshold))
    print("skipped data (data index, data length):")
    print(skip_data_indice)
    return input_data_entries, skip_data_indice

def read_data_entries_from_folder(folder_path):
    print("read data entries from folder at path: " + folder_path)

    skip_article_ids = dict()
    input_data_entries = list()

    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in files:
            if not '.' in name:
                file_path = os.path.join(root, name)
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for data_index in range(len(lines)):
                        line = lines[data_index]
                        tmp = line.strip('\n').split('\t')
                        data_entry = DataEntry(tmp[2], tmp[0], 0)
                        input_data_entries.append(data_entry)
                        
                        if len(tmp[2]) > line_length_threshold:
                            skip_article_ids[tmp[0]] = len(tmp[2])

    print("total data entries: " + str(len(input_data_entries)))
    print("skip data entries with line size > " + str(line_length_threshold))
    print("skipped data (article ids, data length):")
    print(skip_article_ids)
    return input_data_entries, skip_article_ids


class RoleInfo:
    def __init__(self, label, words):
        self.label = label
        self.words = words


def my_pretty_print(relations):
    print("These are extracted relations:")
    for relation in relations:
        for role in relation:
            print(role.label + ': ' + role.words),
        print('\n')


def get_paired_right_bracket_position(description, left_bracket_position):
    inner_left_bracket_cnt = 0
    for right_bracket_position in range(left_bracket_position+1, len(description)):
        if description[right_bracket_position] == '[':
            inner_left_bracket_cnt +=1

        if description[right_bracket_position] == ']':
            if inner_left_bracket_cnt == 0:
                return right_bracket_position

            if inner_left_bracket_cnt > 0:
                # This is a inner right bracket
                inner_left_bracket_cnt-=1

    return left_bracket_position


def has_inner_paired_brackets(description, left_position, right_position):
    stack = list()
    for index in range(left_position+1, right_position):
        if description[index] == '[':
            stack.append(index)
        if description[index] == ']':
            if not stack:
                return False
            stack.pop()
    return not stack


# brackets in label or words should be paired
def get_colon_position(description, left_bracket_position, right_bracket_position):
    # colon position is valid iff both inner brackets in label and word are paired
    # example: [ARG1: me] [ to [V: come] [ARG4: to you] [ARGM-PRP: for sex ]]
    for index in range(left_bracket_position, right_bracket_position):
        if description[index] == ':':
            if has_inner_paired_brackets(description, left_bracket_position, index) and has_inner_paired_brackets(description, index, right_bracket_position):
                return index
    return right_bracket_position


def get_relation_from_description(description):
    index = 0
    relation = list()
    ordered_roles = list()
    while index < len(description) and description[index]:
        if description[index] != '[':
            index+=1
            continue

        left_bracket_position = index
        colon_position = -1
        right_bracket_position = -1

        # the inner brackets should be paired, [[x]y] included y, [x] [y] not included y
        right_bracket_position = get_paired_right_bracket_position(description, left_bracket_position)

        if right_bracket_position == left_bracket_position:
            # There is no detected role any more 
            break

        colon_position = get_colon_position(description, left_bracket_position, right_bracket_position)
        
        if colon_position >= right_bracket_position:
            # This is not a detected role, it is in the form of [xxx]
            index = left_bracket_position+1
            continue

        # must be in the form of [xx: yy]
        words = description[colon_position+2:right_bracket_position] # space [label: words]
        label = description[left_bracket_position+1: colon_position]

        # print("label =", label),
        # print("words =", words)
        ordered_roles.append(RoleInfo(label, words))

        # right_bracket+1 is because "... [V: bbb] haha" => "... [V: bbb haha" 
        description = description[:right_bracket_position] + description[right_bracket_position+1:]
        # colon+2 is because "... [V: bbb haha" => "... bbb haha"
        description = description[:left_bracket_position] + description[colon_position+2:]
        # not deleting the space before "bbb" may result in multispace
        description = description.replace('  ', ' ')
        
        index = left_bracket_position+1

    for role_info in ordered_roles:
        if role_info.label == 'V':
            relation.append(role_info)

    for role_info in ordered_roles:
        if role_info.label != 'V':
            relation.append(role_info)

    return relation


# a relation list is defined as
# [Verb of RoleInfo, Other Type of RoleInfo, Other Type of RoleInfo, ...]
def get_relation_tuples(srls):
    relations = list()
    for data_index, srl in srls.items():
        if not srl['verbs']:
            continue
        for verb_description in srl['verbs']:
            description = verb_description['description']
            relation = get_relation_from_description(description)
            relations.append(relation)
    return relations


def load_srls_from_file(folder_path):
    print(UseStyle("Detected SRLs in folder: " + folder_path, fore='green'))
    print("Loading from files ...")
    srls = dict()
    file_count = 0
    files = list()
    for file_name in os.listdir(folder_path):
        if not '.json' in file_name:
            continue
        else:
            with open(folder_path+str(file_name), 'r') as f:
                srl = json.load(f)
                data_index = int(file_name.split('.')[0])
                srls[data_index] = srl
                file_count+=1
                files.append(file_name)
                if file_count >= max_file_number:
                    break
    print("Srls number: " + str(len(srls)))
    print (UseStyle("Load success", fore='green'))
    return srls


def applyAllenToDE(input_data_entries, skip_data_indice, srl_result_folder_path):

    srls = dict()
    # Already run before and a command saying do not predict explicitly -> load from file
    if os.path.exists(srl_result_folder_path) and os.listdir(srl_result_folder_path) and flag_predict_srl_on_file == False:
        # max_file_number in the following function
        srls = load_srls_from_file(srl_result_folder_path)
        return srls

    if not os.path.exists(srl_result_folder_path):
        os.makedirs(srl_result_folder_path)
        print("SRL result folder not exists, create one: " + srl_result_folder_path)
    elif not os.listdir(srl_result_folder_path):
        print("SRLs not detected in folder: " + srl_result_folder_path)

    print("Predicting using allennlp srl...")
    # load predictor    
    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz")

    file_count = 0
    files = list()
    for data_index in range(len(input_data_entries)):
        de = input_data_entries[data_index]
        if de.article_ids in skip_data_indice:
            continue
        if data_index % 100 == 0:
            print("Predicting index = " + str(data_index))
        srl = predictor.predict(sentence=input_data_entries[data_index].title_desc)
        
        # save to file, 0-base
        with open(srl_result_folder_path + str(de.article_ids) + ".json", 'w') as f:
            json.dump(srl, f)

        srls[data_index] = srl
        file_count+=1
        files.append(str(data_index) + ".json")
        if file_count >= max_file_number:
            return srls
    print (UseStyle("Predict success", fore='green'))
    return srls


# API for visualization use
def get_relations_api(max_file_count=30000):
    global max_file_number
    max_file_number = max_file_count
    if use_steplines_format == False:
        input_data_entries, skip_data_indice = read_data_entries_from_file(input_data_file_path)
    else:
        input_data_entries, skip_data_indice = read_data_entries_from_folder(input_data_file_path)
    srls = applyAllenToDE(input_data_entries, skip_data_indice, srl_result_folder_path)
    relations = get_relation_tuples(srls)
    return relations


def main():
    if use_steplines_format == False:
        input_data_entries, skip_data_indice = read_data_entries_from_file(input_data_file_path)
    else:
        input_data_entries, skip_data_indice = read_data_entries_from_folder(input_data_file_path)

    srls = applyAllenToDE(input_data_entries, skip_data_indice, srl_result_folder_path)
    relations = get_relation_tuples(srls)
    print(UseStyle("Relations extraction finished", fore = 'green'))
    my_pretty_print(relations)


if __name__ == '__main__':
    main()