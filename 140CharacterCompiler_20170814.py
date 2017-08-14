### Project: Identifying
### @Author: James R. Monette, website
### Last Edit: 7/20/2017, 12:27PM

### Description: 140 Character Politics is project hosted on git that has continuously cataloged tweets from U.S. Representatives of Congress since 6/21
### The project updates continuously, so rather than manually downloading the data base every session we'll start by importing straight from their GIT

### Python Imports ###
import pandas as pd
import requests
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

##### Setup for Twitter Crawler #####
class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Personal keys to acces twitter API
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'egg1zaOF7dIkBSFQ4AE6aYPgv'
        consumer_secret = 'NPXf6CTGJ5kspOEBM55N2DrXA2zzTTKSkQHcFxDH8b6A2DMKbn'
        access_token = '4539811335-tJyN1oqUUAJekn8LWETt0O9Z0K3axelJWBE16BK'
        access_token_secret = 'B0pp3hzyt9iT9PUZmGkv6TndIEJNKWl29ZMlRy1bDJ7p5'

        # try authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters w/ regex
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()).lower()

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

def main():

    ##### Step 1: Import Data from GIT #####
    ## First make a list of the filenames in the target directory @runtime
    data_repo = "https://github.com/alexlitel/congresstweets/tree/master/data"
    # Use requests to get contents of git repository
    r = requests.get(data_repo)
    # Some cleanup to reduce contents to list of json files
    content_list = r.content.split()
    json_list = []
    for i in content_list:
        if "title=\"2017-" in i.decode("utf-8"):
            json_list.append(i.decode("utf-8")[7:22])

    ### Create df and read in jsons from json_list
    tweets_df = pd.DataFrame()
    try:
        for json in json_list:
            tweets_df = tweets_df.append(pd.read_json('https://raw.githubusercontent.com/alexlitel/congresstweets/master/data/'+json))
    except:
        print(json + " failed")


    ##### Step2 Cleaning Tweets and Running Sentiment Analysis
    # creating object of TwitterClient Class
    api = TwitterClient()
    # clean tweets and add them back to df
    list_of_text = []
    for text in tweets_df['text']:
        list_of_text.append(api.clean_tweet(text))
    tweets_df['cleaned_text'] = list_of_text

    # run sentiment analysis on cleaned tweets
    #
    sentiment = []
    for cleaned_text in tweets_df['cleaned_text']:
        sentiment.append(api.get_tweet_sentiment(cleaned_text))
    tweets_df['sentiment'] = sentiment

    ##### Step 3: Enhancing the Dataset #####
    ### The original set lacks useful info about each politician, which district are they in, are they up for relection in 2018, etc...
    # In a separate block of code, I pulled data on individual representatives from https://github.com/unitedstates/congress-legislators
    # I'll combine that set with my tweet df below

    # Read in twitter_handle to names
    politician_demo_df = pd.read_csv('D:/Data Science Projects/TDI Project/20170719_140CharacterPolitics/politician_demos_edit.csv',encoding = "ISO-8859-1")

    # Merge set
    full_df = pd.merge(tweets_df,politician_demo_df.drop_duplicates(subset=['screen_name']), on='screen_name')
    pd.DataFrame.to_csv(full_df,'D:/Data Science Projects/TDI Project/20170719_140CharacterPolitics/full.csv')

    # Now limit the set to keywords of interest
    keywords = ['trump','president','white house','potus','administration']
    keyword_df = pd.DataFrame()
    for keyword in keywords:
        keyword_df = keyword_df.append(full_df.loc[full_df['cleaned_text'].str.contains(keyword)],ignore_index=True)
    print(len(keyword_df))
    pd.DataFrame.to_csv(keyword_df,'D:/Data Science Projects/TDI Project/20170719_140CharacterPolitics/keyword.csv')




main()




