from bs4 import BeautifulSoup
import requests
import io 
import nltk
from nltk.corpus import stopwords 
import csv 
import re
import numpy as np
from nltk import bigrams
import itertools
import pandas as pd
import os
import re
from nb import nb_func
from sklearn.feature_extraction.text import CountVectorizer
from nltk.tokenize import word_tokenize
import pickle



def reporter_list_func(list_change):

	reporter_list = []

	counter = 0;
	for x in list_change:	
		if (x.find(class_="comment")):
			counter = counter+1
			comment = x.find(class_="comment")
			if(comment.find(class_="layout-table change-head reporter")):
				if(x.find(class_="comment-text")):
					reporter_list.append(x.find(class_="comment-text"))

			else:
				break
	
	# print (type(reporter_list[0])) = <class 'bs4.element.Tag'>

	paragraphs = remove_stop_words(reporter_list)
				
	# print (paragraphs)
	return paragraphs



def remove_stop_words(alist):
	
	stop_words = set(stopwords.words('english')) 

	bad_chars = [';', ':', '!', "*", "(", ")", "[", "]", "{", "}", ".", ",", "``", "''", '""', "?", "/","_",
	"+", "--", "``", "'", "-", ">", "<", "!","@","#","$","%","^","&","*","|","=","`","~","'", 'pre', 'div',
	'<pre','<a>','<p>']

	filtered_string = ''
	filtered_list = [] 

	for x in alist:
		if(x):
			temp = x.get_text()
		else:
			temp = ''

		

		temp = re.sub(r'[0-9]+', '', temp)
		temp = re.sub(r"\b[a-zA-Z]\b", "", temp)

		for i in bad_chars: 
			temp = temp.replace(i, '')

		
		filtered_string = filtered_string + temp
		

	# str1 = ''.join(filtered_list)
	# return str1

	filtered_list.append(filtered_string)
	return filtered_list			




def nb(rows, columns):

	training_data = pd.DataFrame(rows, columns=columns)
	# print(training_data)


	# Term-Document Matrix
	stmt_docs = [row['sent'] for index,row in training_data.iterrows() if row['class'] == 'good']

	vec_s = CountVectorizer()
	X_s = vec_s.fit_transform(stmt_docs)
	tdm_s = pd.DataFrame(X_s.toarray(), columns=vec_s.get_feature_names())
	# print(tdm_s)

	# path = os.getcwd()
	# completeName = os.path.join(path, "matrix.xlsx") 
	# tdm_s.to_excel(completeName)


	q_docs = [row['sent'] for index,row in training_data.iterrows() if row['class'] == 'bad']

	vec_q = CountVectorizer()
	X_q = vec_q.fit_transform(q_docs)
	tdm_q = pd.DataFrame(X_q.toarray(), columns=vec_q.get_feature_names())

	# print(tdm_q)

	# Code to find Frequency of words in each class
	word_list_s = vec_s.get_feature_names();    
	count_list_s = X_s.toarray().sum(axis=0) 
	freq_s = dict(zip(word_list_s,count_list_s))
	# print(freq_s)

	word_list_q = vec_q.get_feature_names();    
	count_list_q = X_q.toarray().sum(axis=0) 
	freq_q = dict(zip(word_list_q,count_list_q))
	# print(freq_q)

	# the probability for each word in a given class without ls
	# prob_s = []
	# for count in count_list_s:
	# 	prob_s.append(count/len(word_list_s))
	# print('<<<<<<<<<<<<')
	# total = 1
	# for x in prob_s:
	# 	total = x * total
	# print (total)
	# print(dict(zip(word_list_s,prob_s)))

	# Laplace Smoothing
	# Total count of all features in the training set

	docs = [row['sent'] for index,row in training_data.iterrows()]

	vec = CountVectorizer()
	X = vec.fit_transform(docs)

	total_features = len(vec.get_feature_names())
	# print(total_features)

	# total count of all features in a class
	total_cnts_features_s = count_list_s.sum(axis=0)
	total_cnts_features_q = count_list_q.sum(axis=0)

	return freq_s, freq_q, total_features, total_cnts_features_s, total_cnts_features_q








alist_reporter = [] 

filename = "id_list.csv"
rows = [] 
ids_good = []
ids_bad = []
count_good = 0
count_bad = 0

# reading csv file 
with open(filename, 'r') as csvfile: 
    # creating a csv reader object 
    csvreader = csv.reader(csvfile) 
    
    for row in csvreader: 
    	if(row[1] == 'good'):
    		ids_good.append(row[0])
    		count_good += 1
    	else:
    		ids_bad.append(row[0])
    		count_bad += 1

pro_good = count_good/(count_good+count_bad)
pro_bad = count_bad/(count_good+count_bad)

print(pro_good)
print(pro_bad)

for id in ids_good:

	x = "https://bugzilla.mozilla.org/show_bug.cgi?id=" + id

	page = requests.get(x)
	# print(page)
	soup = BeautifulSoup(page.content, 'html.parser')
	list_change = soup.find_all(class_="change-set")

	list_good = reporter_list_func(list_change)
	list_good.append('good')
	alist_reporter.append(list_good)


for id in ids_bad[1:]:

	x = "https://bugzilla.mozilla.org/show_bug.cgi?id=" + id

	page = requests.get(x)
	# print(page)
	soup = BeautifulSoup(page.content, 'html.parser')
	list_change = soup.find_all(class_="change-set")

	list_bad = reporter_list_func(list_change)
	list_bad.append('bad')
	alist_reporter.append(list_bad)  



columns = ['sent', 'class']

freq_s, freq_q, total_features, total_cnts_features_s, total_cnts_features_q = nb (alist_reporter, columns)



# print(type(freq_s))
# print(type(total_features))
# print(type(total_cnts_features_q))



with open('objs.pkl', 'wb') as f:  # Python 3: open(..., 'wb')
    pickle.dump([freq_s, freq_q, total_features, total_cnts_features_s, total_cnts_features_q, pro_good, pro_bad], f)





  

