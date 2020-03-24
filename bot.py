import string
import config
import gen_rap
from gen_rap import RapIndex

def process_mentions(client):
    result = []
    mentions = client.mentions_timeline()
    done = False
    if len(mentions) > 0:
        tweet = mentions[0]
    else:
        done = True
    while not done:
        if tweet not in result:
            result.append(tweet)
        if mentions.index(tweet) == (len(mentions) - 1):
            mentions = client.mentions_timeline(max_id=tweet.id)
            # remove duplicate
            mentions.remove(tweet)
            for i in range(len(mentions)):
                print(mentions[i].text)
            if len(mentions) > 0:
                tweet = mentions[0]
            else:
                done = True
        else:
            tweet = mentions[mentions.index(tweet) + 1]
    return result

def extract_words(tweet):
    words = tweet.text.split()
    result = []
    for i in range(len(words)):
        words[i].translate(str.maketrans('', '', string.punctuation))
    if len(words) >= 3:
        result.append(words[1])
        result.append(words[2])
    elif len(words) == 2:
        result.append(words[1])
    return result

def polling(event, context):
    main()
    return

def tweet_random_verse(event, context):
    client = config.login()
    new_tweet = ""
    new_tweet_list = gen_rap.get_lyrics()
    for bar in new_tweet_list:
        new_tweet += bar
        new_tweet += "\n"
    client.update_status(status=new_tweet)
    return

def main():
    client = config.login()
    tweets = process_mentions(client)
    for i in range(len(tweets)):
        new_tweet = "https://twitter.com/"
        new_tweet += tweets[i].user.screen_name
        new_tweet += "/status/"
        new_tweet += str(tweets[i].id)
        words = extract_words(tweets[i])
        new_tweet += "\n"
        try:
            new_tweet_list = gen_rap.get_lyrics(words)
        except (RuntimeError, KeyError, IndexError):
            new_tweet += "One of your requested words cannot be used. Here's a random verse instead:\n"
            new_tweet_list = gen_rap.get_lyrics()
            for bar in new_tweet_list:
                new_tweet += bar
                new_tweet += "\n"
        else:
            for bar in new_tweet_list:
                new_tweet += bar
                new_tweet += "\n"
        client.update_status(status=new_tweet)
        client.create_favorite(tweets[i].id)
    return

if __name__ == "__main__":
    main()
