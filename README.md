# Project Recommender of RMDS LAB
RMDS Lab is aiming to make its work more public to let data scientists enjoy the charm in algorithms. This is one of its open-source projects, project recommender, which
is deployed on the [RMDS LAB](https://grmds.org).

## Introduction
RMDS wants to recommend RMDS projects to RMDS users customly based on project similarity and popularity. We would calculate out a recommendation score for each project and recommend those projects with high recommendation scores to user. For public demonstration purpose, this project used generated data instead of read data. The process of fake data generation data is included as well.

The Project Recommender consists data generation, project similarity calculation and project recommendation.
1.	project_mask.py
•	generate fake projects using aitextgen
•	input: NA(trained models)
•	output: JSON format of list of projects and JSON format of project’s title and description
2.	project_sim.py
•	calculate project similarity and for each project pick 20 most similar projects
•	input: project descriptions
•	output: csv format of project with their most similar projects and score
3.	tf_idf_vectorizer.py
•	ti_idf+pca method for text embedding
•	input: single document or text
•	output: dense vector of text (after pca to 50 dimension)
4.	universal_sentence_vectorizer.py
•	doc2vec method for text embedding
•	input: single document or text
•	output: dense vector of text (make sure to download pre-trained model)
5.	data_mask.py(optional)
•	generate necessary data to simulate user behavior and project view history. To project user privacy, the origin data is not provided, the file is demonstration purpose only.
•	input: project list and project descriptions
•	output: csv format of project upload history, csv format of user similarity table, csv format of click history and JSON format of project popularity score
6.	project_recom.py
•	recommend 5 projects to each user based on user similarity and project similarity
•	input: project list, user behavior history and project view history
•	output: csv format of recommendation for each user
7.	project_recom_with_fake_data.ipynb
This is a Jupyter notebook of the complete process of the recommendation system(except project mask). It could be used as an overview of the project.


## Requirements of development environment
- pyjarowinkler 1.8
- scikit-learn 0.24.0
## License
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-green.svg)](https://www.gnu.org/licenses/agpl-3.0)
