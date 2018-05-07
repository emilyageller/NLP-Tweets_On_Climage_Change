# This script connects to Twitter's Rest API and pulls Climate Change tweets into a MongoDB on an AWS EC2 Instance


import cnfg
import tweepy
import json
from pymongo import MongoClient
import pymongo

# Connect to MongoDB on AWS
client = pymongo.MongoClient("mongodb://your_aws_instance:your_aws_password@your_aws_ip/climatechange")
db = client.climatechange
col = db.climate_tweets

# Connect to Twitter's API through Tweepy
config = cnfg.load(".twitter_config")
auth = tweepy.AppAuthHandler(config["consumer_key"], config["consumer_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True,
                   wait_on_rate_limit_notify=True)

if (not api):
    print ("Can't Authenticate")
    sys.exit(-1)

# If the API is ready to go, continue with rest of the script

import sys
import jsonpickle
import os

searchQuery = ('#climatechange OR climate change OR #globalwarming OR global warming')  # Search for tweets containing any of these terms
maxTweets = 500000 # Some arbitrary large number
tweetsPerQry = 450  # this is the max the API permits
language = 'en' # only get tweets in english
tweetmode = 'extended' # without this parameter, truncated tweets are returned


# If results from a specific ID onwards are reqd, set since_id to that ID.
# else default to no lower limit, go as far back as API allows
sinceId = None

# If results required are only below a specific ID, set max_id to that ID.
# else default to no upper limit, start from the most recent tweet matching the search query.
max_id = 1e4000

tweetCount = 0
print("Downloading max {0} tweets".format(maxTweets))

# Stream tweets according to user-defined max_id and sinceId
while tweetCount < maxTweets:
    try:
        if (max_id <= 0):
            if (not sinceId):
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry, lang= language, tweet_mode = tweetmode)
            else:
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                        since_id=sinceId, lang= language, tweet_mode = tweetmode)
        else:
            if (not sinceId):
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                        max_id=str(max_id - 1), lang= language, tweet_mode = tweetmode)
            else:
                new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                        max_id=str(max_id - 1),
                                        since_id=sinceId, lang= language, tweet_mode = tweetmode)
        if not new_tweets:
            print("No more tweets found")
            break
            
# Load tweets into MongoDB
        for tweet in new_tweets:
            col.insert(tweet._json)
        tweetCount += len(new_tweets)
        print("Downloaded {0} tweets".format(tweetCount))
        max_id = new_tweets[-1].id
    except tweepy.TweepError as e:
        # Just exit if any error
        print("some error : " + str(e))
        break

print ("Downloaded {0} tweets, Saved to MongoDB ClimateChange".format(tweetCount))