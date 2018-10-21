import time, os.path, traceback, json
import requests
import nltk
from bs4 import BeautifulSoup

REDDIT_START=r'http://reddit.com'
SEARCH_URL=r'http://reddit.com/search.json?q='
SLOWDOWN = 0 # seconds to wait between requests
MIN_WORD_LENGTH = 2 # minimum word length for removal of garbage """words"""


'''
Search query and pull out keywords
'''
def search(query, recursive=False, limit=25, recurse_to=1, filter={'NN'}, weight=1):
    keywords = list()
    response = get_request_nofail(SEARCH_URL+query+'&limit='+str(limit))
    search_results = response.json()['data']['children'] # list of search results
    for i in range(len(search_results)):
        result = search_results[i]
        permalink = search_results[i]['data']['permalink']
        id = search_results[i]['data']['id']
        time.sleep(SLOWDOWN)
        url = REDDIT_START+permalink.rstrip('/')+'.json?limit='+str(limit)
        # print("Now scraping %s" % url)
        thread = get_request_nofail(url)
        comments = thread.json()[1]['data']['children']

        # iterate through all the comments returned
        for j in range(len(comments)-1): # last listing in comments is a link to more comments; not a real comment
            try:
                comment = comments[j]
                comment_body=comment['data']['body']
                tokens = nltk.tokenize.casual.casual_tokenize(comment_body)
                remove_garbage(tokens)
                filtered_words = [word for word in tokens if word not in nltk.corpus.stopwords.words('english')]
                new_keywords = nltk.pos_tag(filtered_words)
                for keyword in new_keywords:
                    if keyword[1] in filter:
                        keywords.append(keyword+(weight/(i+1),))
                        if recursive and recurse_to>0:
                            keywords += search(keyword[0], recursive=True, limit=limit, recurse_to=recurse_to-1, weight=weight/recurse_to)
            except:
                print('Error while processing %s' %url)
                print(json.dumps(comment, indent=2))
                traceback.print_exc()
    return keywords

'''
Catch some common exceptions and data integrity issues
'''
def get_request_nofail(url):
    success = False
    while not success:
        try:
            response = requests.get(url, headers={'user-agent':'Mozilla/5.0'}) # user-agent is due to dumb reddit botting restrictions
            if response.status_code == 200:
                success = True
            if not success:
                time.sleep(SLOWDOWN)
        except KeyboardInterrupt:
            break
        except:
            print("Error in requesting %s" %url)
            traceback.print_exc()
    return response

'''
Remove short "words" that NLP tokenization misinterprets (eg XD, ", ] )
'''
def remove_garbage(l):
    i=0
    while i<len(l):
        if len(l[i]) <=MIN_WORD_LENGTH:
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

def organise_results(result_dict, threshold=0):
    result_l = list()
    for key in result_dict:
        if result_dict[key]>threshold:
            result_l.append([result_dict[key], key])
    result_l.sort() # sort lowest to highest
    return [[x[1],x[0]] for x in result_l[::-1]] # highest first, keyword first


'''
Delete values below threshold
'''
def discard_values(result_dict, threshold=1):
    to_del = list()
    for key in result_dict:
        if result_dict[key]<threshold:
            to_del.append(key)
    for key in to_del:
        del(result_dict[key])

def discard_values2(result_dict, threshold=-1):
    to_del = list()
    for key in result_dict:
        if result_dict[key]>threshold:
            to_del.append(key)
    for key in to_del:
        del(result_dict[key])

def normalize(result_dict, target=1):
    multiplier = target/sum(result_dict.values())
    for key in result_dict:
        result_dict[key]=result_dict[key]*multiplier
    return result_dict

def combine(dict_a, dict_b):
    result = dict(dict_a)
    for key in dict_b:
        if key in result:
            result[key]+=dict_b[key]
        else:
            result[key]=dict_b[key]
    return result


# testing
if __name__ == '__main__':
    from nltk.corpus import wordnet
    # base set of regular expressions
    # '''
    control_results = list()
    # TODO: use non-arbitrary control word(s)
    control_names = {'crane', 'three', 'Australia', 'inning', 'became', 'cloud', 'qwerty', 'machine', 'animal'} # set of random words
    """for syn in wordnet.synsets('life'):
        for name in syn.lemma_names():
            control_names.add(name)"""
    for name in control_names:
        name = name.replace('_', ' ') # nltk is too cool to use spaces so they use _ instead
        print('Now scraping search control results for %s' %name)
        control_results += search(name, limit=100, weight=-1)

    with open('reddit_control.json', 'w') as file:
        json.dump(control_results, file, indent=2) # these results are not adjusted for common words'''
    '''with open('reddit_control.json', 'r') as file:
        control_results = json.load(file)'''

    # actual results
    # '''
    result = list()
    names = {'aboriginal', 'aborigine', 'indigenous canada'} # set to prevent duplicates
    # result = search('indigenous', weight=1.0, limit=100)
    for syn in wordnet.synsets('indigenous'):
        for name in syn.lemma_names():
            names.add(name)
    for syn in wordnet.synsets('inuit'):
        for name in syn.lemma_names():
            names.add(name)

    for name in names:
        print('Now scraping search results for %s' %name)
        result += search(name, limit=100)

    # print(result)
    with open('reddit_keywords.json', 'w') as file:
        json.dump(result, file, indent=2) # these results are not adjusted for common words '''
    with open('reddit_keywords.json', 'r') as file:
        result = json.load(file)

    control_keyword_count = get_count(control_results)
    keyword_count = get_count(result)
    discard_values2(control_keyword_count)
    discard_values(keyword_count)
    with open('reddit_keywords_count.json', 'w') as file:
        json.dump(keyword_count, file, indent=2)

    # normalize values to be able to combine both counts without weighting issues
    control_keyword_count = normalize(control_keyword_count, target=-1)
    keyword_count = normalize(keyword_count)

    results_nice = organise_results(combine(keyword_count, control_keyword_count)) # these results are (sort of) adjusted for common words
    with open('reddit_results.json', 'w') as file:
        json.dump(results_nice, file, indent=2)
