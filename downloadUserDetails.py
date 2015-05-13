import tweepy
import sys
import jsonpickle
import os

# Don't buffer stdout, so we can tail the log output redirected to a file
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# API and ACCESS KEYS
API_KEY = sys.argv[1]
API_SECRET = sys.argv[2]

userIdfName = sys.argv[3]
outfName = sys.argv[4]


auth = tweepy.AppAuthHandler(API_KEY, API_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if (not api):
    print ("Can't Authenticate Bye!")
    sys.exit(-1)

with open(userIdfName, 'r') as inp:
    userIds = [line.rstrip('\n') for line in inp]

numUsers = len(userIds)
print("Going to query {0} users".format(numUsers))
usersQueried = 0

with open(outfName, 'w') as out:
    while (usersQueried < numUsers):
        batch = userIds[usersQueried:min(usersQueried+100, numUsers)]
        usersQueried += 100
        print("Going to Query {0} users".format(len(batch)))
        users = api.lookup_users(user_ids=batch)
        print("Got Back {0} users".format(len(users)))
        for user in users:
            out.write(jsonpickle.encode(user, unpicklable=False)+'\n')
