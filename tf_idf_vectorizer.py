# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 02:26:59 2020

@author: jidong
"""

from sklearn.feature_extraction.text import TfidfVectorizer
#from project_mask import project_feature_extractor
from sklearn.decomposition import TruncatedSVD
import json
import pandas as pd


class tf_idf_model(object):
    def __init__(self):
        vectorizer = TfidfVectorizer(max_df = 50)
        whole_doc = self.collect_doc()
        self.title_matrix = vectorizer.fit_transform(whole_doc[0])
        self.des_matrix = vectorizer.fit_transform(whole_doc[1])
        self.embedding = {}
        self.pca()

    def collect_doc(self):
        with open('project_list.json') as json_file:
            project_list = json.load(json_file)
        with open('project_features.json') as json_file:
            temp_project_dic = json.load(json_file)
        project_features = pd.DataFrame(temp_project_dic)  
        title_document = []
        description_document = []
        for title, row in project_features.iterrows():
            if row['title'] != None:
                title_document.append(row['title'])
            else:
                title_document.append('')
            if row['description'] != None:
                description_document.append(row['description'])
            else:
                description_document.append('')
        return title_document, description_document
    
    def pca(self):
        with open('project_list.json') as json_file:
            project_list = json.load(json_file)
        with open('project_features.json') as json_file:
            temp_project_dic = json.load(json_file)
        project_features = pd.DataFrame(temp_project_dic)          
        pca = TruncatedSVD(n_components = 50)
        title_matrix = pca.fit_transform(self.title_matrix)
        des_matrix = pca.fit_transform(self.des_matrix)
        
        project_list_key = list(project_list.keys())
        for i in range(len(project_list_key)):
            self.embedding[project_list_key[i]] = {'vec_title': title_matrix[i], 'vec_des':des_matrix[i]}

        return
            
        
    
        
if __name__ == "__main__":
    x = tf_idf_model()
    x.pca() 
                
        