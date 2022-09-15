import pymysql
import json

with open('event_data_creds.json', 'r') as creds_file:
    creds = json.load(creds_file)

ENDPOINT = creds["body"]["endpoint"] 
USER = creds["body"]["user"] 
DBNAME = creds["body"]["dbname"] 
PASSWORD = creds["body"]["password"]

# Establishes connection with MqSQL database and creates tables. 

connection = pymysql.connect(host=ENDPOINT, user=USER, passwd=PASSWORD, db=DBNAME)

cursor = connection.cursor()

sql_tweets = "CREATE table tweets (tweet_id VARCHAR(50) NOT NULL, tweet_text VARCHAR(280) NOT NULL, author_id VARCHAR(50), conversation_id VARCHAR(50), created_at DATETIME, geo_place_id VARCHAR(50), in_reply_to_user_id VARCHAR(50), lang VARCHAR(10), like_count INT, reply_count INT, quote_count INT, retweet_count INT, possibly_sensitive VARCHAR(10), reply_settings VARCHAR(20), source VARCHAR(100), tweet_url VARCHAR(100), PRIMARY KEY (tweet_id))"

sql_context_annotations = "CREATE table context_annotations (tweet_id VARCHAR(50) NOT NULL, domain_id VARCHAR(50), domain_name VARCHAR(50), domain_description VARCHAR(200), entity_id VARCHAR(50), entity_name VARCHAR(50))"

sql_entities_annotations = "CREATE table entities_annotations (tweet_id VARCHAR(50) NOT NULL, start INT, end INT, probability INT, type VARCHAR(20), normalized_text VARCHAR(50))"

sql_entities_cashtags = "CREATE table entities_cashtags (tweet_id VARCHAR(50) NOT NULL, start INT, end INT, cashtag VARCHAR(50))"

sql_entities_hashtags = "CREATE table entities_hashtags (tweet_id VARCHAR(50) NOT NULL, start INT, end INT, hashtag VARCHAR(50))"

sql_entities_mentions = "CREATE table entities_mentions (tweet_id VARCHAR(50) NOT NULL, start INT, end INT, username VARCHAR(50), user_id VARCHAR(50))"

sql_entities_urls = "CREATE table entities_urls (tweet_id VARCHAR(50) NOT NULL, start INT, end INT, url VARCHAR(100), expanded_url VARCHAR(200), display_url VARCHAR(200), status VARCHAR(50), title VARCHAR(200), description VARCHAR(500), unwound_url VARCHAR(500))"

sql_referenced_tweets = "CREATE table referenced_tweets (tweet_id VARCHAR(50) NOT NULL, referenced_tweet_type VARCHAR(50), referenced_tweet_id VARCHAR(50))"

sql_users = "CREATE table users(user_id VARCHAR(50) NOT NULL, name VARCHAR(100) NOT NULL, username VARCHAR(50) NOT NULL, created_at DATETIME, description VARCHAR(300), location VARCHAR(200), pinned_tweet_id VARCHAR(50), profile_image_url VARCHAR(300), protected VARCHAR(20), followers_count INT, following_count INT, tweet_count INT, listed_count INT, url VARCHAR(200), verified VARCHAR(20), PRIMARY KEY (user_id))"

cursor.execute(sql_tweets)

cursor.execute(sql_context_annotations)

cursor.execute(sql_entities_annotations)

cursor.execute(sql_entities_cashtags)

cursor.execute(sql_entities_hashtags)

cursor.execute(sql_entities_mentions)

cursor.execute(sql_entities_urls)

cursor.execute(sql_referenced_tweets)

cursor.execute(sql_users)

connection.commit()

connection.close()

print("Success")