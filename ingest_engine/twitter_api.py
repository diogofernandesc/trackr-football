import os
import json
import re
from twitter import Api
from textblob import TextBlob
from nltk.corpus import stopwords
from rake_nltk import Rake

# CONSUMER_KEY = os.getenv("CONSUMER_KEY", None)
# CONSUMER_SECRET = os.getenv("CONSUMER_SECRET", None)
# ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", None)
# ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", None)

# Users to watch for should be a list. This will be joined by Twitter and the
# data returned will be for any tweet mentioning:
# @twitter *OR* @twitterapi *OR* @support.
#USERS = ['@twitter',
 #        '@twitterapi',
  #       '@support']
USERS = ['Trump']

# Languages to filter tweets by is a list. This will be joined by Twitter
# to return data mentioning tweets only in the english language.
LANGUAGES = ['en']

# Since we're going to be using a streaming endpoint, there is no need to worry
# about rate limits.
api = Api(CONSUMER_KEY,
          CONSUMER_SECRET,
          ACCESS_TOKEN,
          ACCESS_TOKEN_SECRET,
          tweet_mode='extended')


def main():
    with open('output.txt', 'a') as f:
        # api.GetStreamFilter will return a generator that yields one status
        # message (i.e., Tweet) at a time as a JSON dictionary.
        for line in api.GetStreamFilter(track=USERS, languages=LANGUAGES):
            if 'extended_tweet' in line or not line['text'].endswith('...'):
                f.write(line['extended_tweet']['full_text'])
                f.write('\n')


def twitter_test():
    r = Rake()
    tweet_count = 0
    overall_sentiment = 0
    noun_phrases = []
    tags = []
    for streamed_tweet in api.GetStreamFilter(track=USERS, languages=LANGUAGES):
        if 'retweeted_status' not in streamed_tweet:
            if 'extended_tweet' in streamed_tweet:
                tweet = streamed_tweet['extended_tweet']['full_text']
            else:
                if 'text' in streamed_tweet:
                    tweet = streamed_tweet['text']

            # Clean tweet:
            regex_remove = "(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|&amp;|amp|(\w+:\/\/\S+)|^RT|http.+?"
            tweet = re.sub(regex_remove, '', tweet).strip()
            # tweet = " ".join(word for word in tweet.split() if word not in stopwords.words('english'))
            tweet_blob = TextBlob(tweet)
            sentiment = tweet_blob.sentiment.polarity
            print(tweet)
            print(sentiment)
            result = r.extract_keywords_from_text(text=tweet)
            if result:
                print(result)
            print("------------------")
            tweet_count += 1
            overall_sentiment += sentiment


        if tweet_count == 100:
            print(tweet_count)
            print(overall_sentiment)
            break

if __name__ == '__main__':
    twitter_test()