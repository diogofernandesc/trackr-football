import os
import json
from twitter import Api

CONSUMER_KEY = 'FEX1vMnNmTl7OULEgdRF9BcEL'
# CONSUMER_KEY = os.getenv("CONSUMER_KEY", None)
CONSUMER_SECRET = 'oottsceTK4vbjYceigB4frHI8DNBffztDHH2rt9Xt743BxQW4k'
# CONSUMER_SECRET = os.getenv("CONSUMER_SECRET", None)
ACCESS_TOKEN = '212721420-9RvBPYn9uTj5GOHQM9DB7zAdSpMvV3dEaj2muG3R'
# ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", None)
ACCESS_TOKEN_SECRET = '8bBK5BfiruvIPpghxUlfzV1iaDHrW2CngN2cyz5oaoSBu'
# ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET", None)

# Users to watch for should be a list. This will be joined by Twitter and the
# data returned will be for any tweet mentioning:
# @twitter *OR* @twitterapi *OR* @support.
#USERS = ['@twitter',
 #        '@twitterapi',
  #       '@support']
USERS = ['Kane', 'Mourinho']

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


if __name__ == '__main__':
    main()