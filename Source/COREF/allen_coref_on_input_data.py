# allennlp
from allennlp.predictors.predictor import Predictor
from tqdm import tqdm
import json
import os

from utils import *
from coref_config import *


def loadCorefPredictor():
    print("loading predictor...")
    predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/coref-model-2018.02.05.tar.gz")
    print("successfully loaded the predictor")
    return predictor


# Output Tmp Files
def applyAllenToDP():
    global data_low_index, data_high_index

    predictor = loadCorefPredictor()

    if not os.path.exists(coref_result_file_path):
        os.makedirs(coref_result_file_path)
    
    pbar = tqdm(range(data_low_index, data_high_index)) # process bar

    for index in range(data_low_index, data_high_index):
        if (index+1) in end_error_indice:
            pbar.update(1)
            continue

        pbar.update(1)

        with open(coref_result_file_path + str(index+1) + ".json", 'w') as f:

            srl = predictor.predict(document=input_data_points[index].reduced_title_desc)
            json.dump(srl, f)
    pbar.close()

if __name__ == '__main__':
    global input_data_file_path
    readFile(input_data_file_path)
    applyAllenToDP()
