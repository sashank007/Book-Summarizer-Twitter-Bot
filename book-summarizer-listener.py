from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener


#consumer key, consumer secret, access token, access secret.
ckey=""
csecret=""
atoken=""
asecret=""

class listener(StreamListener):

    #json data
    def on_data(self, data):
        print("data from stream : " , data)
        return(True)

    def on_error(self, status):
        print("Error occcurred" , status)
    
    def on_connection_error(self, status):
        print("Connection error occcurred" , status)

if __name__ == "__main__":
    auth = OAuthHandler(ckey, csecret)
    auth.set_access_token(atoken, asecret)

    twitterStream = Stream(auth, listener())
    twitterStream.filter(to=["booksummarizer"])

# filtering logic : 
# to:	Standalone	Core	Matches any Tweet that is in reply to a particular user.
# The value can be either the username (excluding the @ character) or the user’s numeric user ID.
# You can only pass a single username/ID per to: operator.
# Example: to:twitterdev OR to:twitterapi -to:twitter