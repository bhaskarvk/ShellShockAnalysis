import tweepy
import sys
import jsonpickle
import os

# Don't buffer stdout, so we can tail the log output redirected to a file
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# API and ACCESS KEYS
API_KEY = sys.argv[1]
API_SECRET = sys.argv[2]

searchQuery = sys.argv[3]
maxTweets = int(sys.argv[4])
tweetsPerQry = 100
fName = sys.argv[5]

sinceId = None
if(len(sys.argv) > 6):
    if(sys.argv[6] != '-1'):
        sinceId = sys.argv[6]

last_id = -1L
if(len(sys.argv) > 7):
    last_id = long(sys.argv[7])

auth = tweepy.AppAuthHandler(API_KEY, API_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if (not api):
    print ("Can't Authenticate Bye!")
    sys.exit(-1)

tweetCount = 0
print("Downloading max {0} tweets".format(maxTweets))
with open(fName, 'w') as f:
    while tweetCount < maxTweets:
        try:
            if (last_id <= 0):
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry)
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            since_id=sinceId)
            else:
                if (not sinceId):
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(last_id - 1))
                else:
                    new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                            max_id=str(last_id - 1),
                                            since_id=sinceId)
            if not new_tweets:
                print("No more tweets found")
                break
            for tweet in new_tweets:
                f.write(jsonpickle.encode(tweet._json, unpicklable=False) +
                        '\n')
            tweetCount += len(new_tweets)
            print("Downloaded {0} tweets".format(tweetCount))
            last_id = new_tweets[-1].id
        except tweepy.TweepError as e:
            # Just exit if any error
            print("some error : " + str(e))
            break

print ("Downloaded {0} tweets, Saved to {1}".format(tweetCount, fName))
