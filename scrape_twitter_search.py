# -*- coding: utf-8 -*-
"""
"""
import pandas as pd

def scrape_tweets_from_search(search_depth = 10):
    import time
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    
    driver = webdriver.Firefox()
    base_url = u'https://twitter.com/search?q='
    query = '%23indigenous OR %23aboriginal'
            
    url = base_url + query
    
    driver.get(url)
    time.sleep(1)
    driver.refresh()
    
    body = driver.find_element_by_tag_name('body')
    
    for _ in range(search_depth):
        body.send_keys(Keys.END)
        time.sleep(1.75)
        
    tweets = driver.find_elements_by_class_name('TweetTextSize')
    timestamps = [element.get_attribute('title') for element in driver.find_elements_by_class_name('tweet-timestamp')]
    
    i = 0
    tweetdata = []
    for tweet in tweets:
        tweetdata.append([query.replace("%23","#"),str(i+1),str(tweet.text),str(timestamps[i])])
        i = i + 1
        
    driver.quit()
    
    return tweetdata
    
def save_results_to_file():
    import pickle
    from datetime import datetime
    t1 = datetime.now()
    search_depth = 900 #the code pulls ~ (20 + search_depth*20 tweets), provided there are enough results
    tweetdb = []
    tweetreturn = scrape_tweets_from_search(search_depth)
    tweetdb.extend(tweetreturn)
    df = pd.DataFrame(tweetdb, columns=['Search Term','Tweet number','Text','Timestamp'])
    print("tweet count = " + str(len(df)))
    #df.drop_duplicates(subset = ['Text','Timestamp'], keep=False, inplace=True)
    #print("unique tweets = " + str(len(df)))
    with open("tweets_simple.file","wb") as f:
       pickle.dump(df,f, pickle.HIGHEST_PROTOCOL)
    #df2 = pd.DataFrame(tweetdb, columns=['Search Term','Tweet number','Text','Timestamp'])
    #with open("tweets.file", "rb") as f:
       #df2 = pickle.load(f)
    #print(df2.to_string())
    t2 = datetime.now()
    print("\n\nThe process took " + str(t2 - t1) + " seconds")
    

save_results_to_file()
    