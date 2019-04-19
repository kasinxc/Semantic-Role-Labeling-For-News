from coref_config import *

class dataPoint:
    def get_topic(self):
        probs = self.topic_prob[1:-1] # remove [ and ] in the beginning and end
        probs = probs.split(',')
        max_prob = -1.0
        if len(probs) != title_num:
            print("Input probabilities do not match with configed title number!")
        for i in range(len(probs)):
            prob = probs[i]
            if ' ' in prob:
                prob = prob.replace(' ', '')
            prob = float(prob)
            if max_prob < prob:
                max_prob = prob
                self.topic_order = i
        return self.topic_order

    def __init__(self, td, ai, tp):
        self.title_desc = td
        self.article_ids = ai
        self.topic_prob = tp

        self.topic_order = self.get_topic()
        self.words_count = dict()
        self.verbs = list() # list of labelInfos
        self.reduced_title_desc = td
        while '  ' in self.reduced_title_desc:
            self.reduced_title_desc = self.reduced_title_desc.replace('  ', ' ')



input_data_points = list()

# input dataset
def getTopicInfo():
    topic_lines = list()
    for i in range(title_num):
        topic_lines.append(0)
    for dp in input_data_points:
        topic_lines[dp.topic_order]+=1

    for i in range(title_num):
        print("There are " + str(topic_lines[i]) + " lines for topic: " + str(i))

def readFile(file_path):
    print("reading file from path: " + file_path)
    with open(file_path, 'r') as f:
        line_index = 1
        for line in f.readlines():
            line_index += 1
            tmp = line.strip('\n').split('\t')
            dp = dataPoint(tmp[0], tmp[1], tmp[2])
            input_data_points.append(dp)
    
    getTopicInfo()
    print("successfully read the file")
    print("total lines: " + str(len(input_data_points)))