from os import getenv
import basilica 
import twitter_scraper 
from twitter_scraper import get_tweets, Profile
from dotenv import load_dotenv 
from .db_model import db, User, Tweet 

load_dotenv()

BASILICA = basilica.Connection(getenv('BASILICA_KEY'))

def add_user_twitter_scraper(username):
    """Add a user and their tweets to database."""
    try:
        # Get user profile   
        user_profile = Profile(username)

        # add to user table. 
        db_user = (User.query.get(user_profile.user_id) or
                   User(id=user_profile.user_id,
                        username=username,
                        follower_count=user_profile.followers_count))
        db.session.add(db_user)

        # Get most recent tweets
        tweets = list(get_tweets(username, pages=2))
        original_tweets = [d for d in tweets if d['username']==username]

        # Get an example Basilica embedding for first tweet
        for tweet in original_tweets: 
            embedding = BASILICA.embed_sentence(tweet['text'], model='twitter')
            
         # Add tweet info to Tweet table
            db_tweet = Tweet(id=tweet['tweetId'],
                            text=tweet['text'],
                            embedding=embedding)
            db_user.tweet.append(db_tweet)
            db.session.add(db_tweet)
        db.session.commit()
    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e

    return original_tweets, embedding