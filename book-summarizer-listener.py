from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from requests_oauthlib import OAuth1Session
import tweepy
import requests
import os
import json
import re
import os
from dotenv import load_dotenv

print(os.getenv('TWITTER_CONSUMER_KEY'))

load_dotenv()

TWITTER_CONSUMER_KEY=os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET=os.getenv('TWITTER_CONSUMER_SECRET');
TWITTER_ACCESS_TOKEN=os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
TWITTER_WEBHOOK_ENV=os.getenv('TWITTER_WEBHOOK_ENV')
bearer_token=os.getenv('bearer_token')

class Tweet:
    def __init__(self, text, id):
        self.text = text
        self.id = id

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = "Bearer " + bearer_token
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    sample_rules = [
        {"value": "@BookSummBot has:images"},
        # {"value": "cat has:images -grumpy", "tag": "cat pictures"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))

def process_images(images):
    for image in images:
        print("processing image ... " , image);
    return "Finished processing image"

def extract_image(tweet):

    tweet_text = str(tweet.text)
    print("tweet text in extract_image " , tweet_text);
    image_urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', tweet_text)
    print("all image urls : " , image_urls)
    return image_urls

#This method is responsible for processing the tweet.
def process_tweet(tweet):

    tweet_text = tweet.text
    tweet_id = tweet.id

    print("tweet text in process_tweet : " , tweet_text);

    tweet_images = extract_image(tweet)

    result = process_images(tweet_images)

    return result

"""
The ID of an existing status that the update is in reply to.
Note: This parameter will be ignored unless the author of the Tweet this parameter references
is mentioned within the status text. Therefore, you must include @username ,
where username is the author of the referenced Tweet, within the update.
"""

def reply_to_tweet_2(original_tweet,reply):

    tweet_id = original_tweet.id
    username_to_reply_to="BookSummBot";
    print("original tweet id : " , tweet_id, original_tweet)

    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)

    ### at this point I've grabbed the tweet and loaded it to JSON...

    reply_status = "@%s %s" % (username_to_reply_to, reply)
    response = api.update_status(reply_status, tweet_id)
    print("update status response : " , response);

def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print("json response : " , json_response);
            print("data : " , json_response['data'])

            data = json_response['data']
            tweet = Tweet(data.get("text"), data.get("id"))

            response = process_tweet(tweet)

            reply_to_tweet_2(tweet, response)

            print("Received json_response from stream : " , json.dumps(json_response, indent=4, sort_keys=True))

def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    get_stream(set)


if __name__ == "__main__":
    main()