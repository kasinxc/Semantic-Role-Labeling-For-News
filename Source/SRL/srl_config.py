# common

max_file_number = 30000 # used by srl_visualization and relation_extraction

# srl_visualization
min_verb_count_to_draw = 5
max_verb_count_to_draw = 500
min_verb_other_roles_count_to_draw = 2
max_verb_other_roles_count_to_draw = 500
max_length_of_role = 50
top_ranking_verbs = 5
enable_coreference_resolution = True
coref_read_from_correct_file = True
role_of_interest = ['Donald Trump']

# relation_extraction
input_data_file_path = '../../Data/trump_prob'
srl_result_folder_path = '../../Result/SRL/Allennlp_Srl/'
# Data with lines number larger than 4000 is more likely to fail the SRL processing
line_length_threshold = 4000 
flag_predict_srl_on_file = False

