# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 10:23:33 2020

@author: jidong 

Edited by Vincent Chen, Mon Apr 26

Changes:

Generate a recom_score for all projects based on views and similarities


"""



import time
import pandas as pd
import pickle
import paramiko
import pymysql
import json




class project_recom(object):
    def __init__(self):
        with open('project_dict_view.json') as json_file:
          self.project_dict = json.load(json_file)
 #      self.project_dict = load_sim_table_from_MySQL()[0]
        self.click_table = pd.read_csv('top_click_all.csv')
        self.user_sim_table = pd.read_csv('user_sim_table.csv')
        self.project_sim_table = pd.read_csv('project_sim_table.csv')
        self.upload_project = pd.read_csv('upload_project.csv')
        self.user_list = list(set(self.user_sim_table['user_id'].tolist()))
 #       self.user_list = load_user_list()

    def recom_score(self, uid, project_id):
        view_score = self.project_dict[str(project_id)]
        encode_score = 0
        history = self.get_project_num(self.click_table[self.click_table['uid']==uid])
        history.extend(self.upload_project[self.upload_project['publisher_id']==uid]['project_id'].values) #add uploaded project num
        if len(history) != 0:
            sim_score_data=pd.DataFrame(None)
            for project in history:
                #switch, search for project most similar to project_id
                sim_score_temp = self.project_sim_table[(self.project_sim_table['pid']==int(project))&(self.project_sim_table['encode_sim']==project_id)]
                sim_score_data = pd.concat([sim_score_data,sim_score_temp])
                sim_score_temp_2 = self.project_sim_table[(self.project_sim_table['pid']==int(project_id))&(self.project_sim_table['encode_sim']==project)]
                sim_score_data = pd.concat([sim_score_data,sim_score_temp])
            if len(sim_score_data)>0:
                encode_score = float(sim_score_data.sort_values(by='encode_sim_score', ascending=False)['encode_sim_score'].values[0])/100
        
        total_score = float(view_score)*0.5 + float(encode_score)*0.5
        return total_score

    def get_userbased_project_list(self, uid, n_near, m_recent):
        sim_user_list = self.user_sim_table[self.user_sim_table['user_id']==uid]['sim_user'][0:n_near]
        project_list = []
        if len(sim_user_list) != 0:
            for sim_user in sim_user_list:
                project_list.extend(self.get_project_num(self.click_table[self.click_table['uid']==sim_user])[:m_recent])
        
        project_list = list(set(project_list))
        return project_list
    
    def get_contentbased_project_list(self, uid, n_near, m_recent):
        history = self.get_project_num(self.click_table[self.click_table['uid']==uid])[:m_recent]
        history.extend(self.upload_project[self.upload_project['publisher_id']==uid]['project_id'].values) #add uploaded project num
        project_list = []
        if len(history) != 0:
            for pid in history:
                project_list.extend(self.project_sim_table[self.project_sim_table['pid']==int(pid)]['encode_sim'][0:n_near])
                
        
        project_list = list(set(project_list))
        return project_list
                
    
 
    def update_single_user(self, uid):
        usr_project_list = self.get_userbased_project_list(uid, 9, 9)
        cont_project_list = self.get_contentbased_project_list(uid, 9, 9)
        project_list = list(set(usr_project_list+cont_project_list))
        project_recom_df = pd.DataFrame(None)
        if len(project_list)!=0:
            project_recom_list = []
            for elem in project_list:
                if str(elem) in list(self.project_dict): #make sure they are in the project table
                    project_recom_list.append({'user': uid, 'project': elem,'rec_score':self.recom_score(uid,elem) })
            project_recom_df = pd.DataFrame(project_recom_list)
            if len(project_recom_df)>0: #in case there are no projects applicable
                project_recom_df = project_recom_df.sort_values(by='rec_score',ascending=False)
            project_recom_df = project_recom_df.reset_index(drop=True)
        return project_recom_df    

    def update_all_user(self):
        project_rec_table = pd.DataFrame(None)
        for uid in self.user_list:
            project_rec_temp = self.update_single_user(uid)
            print(uid)
            project_rec_table = pd.concat([project_rec_table, project_rec_temp], ignore_index=True)
        return project_rec_table


    def get_project_num(self,data):
        num_list = []
        if len(data)==0:
            return num_list   
        clean_data = data['node'].values[0].replace('[','').replace(']','').replace("'","")
        if len(clean_data)==0:
            return num_list
        for node in clean_data.split(','):
            num_list.append(node.split('/')[-1])
        return num_list
    
    
    def final_result(self,project_recom_user,non_empty_user):
        import random
        project_dict_view = project_recom_user.project_dict
        project_dict_view = (sorted(project_dict_view.items(), key=lambda item: item[1], reverse=True))
        pop_list = []
        project_dic = project_recom_user.project_dict
        for i in range(10):
          pop_list.append(int(project_dict_view[i][0]))
        non_empty_list = non_empty_user['user'].tolist()
        user_sim_table = pd.read_csv('user_sim_table.csv')
        user_list = list(set(user_sim_table['user_id'].tolist()))
        gen_recom_list = []
        for i in range (len(user_list)):
          if user_list[i] not in  non_empty_list:
            random_list = random.sample(pop_list, 5)
            for j in range (5):
              gen_recom = []
              gen_recom.append(user_list[i])
              gen_recom.append(random_list[j])
              gen_recom.append(0.5*project_dic[str(random_list[j])])
              gen_recom_list.append(gen_recom)
        recom_list = non_empty_user.values.tolist()
        from pandas.core import missing
        from collections import Counter
        recom_list_exist = []
        for i in range (len(recom_list)):
          recom_list_exist.append(recom_list[i][0])
        count_recom = dict(Counter(recom_list_exist))
        missing_dic = {}
        for item in count_recom.keys():
          if count_recom[item] < 5:
            missing_dic[item] = 5-count_recom[item]
        missing_list = list(map(list, missing_dic.items()))
        recom_fill = []
        for i in range (len(missing_list)):
          for j in range (missing_list[i][1]):
              random_list = random.sample(pop_list, missing_list[i][1])
              gen_recom = []
              gen_recom.append(missing_list[i][0])
              gen_recom.append(random_list[j])
              gen_recom.append(0.5*project_dic[str(random_list[j])])
              recom_fill.append(gen_recom)  
        total_list = recom_list + gen_recom_list + recom_fill
        recom_df_total = pd.DataFrame(sorted(total_list, key=lambda x: x[0]))
        recom_df_total.columns = ['user','project','recom_score']  
        recom_df_total = recom_df_total.sort_values(by=['user', 'recom_score'], ascending = [True, False])
        recom_df_total = recom_df_total[['user','project','recom_score']]
        recom_df_total.to_csv('recommendation.csv',index = False)
        return recom_df_total

if __name__ == '__main__':
    project_recom_user = project_recom()
    non_empty_user = project_recom_user.update_all_user()    #recom = x.update_whole_table()
    start = time.time()
 #   recom = x.update_single_user(488)
    #print (time.time()-start)
    outcome = project_recom_user.final_result(project_recom_user,non_empty_user)
