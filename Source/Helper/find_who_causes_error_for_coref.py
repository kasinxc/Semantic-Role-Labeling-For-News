import os
import string

result_folder_path = '../../Result/COREF/Allennlp_Coref/'
input_data_folder_path = '../../Data/6_month/prod20181107_scheduled20181107t013500/StepLines__nocontent_title_desc/'


def have_punctuation(input_data):
    punctuations = string.punctuation
    for p in punctuations:
        if p in input_data:
            return True
    return False


def find_skip_article_ids():
    skip_article_ids = set()
    for root, dirs, files in os.walk(input_data_folder_path, topdown=False):
        for name in files:
            if '.' in name:
                continue
            with open(input_data_folder_path + name, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip('\n').split('\t')
                    ai = line[0]
                    td = line[2]
                    if not have_punctuation(td):
                        skip_article_ids.add(int(ai))
    return skip_article_ids

def find_result_article_ids():
    article_ids = set()
    for root, dirs, files in os.walk(result_folder_path, topdown=False):
        for name in files:
            if not '.json' in name:
                continue
            name = name.split('.')
            article_id = int(name[0])
            article_ids.add(article_id)
    return article_ids

def find_who_causes_error():
    skip_article_ids = find_skip_article_ids()
    article_ids = find_result_article_ids()

    for file_id in range(1, 109):
        min_article_id = (file_id-1) * 5000
        has_one_processed = False
        potential_error = set()
        for article_id in range(min_article_id, min_article_id + 5000):
            if article_id in skip_article_ids:
                continue
            if article_id in article_ids:
                has_one_processed = True
            else:
                potential_error.add(article_id)

        if has_one_processed and not potential_error:
            print(str(file_id) + "processed")
        if has_one_processed and potential_error:
            print("potential_error in file " + str(int(min_article_id / 5000 + 1)))

            print(min(potential_error))


        

    # while article_ids:
    #     min_id = min(article_ids)
    #     print(min_id)
    #     find = False
    #     for i in range(min_id, min_id+5000):
    #         if i in article_ids:
    #             article_ids.remove(i)
    #         else:
    #             if i in skip_article_ids:
    #                 continue
    #             else:
    #                 print(str(i) + " not in set")
    #                 # print(article_ids)
    #                 find = True
    #                 break
    #     if find:
    #         break

find_who_causes_error()
