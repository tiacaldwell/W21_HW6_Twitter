#########################################
##### Name: Tia Caldwell           #####
##### Uniqname: tiacc              #####
##### Extra credit 1 ##################
#########################################

from requests_oauthlib import OAuth1
import json
import requests

import secrets_starter_code as secrets # file that contains your OAuth credentials

CACHE_FILENAME = "twitter_cache.json"
CACHE_DICT = {}

client_key = secrets.TWITTER_API_KEY
client_secret = secrets.TWITTER_API_SECRET
access_token = secrets.TWITTER_ACCESS_TOKEN
access_token_secret = secrets.TWITTER_ACCESS_TOKEN_SECRET

oauth = OAuth1(client_key,
            client_secret=client_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret)

def test_oauth():
    ''' Helper function that returns an HTTP 200 OK response code and a 
    representation of the requesting user if authentication was 
    successful; returns a 401 status code and an error message if 
    not. Only use this method to test if supplied user credentials are 
    valid. Not used to achieve the goal of this assignment.'''

    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    auth = OAuth1(client_key, client_secret, access_token, access_token_secret)
    authentication_state = requests.get(url, auth=auth).json()
    return authentication_state

#print(test_oauth())

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params

    AUTOGRADER NOTES: To correctly test this using the autograder, use an underscore ("_") 
    to join your baseurl with the params and all the key-value pairs from params
    E.g., baseurl_key1_value1
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    unique_id = baseurl

    #iterate through the dictonary of parameters in alphabetical order 
    sortedparams = sorted(params, key=str.lower)
    for p in sortedparams:
        #appends "_key_value" to the uniquie_id string 
        unique_id += ("_"+p+"_"+params[p]) 
    
    return unique_id
    
def make_request(baseurl, params):
    '''Make a request to the Web API using the baseurl and params
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the data returned from making the request in the form of 
        a dictionary
    '''
    auth = OAuth1(client_key, client_secret, access_token, access_token_secret)
    twitter_response = requests.get(baseurl, params, auth=auth).json() #This will add the ? for you before the paramets (key=value)
    #print(twitter_response)

    CACHE_DICT[construct_unique_key(baseurl, params)] = twitter_response
    return CACHE_DICT

def make_request_with_cache(baseurl, hashtag, count):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache, 
    but it will help us to see if you are appropriately attempting to use the cache.
    
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    hashtag: string
        The hashtag to search for
    count: integer
        The number of results you request from Twitter
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    #create parameters dictonary 
    #params = {'q':'%23'+hashtag+'%20-filter%3Aretweets', 'count': str(count)} #WILL EXCLUDE RETWEETS
    clean_hashtag = hashtag.lower().strip().replace('#', '')
    params = {'q':'%23'+clean_hashtag, 'count': str(count)} 

    #store unique_id 
    unique_id = construct_unique_key(baseurl, params)
    #print("THIS RUN's UNiQUE ID IS: ", unique_id)

    #check if unique_id is already in cache. If so, return the results. If not, run a Twitter request 
    if unique_id in CACHE_DICT:  
        print("\n fetching cached data...")
        return CACHE_DICT[unique_id]
    else: 
        print("\n making new request...")
        save_cache(make_request(baseurl, params))
        return CACHE_DICT[unique_id]

def find_most_common_cooccurring_hashtag(tweet_data, hashtag_to_ignore):
    ''' Finds the hashtag that most commonly co-occurs with the hashtag
    queried in make_request_with_cache().

    Parameters
    ----------
    tweet_data: dict
        Twitter data as a dictionary for a specific query
    hashtag_to_ignore: string
        the same hashtag that is queried in make_request_with_cache() 
        (e.g. "#MarchMadness2021")
    unique_id: str
        Unique ID of API search so access the right part of the dictonary 

    Returns
    -------
    string
        the hashtag that most commonly co-occurs with the hashtag 
        queried in make_request_with_cache()

    '''
    ''' Hint: In case you're confused about the hashtag_to_ignore 
    parameter, we want to ignore the hashtag we queried because it would 
    definitely be the most occurring hashtag, and we're trying to find 
    the most commonly co-occurring hashtag with the one we queried (so 
    we're essentially looking for the second most commonly occurring 
    hashtags).'''

    #create empty dictonary to track hashtag counts 
    hashtag_count = {}

    #pull the key of the dictonary that has the correct unique ID 
    list_of_tweets  = tweet_data['statuses']
    #print("length list of tweets is", len(list_of_tweets))

    for tweet_data in list_of_tweets:                         #seperate data into a list of data per tweet 
        hashtag_list = tweet_data['entities']['hashtags']     #find the list of hashtags in each tweet 
        for hashtag in hashtag_list:                          #iterate through the hashtags 
            clean_hashtag = hashtag['text'].lower().strip()   #strip excess spaces, make lower case 
            if clean_hashtag in hashtag_count:               #Either add to the count of how many times the # has occured 
                hashtag_count[clean_hashtag] = hashtag_count[clean_hashtag] + 1 
            else:                                            #Or add the hashtag as a key to the dictonary with a value one
                hashtag_count[clean_hashtag] = 1

    #delete key that is the excluded one or similar (ie no numbers) 
    clean_exlcude = (hashtag_to_ignore.lower().strip().replace('#', ''))
    hashtag_count.pop(clean_exlcude, None)
    clean_exlcude_nonum = ''.join([i for i in clean_exlcude if not i.isdigit()])
    hashtag_count.pop(clean_exlcude_nonum, None)

    if len(hashtag_count) >0:
        #return the max 
        print('\n The top three most common co-occuring hashtags with', hashtag_to_ignore, 'are:')

        x= 0
        for hashtag in sorted(hashtag_count, key=hashtag_count.get, reverse = True)[:3]:
            x = x +1
            if x < 3:
                print('\t Number ' + str(x)  + ': #'+ hashtag + ' with ' +  str(hashtag_count[hashtag]) + ' uses')
            if x ==3: 
                print('\t Number ' + str(x)  + ': #'+ hashtag + ' with ' +  str(hashtag_count[hashtag]) + ' uses \n')
        
        return(max(hashtag_count, key=hashtag_count.get)) 

    else: 
        print("\n There are no recents Tweets with this hashtag! Try another")


'''
Extra Credits #1
You’ll write an interactive program that can search any hashtag and displays its top3 most commonly co-occurring hashtags. 
The program should keep prompting userto search for a hashtag unless the user enters“exit”. Please note that for each
search you should still retrieve 100 tweets. We are not providing sample output, so you are encouraged to exercise 
reasonablejudgment in following the instructions above to meet the requirements. 
'''

def find_top_3_any_hashtag():
    
    baseurl = "https://api.twitter.com/1.1/search/tweets.json"
    count = 100 

    while True: 
        hashtag = input(" \n What hashtag do you want to search? (type 'exit' to stop): ")

        if hashtag == "exit": 
            break
        else: 
            tweet_data = make_request_with_cache(baseurl, hashtag, count)
            most_common_cooccurring_hashtag = find_most_common_cooccurring_hashtag(tweet_data, hashtag)

print("\n This is etxra credit #1:")
find_top_3_any_hashtag()