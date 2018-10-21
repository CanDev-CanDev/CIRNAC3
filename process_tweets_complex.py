# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 04:25:24 2018

@author: Harshit J
"""
import pandas as pd
import pickle
import nltk
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import json

MIN_WORD_LENGTH = 2

def remove_garbage(l):
    i=0
    while i<len(l):
        if len(l[i]) <= MIN_WORD_LENGTH:
            del(l[i])
        else:
            i+=1
            
def get_count(l):
    # l should a iterable of tuple (word, NLP identifier, weight)
    result = dict()
    for i in l:
        if i[0] in result:
            result[i[0]]+=i[2]
        else:
            result[i[0]]=i[2]
    return result

def discard_values(result_dict, threshold=1):
    to_del = list()
    for key in result_dict:
        if result_dict[key]<threshold:
            to_del.append(key)
    for key in to_del:
        del(result_dict[key])
        
def organise_results(result_dict):
    result_l = list()
    for key in result_dict:
        result_l.append([result_dict[key], key])
    result_l.sort() # sort lowest to highest
    return [[x[1],x[0]] for x in result_l[::-1]] # highest first, keyword first

def normalize(result_dict, target=1):
    multiplier = target/sum(result_dict.values())
    for key in result_dict:
        result_dict[key]=result_dict[key]*multiplier
    return result_dict

with open("tweets_complex.file", "rb") as f:
    tweetdb = pickle.load(f)
df = pd.DataFrame(tweetdb, columns=['Search Term','Tweet number','Text','Timestamp'])

with pd.option_context('display.max_rows', None, 'display.max_columns', df.shape[1]):
    print(df.loc[[0]])
    
df['Tokenized Tweet'] = df['Text'].apply(nltk.tokenize.casual.casual_tokenize)

with pd.option_context('display.max_rows', None, 'display.max_columns', df.shape[1]):
    print(df.loc[[0]])

lst = df['Tokenized Tweet'].tolist()

print(lst[0])
filtered_words = []
new_keywords = []
keywords = []
weight = 1
filter = {'NN'}

for i in range(len(lst)):
    remove_garbage(lst[i])
    filtered_words.append([word for word in lst[i] if word not in nltk.corpus.stopwords.words('english')])
    filtered_words[i] = [item.lower() for item in filtered_words[i]]
    new_keywords.append(nltk.pos_tag(filtered_words[i]))
    for keyword in new_keywords[i]:
        if keyword[1] in filter:
            keywords.append(keyword+(weight/1,))
    
result = get_count(keywords)    

print(lst[0])
print(filtered_words[0])
print(new_keywords[0])
print(keywords[0])
discard_values(result, threshold=20)

result = normalize(result, target=1)

result_nice = organise_results(result)


print(result_nice)
with open('twitter_results2.json', 'w') as file:
    json.dump(result_nice, file, indent=2)

wc = WordCloud(background_color="white",width=4000,height=3000, max_words=50,relative_scaling=0.5,normalize_plurals=False).generate_from_frequencies(result)
plt.imshow(wc)
plt.axis('off')
plt.savefig('wordcloud2.png',format = 'png', dpi = 1200, bbox_inches='tight')