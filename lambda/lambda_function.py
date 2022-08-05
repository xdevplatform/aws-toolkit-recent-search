import sys
import json
import pymysql
import requests

def lambda_handler(event, context):
    print("Parsing event json...")
    body = json.loads(event["body"])
    print("Received body:")
    print(body)
    query = body["query"] 
    max_results = body["max_results"] 
    start_time = body["start_time"] 
    end_time = body["end_time"]  

    ENDPOINT = body["endpoint"] 
    USER = body["user"] 
    DBNAME = body["dbname"] 
    PASSWORD = body["password"] 

    BEARER_TOKEN = body["bearer_token"] 

    def get_oauth2_bearer_token(r):
        
        r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
        return r

    def recent_search(query_params):
        url = "https://api.twitter.com/2/tweets/search/recent?tweet.fields=id,text,attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,withheld&expansions=author_id,referenced_tweets.id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username,referenced_tweets.id.author_id&media.fields=media_key,type,duration_ms,height,preview_image_url,url,public_metrics,width,alt_text&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type&poll.fields=duration_minutes,end_datetime,id,options,voting_status&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
        auth = get_oauth2_bearer_token
        headers = {"Content-Type": "application/json"}
        print(f"Running request for url: {url}")
        print(f"With query params: {query_params}")
        return requests.request(
                "GET",
                url = url,
                params = query_params,
                headers = headers,
                auth = auth
            )

    def put_tweets(query, max_results, start_time, end_time):

        request_count = 0

        query_parameters = {
            "query": query,
            "max_results": max_results,
            "start_time": start_time,
            "end_time": end_time
            }

        while True:
            response = recent_search(query_parameters)
            if response.status_code != 200:
                print(response)
                raise Exception(response.status_code, response.text)
            request_count += 1
            print("Request count:", request_count)
            response_payload = response.json()
            meta = response_payload["meta"]
            data = response_payload["data"]
            users = response_payload["includes"]["users"]
            if meta["result_count"] == 0:
                sys.exit("No results to analyze.")

            # Send results to database
            connection = pymysql.connect(host=ENDPOINT, user=USER, passwd=PASSWORD, db=DBNAME)
            cursor = connection.cursor()

            sql_tweets = "REPLACE INTO tweets (tweet_id, tweet_text, author_id, conversation_id, created_at, geo_place_id, in_reply_to_user_id, lang, like_count, reply_count, quote_count, retweet_count, possibly_sensitive, reply_settings, source, tweet_url) VALUES \n"
            
            sql_annotations = "REPLACE INTO context_annotations (tweet_id, domain_id, domain_name, domain_description, entity_id, entity_name) VALUES \n"

            sql_referenced_tweets = "REPLACE INTO referenced_tweets (tweet_id, referenced_tweet_type, referenced_tweet_id) VALUES \n"
            
            sql_entities = "REPLACE INTO entities_annotations (tweet_id, start, end, probability, type, normalized_text) VALUES \n"

            sql_cashtags = "REPLACE INTO entities_cashtags (tweet_id, start, end, cashtag) VALUES \n"

            sql_hashtags = "REPLACE INTO entities_hashtags (tweet_id, start, end, hashtag) VALUES \n"

            sql_mentions = "REPLACE INTO entities_mentions (tweet_id, start, end, username, user_id) VALUES \n"

            sql_urls = "REPLACE INTO entities_urls (tweet_id, start, end, url, expanded_url, display_url, status, title, description, unwound_url) VALUES \n"

            for tweet in data:

                tweet_id = tweet["id"]
                tweet_text = connection.escape(tweet["text"])
                author_id = connection.escape(tweet["author_id"])
                lang = connection.escape(tweet["lang"])
                created_at = connection.escape(tweet["created_at"])
                like_count = connection.escape(tweet["public_metrics"]["like_count"])
                reply_count = connection.escape(tweet["public_metrics"]["reply_count"])
                quote_count = connection.escape(tweet["public_metrics"]["quote_count"])
                retweet_count = connection.escape(tweet["public_metrics"]["retweet_count"])
                try: 
                    geo_place_id = connection.escape(tweet["geo"]["place_id"])
                except: 
                    geo_place_id = 'NULL'
                try:
                    conversation_id = connection.escape(tweet["conversation_id"])
                except: 
                    conversation_id = 'NULL'
                try:
                    in_reply_to_user_id = connection.escape(tweet["in_reply_to_user_id"])
                except: 
                    in_reply_to_user_id = 'NULL'
                try: 
                    possibly_sensitive = connection.escape(tweet["possibly_sensitive"])
                except: 
                    possibly_sensitive = 'NULL'
                try:
                    reply_settings = connection.escape(tweet["reply_settings"])
                except: 
                    reply_settings = 'NULL'
                try:
                    source = connection.escape(tweet["source"])
                except: 
                    source = 'NULL'
                tweet_url = connection.escape(f"https://twitter.com/twitter/status/{tweet_id}")
                sql_tweets += f"({tweet_id}, {tweet_text}, {author_id}, {conversation_id}, {created_at}, {geo_place_id}, {in_reply_to_user_id}, {lang}, {like_count}, {reply_count}, {quote_count}, {retweet_count}, {possibly_sensitive}, {reply_settings}, {source}, {tweet_url}), \n"
                
                if "context_annotations" in tweet:
                    for anno in tweet["context_annotations"]:
                        domain_id = connection.escape(anno["domain"]["id"])
                        domain_name = connection.escape(anno["domain"]["name"]) 
                        try:
                            domain_description = connection.escape(anno["domain"]["description"])
                        except:
                            domain_description = "NULL"
                        entity_id = connection.escape(anno["entity"]["id"])
                        entity_name = connection.escape(anno["entity"]["name"])
                        sql_annotations += f"({tweet_id}, {domain_id}, {domain_name}, {domain_description}, {entity_id}, {entity_name}), \n"
                    else:
                        pass
                else:
                    pass

                if "referenced_tweets" in tweet: 
                    referenced_tweets = tweet["referenced_tweets"]
                    for ref_tweet in referenced_tweets: 
                        referenced_tweet_type = connection.escape(ref_tweet["type"])
                        referenced_tweet_id = connection.escape(ref_tweet["id"])
                        sql_referenced_tweets += f"({tweet_id}, {referenced_tweet_type}, {referenced_tweet_id}), \n"
                else:
                    pass

                if "entities" in tweet:
                    if "annotations" in tweet["entities"]:
                        for anno in tweet["entities"]["annotations"]:
                            start =  connection.escape(anno["start"])
                            end = connection.escape(anno["end"])
                            probability = connection.escape(anno["probability"])
                            type = connection.escape(anno["type"])
                            normalized_text = connection.escape(anno["normalized_text"])
                            sql_entities += f"({tweet_id}, {start}, {end}, {probability}, {type}, {normalized_text}), \n"
                    else:
                        pass

                    if "cashtags" in tweet["entities"]:
                        for cashtg in tweet["entities"]["cashtags"]:
                            start =  connection.escape(cashtg["start"])
                            end = connection.escape(cashtg["end"])
                            cashtag = connection.escape(cashtg["tag"])
                            sql_cashtags += f"({tweet_id}, {start}, {end}, {cashtag}), \n"
                    else:
                        pass

                    if "hashtags" in tweet["entities"]:
                        for hashtg in tweet["entities"]["hashtags"]:
                            start =  connection.escape(hashtg["start"])
                            end = connection.escape(hashtg["end"])
                            hashtag = connection.escape(hashtg["tag"])
                            sql_hashtags += f"({tweet_id}, {start}, {end}, {hashtag}), \n"
                    else:
                        pass

                    if "mentions" in tweet["entities"]:
                        for ment in tweet["entities"]["mentions"]:
                            start =  connection.escape(ment["start"])
                            end = connection.escape(ment["end"])
                            username = connection.escape(ment["username"])
                            user_id = connection.escape(ment["id"])
                            sql_mentions += f"({tweet_id}, {start}, {end}, {username}, {user_id}), \n"
                    else:
                        pass

                    if "urls" in tweet["entities"]:
                        for u in tweet["entities"]["urls"]:
                            start =  connection.escape(u["start"])
                            end = connection.escape(u["end"])
                            url = connection.escape(u["url"])
                            try:
                                expanded_url = connection.escape(u["expanded_url"])
                            except: 
                                expanded_url = "NULL"
                            try:
                                display_url = connection.escape(u["display_url"])
                            except:
                                display_url = "NULL"
                            try:
                                status = connection.escape(u["status"])
                            except:
                                status = "NULL"
                            try: 
                                title = connection.escape(u["title"])
                            except:
                                title = "NULL"
                            try: 
                                description = connection.escape(u["description"])
                            except: 
                                description = "NULL"
                            try: 
                                unwound_url = connection.escape(u["unwound_url"])
                            except: 
                                unwound_url = "NULL"
                            sql_urls += f"({tweet_id}, {start}, {end}, {url}, {expanded_url}, {display_url}, {status}, {title}, {description}, {unwound_url}), \n"
                    else:
                        pass
                else: 
                    pass 

            sql_tweets = sql_tweets[:-3] + ";"

            sql_annotations = sql_annotations[:-3] + ";"

            sql_referenced_tweets = sql_referenced_tweets[:-3] + ";"

            sql_entities = sql_entities[:-3] + ";"

            sql_cashtags = sql_cashtags[:-3] + ";"

            sql_hashtags = sql_hashtags[:-3] + ";"

            sql_mentions = sql_mentions[:-3] + ";"

            sql_urls = sql_urls[:-3] + ";"

            sql_users = "REPLACE INTO users (user_id, name, username, created_at, description, location, pinned_tweet_id, profile_image_url, protected, followers_count, following_count, tweet_count, listed_count, url, verified) VALUES \n"

            for user in users:

                user_id = connection.escape(user["id"])
                name = connection.escape(user["name"])
                username = connection.escape(user["username"])
                created_at = connection.escape(user["created_at"])
                followers_count = connection.escape(user["public_metrics"]["followers_count"])
                following_count = connection.escape(user["public_metrics"]["following_count"])
                tweet_count = connection.escape(user["public_metrics"]["tweet_count"])
                listed_count = connection.escape(user["public_metrics"]["listed_count"])
                protected = connection.escape(user["protected"])
                verified = connection.escape(user["verified"])
                try:
                    pinned_tweet_id = connection.escape(user["pinned_tweet_id"])
                except:
                    pinned_tweet_id = 'NULL'
                try:
                    description = connection.escape(user["description"])
                except:
                    description = 'NULL'
                try:
                    location = connection.escape(user["location"])
                except:
                    location = 'NULL' 
                try:
                    profile_image_url = connection.escape(user["profile_image_url"])
                except:
                    profile_image_url = 'NULL'
                try:
                    url = connection.escape(user["url"])
                except:
                    url = 'NULL'

                sql_users += f"({user_id}, {name}, {username}, {created_at}, {description}, {location}, {pinned_tweet_id}, {profile_image_url}, {protected}, {followers_count}, {following_count}, {tweet_count}, {listed_count}, {url}, {verified}), \n"

            sql_users = sql_users[:-3] + ";"

            cursor.execute(sql_tweets)
            try:
                cursor.execute(sql_annotations)
            except:
                pass
            try:
                cursor.execute(sql_referenced_tweets)
            except:
                pass
            try:
                cursor.execute(sql_entities)
            except:
                pass
            try:
                cursor.execute(sql_cashtags)
            except:
                pass
            try:
                cursor.execute(sql_hashtags)
            except:
                pass
            try:
                cursor.execute(sql_mentions)
            except:
                pass
            try:
                cursor.execute(sql_urls)
            except:
                pass
            cursor.execute(sql_users)
            
            connection.commit()
            connection.close()

            #Check for next token and paginate through data if additional data is available
            if "next_token" not in meta:
                break
            next_token = meta["next_token"]
            query_parameters.update(next_token = next_token)
        
        return(request_count)

    request_count = put_tweets(query, max_results, start_time, end_time)
    print(f"Number of requests: {request_count}")