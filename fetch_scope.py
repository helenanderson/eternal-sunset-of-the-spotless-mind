from os import path
import os
import requests
import tweepy
import datetime
import re

#Returns (consumer_key, consumer_secret)
# def load_twitter_secrets():
#     twitter_filename = path.join('secrets', 'twitter.txt')
#     with open(twitter_filename, 'r') as twitter_file:
#         return twitter_file.read().strip().split('\n')

def load_auth():
    #consumer_key, consumer_secret = load_twitter_secrets()
    #return tweepy.AppAuthHandler(consumer_key, consumer_secret)
    return tweepy.AppAuthHandler(os.environ['TWITTER_KEY'], os.environ['TWITTER_SECRET'])

twitter_auth = load_auth()
twitter = tweepy.API(twitter_auth)

# Returns scope_info object
def most_recent_scopes(query, scopes):
    all_scopes = scopes
    tweets = twitter.search(q='periscope ' + query)
    for tweet in tweets:
        original_text = ""
        if hasattr(tweet, 'retweeted_status'):
            original_text = tweet.retweeted_status.text
        else:
            original_text = tweet.text

        for url in tweet.entities['urls']:
            original_text = original_text.replace(url['url'], '')

        if original_text not in [thing[5] for thing in all_scopes]:
            #print tweet.text
            for url in tweet.entities['urls']:
                #print tweet.entities['urls']
                plain_url = url['url']
                expanded_url = url['expanded_url']
                original_text.replace(plain_url, "")
                #print expanded_url
                if expanded_url.startswith('https://www.periscope.tv/w/'):
                    response = requests.get(expanded_url)
                    scope_info = [tweet, plain_url, start_time(response), scope_is_live(response), False, original_text]
                    if scope_info[2] and (len(all_scopes) is 0 or scope_info[1] not in [scope[1] for scope in all_scopes]):
                        all_scopes.append(scope_info)
    sorted_scopes = sorted(all_scopes, key=lambda x: x[2], reverse=True)
    for scope in sorted_scopes:
        if scope[3] is True:
            sorted_scopes.remove(scope)
            sorted_scopes.insert(0, scope)
    #print [(scope[1], scope[2], scope[3]) for scope in sorted_scopes]
    #live_scopes = [x for x in sorted_scopes if x[3] is True]
    return sorted_scopes

def scope_is_live(response):
    return 'isEnded&quot;:false' in response.text

def start_time(response):
    m = re.search(r'start&quot;:&quot;((\d\d\d\d)-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d))', response.text)
    if not m:
        return None
    return m.group(1)

def scope_in_timeframe(tweet, hours):
    return datetime.datetime.now() - tweet.created_at < datetime.timedelta(hours = hours)
