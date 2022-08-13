import pandas as pd
from aitextgen.TokenDataset import TokenDataset
from aitextgen.tokenizers import train_tokenizer
from aitextgen.utils import GPT2ConfigCPU
from aitextgen import aitextgen
#from faker import Faker
from random import shuffle, sample, randint, random
import ast
import re
import json

def project_feature_extractor():
    file_name = "dataset_des.txt"

    # Train a custom BPE Tokenizer on the downloaded text
    # This will save one file: `aitextgen.tokenizer.json`, which contains the
    # information needed to rebuild the tokenizer.
    train_tokenizer(file_name)

    tokenizer_file = "aitextgen.tokenizer.json"

    # GPT2ConfigCPU is a mini variant of GPT-2 optimized for CPU-training
    # e.g. the # of input tokens here is 64 vs. 1024 for base GPT-2.
    config = GPT2ConfigCPU()

    # Instantiate aitextgen using the created tokenizer and config
  #  self.ai_text = aitextgen(model_folder="trained_model", tokenizer_file="aitextgen.tokenizer.json")
    ai = aitextgen(model_folder="trained_model", tokenizer_file=tokenizer_file, config=config)

    # You can build datasets for training by creating TokenDatasets,
    # which automatically processes the dataset with the appropriate size.
    data = TokenDataset(file_name, tokenizer_file=tokenizer_file, block_size=64)

    # Train the model! It will save pytorch_model.bin periodically and after completion to the `trained_model` folder.
    # On a 2020 8-core iMac, this took ~25 minutes to run.
    ai.train(data, batch_size=8, num_steps=500000, generate_every=5000, save_every=5000)

    project_list_index = []
    project_list_title = []
    project_list_des = []
    for i in range (200):
        index = randint(0,2000)
        title = ai.generate(1,max_length = 15,return_as_list=True)[0]
        des = ai.generate(1,max_length = 150,return_as_list=True)[0]
        project_list_index.append(index)
        project_list_title.append(title)
        project_list_des.append(des)
    temp_project_dic = {'index': project_list_index, 'title': project_list_title, 'description': project_list_des}
    project_features = pd.DataFrame(temp_project_dic)        
    project_tf = []
    for i in range (len(project_list_des)):
        project_tf.append("True")
    project_list = dict(zip(project_list_index, project_tf))
    project_list_json = json.dumps(project_list)
    f = open("project_list.json","w")
    f.write(project_list_json)
    f.close()

    project_features_json = json.dumps(temp_project_dic)
    e = open("project_features.json","w")
    e.write(project_features_json)
    e.close()
    print(project_features)    
    return project_list, project_features

if __name__ == '__main__': 
	project_list, project_features = project_feature_extractor()