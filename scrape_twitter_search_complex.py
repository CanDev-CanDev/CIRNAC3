# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
def read_search_terms(filename):
    lst=[]
    with open (filename,"r") as f:
        for line in f:
            y = line.rstrip().split(',')
            y[0] = y[0].strip("\'")
            y[1]=int(y[1])
            lst.append(y)
        return lst

def scrape_tweets_from_search(search_term = "right", search_depth = 10, hashtag = 0):
    import time
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from datetime import datetime
    
    t1 = datetime.now()
    
    driver = webdriver.Firefox()
    base_url = u'https://twitter.com/search?q='
    if hashtag == 0:
        query = search_term
    else:
        words = search_term.split()
        query = ""
        for word in words:
            word = "%23" + word + " "
            query = query + word
        query = query[:-1]
            
    url = base_url + query
    
    driver.get(url)
    time.sleep(1)
    driver.refresh()
    
    body = driver.find_element_by_tag_name('body')
    
    for _ in range(search_depth):
        body.send_keys(Keys.END)
        time.sleep(1.5)
        
    tweets = driver.find_elements_by_class_name('TweetTextSize')
    timestamps = [element.get_attribute('title') for element in driver.find_elements_by_class_name('tweet-timestamp')]
    
    i = 0
    tweetdata = []
    for tweet in tweets:
        tweetdata.append([query.replace("%23","#"),str(i+1),str(tweet.text),str(timestamps[i])])
        i = i + 1
    
    #t2 = datetime.now()
    #print("\n\nThe process took " + str(t2 - t1) + " seconds")
    
    driver.quit()
    
    return tweetdata
    
def save_results_to_file():
    import pickle
    search_depth = 20 #the code pulls ~ (20 + search_depth*20 tweets), provided there are enough results
    search_terms = read_search_terms("Query_terms.txt")
    tweetdb = []
    for item in search_terms:
        query = item[0]
        hashtag = item[1]
        tweetreturn = scrape_tweets_from_search(query,search_depth,hashtag)
        tweetdb.extend(tweetreturn)
    df = pd.DataFrame(tweetdb, columns=['Search Term','Tweet number','Text','Timestamp'])
    print(len(df))
    df.drop_duplicates(subset = ['Text','Timestamp'], keep=False, inplace=True)
    print(len(df))
    with open("tweets_complex.file","wb") as f:
       pickle.dump(df,f, pickle.HIGHEST_PROTOCOL)
    #df2 = pd.DataFrame(tweetdb, columns=['Search Term','Tweet number','Text','Timestamp'])
    #with open("tweets.file", "rb") as f:
       #df2 = pickle.load(f)
    #print(df2.to_string())"""
    
save_results_to_file()
    