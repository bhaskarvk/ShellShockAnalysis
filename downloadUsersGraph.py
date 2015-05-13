import tweepy
import sys
import jsonpickle
#import pandas as pd
import networkx as nx
import os

userDetailsCache =  {}


def getUserDetails(api, cache, userIds):
    uniqUserIds = set(userIds)

    # return object
    userDetails = list()

    cachedUserIds = set([userId for userId in uniqUserIds if userId in cache])
    userDetails.extend([cache[user] for user in cachedUserIds])


    unCachedUserIds =  list(uniqUserIds.difference(cachedUserIds))
    usersToBeQueried = len(unCachedUserIds)

    print("{0} users cached".format(len(cachedUserIds)))
    print("Going to query {0} uncached users".format(usersToBeQueried))
    usersQueried = 0
    while (usersQueried < usersToBeQueried):
        batch = unCachedUserIds[usersQueried:min(usersQueried+100, usersToBeQueried)]
        usersQueried += 100
        users = api.lookup_users(user_ids=batch) #TODO catch exception
        userDetails.extend(users)
        for user in users:
            cache[user.id] = user
    print("Got Back {0} users".format(len(userDetails)))
    return userDetails


def getFollowersIds(api, user):
    print("Going to query followers of user {0}[{1}]".format(user.screen_name, user.id))
    followersIds = tweepy.Cursor(api.followers_ids, id=user.id).items(10) # 100 most recent followers
    try:
        return [followerId for followerId in followersIds] # We need to traverse the cursor
    except tweepy.TweepError as e:
        return []


def getFollowersIds2(api, userId):
    print("Going to query followers of user [{0}]".format(userId))
    followersIds = tweepy.Cursor(api.followers_ids, id=userId,count=5000).items(5000)
    try:
        return [followerId for followerId in followersIds] # We need to traverse the cursor
    except tweepy.TweepError as e:
        return []


def stripString(s):
    if s is None:
        return ''
    else:
        return s.strip()


def addUser(G, user):
    if (not G.has_node(user.id)):
        G.add_node(user.id,
                   created_at=user.created_at.isoformat(),
                   created_at_epochOffset=user.created_at.strftime('%s'),
                   lang=stripString(user.lang),
                   name=stripString(user.name),
                   timezone=stripString(user.time_zone),
                   location=stripString(user.location),
                   followers_count=user.followers_count,
                   screen_name=stripString(user.screen_name),
                   total_tweets=user.statuses_count
                   )


def addUserIds(G, userIds):
        G.add_nodes_from(userIds)


def addFollowers(G, user, followers):
    followersCount = 0
    for follower in followers:
        followersCount += 1
        addUser(G, follower)
        G.add_edge(follower.id, user.id)
    print("Added {0} followers to User {1}[{2}]".format(followersCount, user.screen_name, user.id))


def addFollowersIds(G, userId, followersIds):
    for followerId in followersIds:
        G.add_edge(followerId, userId)
    print("Added {0} followers to User [{1}]".format(len(followersIds), userId))


def populateGraph(G, cache, userDetails, curLevel, maxLevel):
    if(curLevel<maxLevel):
        print("At level {0}".format(curLevel))
        for user in userDetails:
            if (curLevel == 0): # Already added by prev. call to populateGraph->addFollowers
                addUser(G, user)
            followersIds  = getFollowersIds(api, user)
            if(len(followersIds)>0):
                followers = getUserDetails(api, cache, followersIds)
                addFollowers(G, user, followers)
                populateGraph(G, cache, followers, curLevel+1, maxLevel)
    else:
        print("Reached max level of {0}".format(maxLevel))


def populateIdGraph(G, userIds, curLevel, maxLevel):
    if(curLevel<maxLevel):
        print("At level {0}".format(curLevel))
        if(curLevel==0):
            addUserIds(G, userIds)
        for userId in userIds:
            followersIds  = getFollowersIds2(api, userId)
            if(len(followersIds)>0):
                addFollowersIds(G, userId, followersIds)
                populateIdGraph(G, followersIds, curLevel+1, maxLevel)
    else:
        print("Reached max level of {0}".format(maxLevel))



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
    authors = [line.rstrip('\n') for line in inp]

#authorDetails = getUserDetails(api, userDetailsCache, authors)

G = nx.DiGraph()
populateIdGraph(G, authors, 0, 3)
nx.write_gexf(G, outfName)
