import pandas as pd
import sys
import json
from datetime import datetime
from ggplot import *

fName = sys.argv[1]

tweets = []
with open(fName, 'r') as fp:
    for tweet in fp:
        t = json.loads(tweet)
        t['created_at'] = \
            datetime.strptime(t['created_at'],
                              '%a %b %d %H:%M:%S +0000 %Y')
        tweets.append(t)

print len(tweets)

# tweetsTS = pd.DatetimeIndex([tweet['created_at'] for tweet in tweets])
# tweetsDF = pd.DataFrame(tweets, index=tweetsTS)
tweetsDF = pd.DataFrame(tweets)
tweetsDF['date'] = tweetsDF['created_at'].map(lambda x: x.date())
tweetsDF['user_info'] = tweetsDF['user'].map(lambda u:u['name']+'(@'+u['screen_name']+')')
tweetsDF['screen_name'] = tweetsDF['user'].map(lambda u: u['screen_name'])
tweetsDF['is_a_retweet'] = pd.notnull(tweetsDF['retweeted_status'])
tweetsDF['hashtags'] = tweetsDF['entities'].map(
    lambda x: ' '.join(([ht['text'].lower().strip()
                         for ht in x['hashtags']])))
tweetsDF['urls'] = tweetsDF['entities'].map(
    lambda x: ' '.join(([ht['expanded_url'].strip()
                        for ht in x['urls']])))

uniqtweetsDF = tweetsDF[~tweetsDF['is_a_retweet']]
uniqtweetsDF.reset_index(inplace=True)

# Tweets and Retweets per day
ggplot(tweetsDF,
       aes(x='factor(date)', fill='factor(is_a_retweet)')) + \
    geom_bar() + scale_y_continuous(labels='comma') + \
    theme(axis_text_x=element_text(angle=45, hjust=1)) + \
    xlab('date') + ylab('tweets') + ggtitle('All Tweets related to Shellshock')

print len(uniqtweetsDF)

# Unique Tweets per day
ggplot(uniqtweetsDF,
       aes(x='factor(date)', fill='factor(is_a_retweet)')) + \
    geom_bar() + scale_y_continuous(labels='comma') + \
    theme(axis_text_x=element_text(angle=45, hjust=1)) + \
    xlab('date') + ylab('tweets') + ggtitle('All Tweets related to Shellshock')

# Top 20 retweets
uniqtweetsDF.sort(columns='retweet_count',ascending=False)[:20].reset_index()[['screen_name','retweet_count','text']]

ggplot(uniqtweetsDF.sort(columns='retweet_count',ascending=False)[0:20].reset_index(),
       aes(x='factor(screen_name)', y='retweet_count', fill='factor(is_a_retweet)')) + \
    geom_bar(stat='identity') + scale_y_continuous(labels='comma') + \
    theme(axis_text_x=element_text(angle=45, hjust=1)) + \
    xlab('User') + ylab('Number of Retweets') + ggtitle('Owners of Top 20 Retweeted tweets related to Shellshock')

# Top 20 Hashtags in Tweets & Retweets
all_tags = pd.Series([ht for hts in tweetsDF['hashtags']
                        for ht in hts.split(" ")])
all_tags = all_tags[all_tags.map(len) > 0]
all_tags.reset_index(drop=True, inplace=True)

top_100_hts = pd.value_counts(all_tags)[:100]
top_100_hts = top_100_hts.reset_index()
top_100_hts.columns = ['hashtag', 'count']
ggplot(top_100_hts[:20], aes(x='factor(hashtag)', y='count')) + \
    geom_bar(stat='identity') + scale_y_continuous(labels='comma') + \
    theme(axis_text_x=element_text(angle=45, hjust=1)) + xlab('Hashtag') + \
    ylab('Count') + ggtitle('Top 20 hashtags in all tweets related to Shellshock')

# Top 20 Hashtags in Unique Tweets
all_tags = pd.Series([ht for hts in uniqtweetsDF['hashtags']
                        for ht in hts.split(" ")])
all_tags = all_tags[all_tags.map(len) > 0]
all_tags.reset_index(drop=True, inplace=True)

top_100_hts = pd.value_counts(all_tags)[:100]
top_100_hts = top_100_hts.reset_index()
top_100_hts.columns = ['hashtag', 'count']
ggplot(top_100_hts[:20], aes(x='factor(hashtag)', y='count')) + \
    geom_bar(stat='identity') + scale_y_continuous(labels='comma') + \
    theme(axis_text_x=element_text(angle=45, hjust=1)) + xlab('Hashtag') + \
    ylab('Count') + ggtitle('Top 20 hashtags in unique tweets related to Shellshock')

# Top 20 urls in Tweets & Retweets
all_urls = pd.Series([url for urls in tweetsDF['urls']
                        for url in urls.split(" ")])
all_urls = all_urls[all_urls.map(len) > 0]
all_urls.reset_index(drop=True, inplace=True)

top_100_urls = pd.value_counts(all_urls)[:100]
top_100_urls = top_100_urls.reset_index()
top_100_urls.columns = ['url', 'count']
ggplot(top_100_urls[:20], aes(x='factor(url)', y='count')) + \
    geom_bar(stat='identity') + scale_y_continuous(labels='comma') + \
    theme(axis_text_x=element_text(angle=45, hjust=1)) + xlab('Url') + \
    ylab('Count') + ggtitle('Top 20 urls in all tweets related to Shellshock')

# Top 20 urls in Unique Tweets
all_urls = pd.Series([url for urls in uniqtweetsDF['urls']
                        for url in urls.split(" ")])
all_urls = all_urls[all_urls.map(len) > 0]
all_urls.reset_index(drop=True, inplace=True)

top_100_urls = pd.value_counts(all_urls)[:100]
top_100_urls = top_100_urls.reset_index()
top_100_urls.columns = ['url', 'count']
ggplot(top_100_urls[:20], aes(x='factor(url)', y='count')) + \
    geom_bar(stat='identity') + scale_y_continuous(labels='comma') + \
    theme(axis_text_x=element_text(angle=45, hjust=1)) + xlab('Url') + \
    ylab('Count') + ggtitle('Top 20 urls in unique tweets related to Shellshock')
