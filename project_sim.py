from universal_sentence_vectorizer import ContentVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tf_idf_vectorizer import tf_idf_model
import pandas as pd
import json
from sqlalchemy import create_engine


class project_sim(object):
    def __init__(self):
        with open('project_list.json') as json_file:
            project_list = json.load(json_file)
        with open('project_features.json') as json_file:
            temp_project_dic = json.load(json_file)
        project_features = pd.DataFrame(temp_project_dic)   
        self.embeddingmodel = ContentVectorizer()
        self.tf_idfmodel = tf_idf_model()
        self.tf_idfmodel.pca()
        
    def tf_idf_embedding(self, pid):
        return self.tf_idfmodel.embedding[str(pid)]
        
    def embedding(self, pid):
        with open('project_features.json') as json_file:
            temp_project_dic = json.load(json_file)
        project_features = pd.DataFrame(temp_project_dic)      
        return self.embeddingmodel.encode_content(project_features[project_features['index']==pid][['title','description']].to_dict('records')[0])
    
    def cossin_similarity(self, vec1, vec2):
        return cosine_similarity([vec1, vec2])[0][1] * 100

    def generate_project_simlarity(self):
        with open('project_list.json') as json_file:
            project_list = json.load(json_file)
        with open('project_features.json') as json_file:
            temp_project_dic = json.load(json_file)
        project_features = pd.DataFrame(temp_project_dic)
        project_list_keylist = []
        for key in project_list.keys():
            project_list_keylist.append(int(key))
        results = []
        count = 0
        for project1 in project_list_keylist:
            encode = []
            tfidf = []
            for project2 in project_list_keylist:
                if project1 != project2:
                    encode.append({'pid':project2,'sim_score':self.cossin_similarity(self.embedding(project1),self.embedding(project2))})
                    tf_title_score = self.cossin_similarity(self.tf_idfmodel.embedding[str(project1)]['vec_title'], self.tf_idfmodel.embedding[str(project2)]['vec_title'])
                    tf_des_score = self.cossin_similarity(self.tf_idfmodel.embedding[str(project1)]['vec_des'], self.tf_idfmodel.embedding[str(project2)]['vec_des'])
                    tfidf.append({'pid':project2,'sim_score':0.7*tf_title_score+0.3*tf_des_score})
            encode = sorted(encode, key = lambda x: x['sim_score'], reverse = True)[:20]
            tfidf = sorted(tfidf, key = lambda x: x['sim_score'], reverse = True)[:20]
            for i in range(20):
                results.append({'pid':int(project1), 
                                'encode_sim':int(encode[i]['pid']),
                                'encode_sim_score': encode[i]['sim_score'],
                                'tfidf_sim':int(tfidf[i]['pid']),
                                'tfidf_sim_score': tfidf[i]['sim_score']})
            count += 1
            print (count)
        project_sim_table = pd.DataFrame(results)
        project_sim_table.to_csv('project_sim_table.csv',index=False)  
    
        return project_sim_table
    
if __name__ == '__main__':
    x = project_sim()
    sim_results = x.generate_project_simlarity()
