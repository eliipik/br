import pickle
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import requests
from reporter import reporter_list_func


# Getting back the objects:
with open('objs.pkl', 'rb') as f:  
    freq_s, freq_q, total_features, total_cnts_features_s, total_cnts_features_q, pro_good, pro_bad = pickle.load(f)

# print(type(freq_s))
# print(type(total_features))
# print(type(total_cnts_features_q))


val = input("Enter the id: ") 

x = "https://bugzilla.mozilla.org/show_bug.cgi?id=" + val
page = requests.get(x)
# print(page)


soup = BeautifulSoup(page.content, 'html.parser')
list_change = soup.find_all(class_="change-set")

new_report = reporter_list_func(list_change)
str_new_report = ''.join(new_report)


# str_new_report = 'what is the price of the book'
new_word_list = word_tokenize(str_new_report)

prob_s_with_ls = []
for word in new_word_list:
    if word in freq_s.keys():
        count = freq_s[word]
    else:
        count = 0
    prob_s_with_ls.append((count + 1)/(total_cnts_features_s + total_features))
dict_good = dict(zip(new_word_list,prob_s_with_ls))


prob_q_with_ls = []
for word in new_word_list:
    if word in freq_q.keys():
        count = freq_q[word]
    else:
        count = 0
    prob_q_with_ls.append((count + 1)/(total_cnts_features_q + total_features))
dict_bad = dict(zip(new_word_list,prob_q_with_ls))


total_good = 1
for x, y in dict_good.items():
  total_good = total_good * y
  

total_bad = 1
for x, y in dict_bad.items():
  total_bad = total_bad * y
  


if ((total_good * pro_good) > (total_bad * pro_bad)):
	print ('good')
else:
	print ('bad')




