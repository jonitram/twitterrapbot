import string
import config
import pronouncing as p
import pickle
import random

input_file = 'rap_lyrics.txt'

LINE_LENGTH = [6, 8]
markov_index = dict()
rhyme_index = dict()
index = []

# creation of a new index
def add_markov(key, value):
    if key in markov_index:
        if value in markov_index[key]:
            markov_index[key][value] += 1
        else:
            markov_index[key][value] = 1
    else:
        entry = dict()
        entry[value] = 1
        markov_index[key] = entry
    
def save(filename):
    index.append(markov_index)
    index.append(rhyme_index)
    with open(filename, "wb") as f:
        pickle.dump(index, f, pickle.HIGHEST_PROTOCOL)

def load(filename):
    global markov_index, rhyme_index
    with open(filename, "rb") as f:
        dump = pickle.load(f)
        markov_index = dump[0]
        rhyme_index = dump[1]

def add_rhyme(word):
    # removing 'i' & 'a'
    if len(word) == 1 and word not in 'ia':
        return
    phones = p.phones_for_word(word)
    if len(phones) != 0:
        phones = phones[0].split(" ")
        i = len(phones) - 1
        stub = ""
        while i >= 0:
            if any(char.isdigit() for char in phones[i]):
                if (stub+phones[i]) in rhyme_index:
                    rhyme_index[stub+phones[i]].add(word)
                else:
                    rhyme_index[stub+phones[i]] = set([word])
                break
            stub += phones[i]
            i -= 1

# generation of lyrics
def markov_next(word, no_stop=False, always_stop=False):
    if word not in markov_index:
        raise RuntimeError

    choices = []
    for key in markov_index[word]:
        for i in range(markov_index[word][key]):
            if no_stop and key == '--':
                None # don't add
            else:
                choices.append(key)
    if always_stop and '--' in choices:
        return '--'
    else:
        if len(choices) == 0:
            return '--'
        return random.choice(choices)
    
def get_phonetic_end(word):
    phones = p.phones_for_word(word)
    if len(phones) != 0:
        phones = phones[0].split(" ")
        i = len(phones) - 1
        stub = ""
        while i >= 0:
            if any(char.isdigit() for char in phones[i]):
                if (stub+phones[i]) in rhyme_index:
                    return stub+phones[i]
            stub += phones[i]
            i -= 1
    return None

def get_rhyming_words(word):
    end = get_phonetic_end(word)
    words = [word for word in rhyme_index[end]]
    return words

def get_random_rhyming_words(num=2):
    vowels = [key for key in rhyme_index]
    while len(vowels) > 0:
        choice = random.choice(vowels)
        if len(rhyme_index[choice]) < num:
            vowels.remove(choice)
        else:
            words = [word for word in rhyme_index[choice]]
            return_list = []
            while len(return_list) < num:
                word_choice = random.choice(words)
                return_list.append(word_choice)
                words.remove(word_choice)
            return return_list
    return None

def get_bars(chosen_words=None, num_bars=2):
    end_words = []
    if chosen_words == None or len(chosen_words) == 0:
        if num_bars == 1:
            end_words.extend(get_random_rhyming_words(num=4))
        else:
            for i in range(num_bars):
                end_words.extend(get_random_rhyming_words(num=2))
    else:
        if len(chosen_words) == 2:
            end_words.extend(chosen_words)
            for word in chosen_words:
                end_words.append(random.choice(get_rhyming_words(word)))
        elif len(chosen_words) == 1:
            end_words.extend(chosen_words)
            random_words = get_rhyming_words(end_words[0])
            for i in range(3):
                random_word = random.choice(random_words)
                end_words.append(random_word)
                random_words.remove(random_word)
    bars = []
    for word in end_words:
        current_line = word
        current_word = word
        num_words = 1
        # real word
        while current_word != '--':
            # more space in the line; keep going
            if num_words < LINE_LENGTH[0]:
                current_word = markov_next(current_word, no_stop=True)
            # no more space in the line; stop
            elif num_words > LINE_LENGTH[1]:
                current_word = markov_next(current_word, always_stop=True)
            # in the middle; keep going or stop
            else:
                current_word = markov_next(current_word)
            # don't add non-lyrics
            if current_word != '--' and current_word != " ":
                current_line = current_word + " " + current_line
                num_words += 1
        # this line is done
        bars.append(current_line) 
    return bars

def get_lyrics(end_words=None):
    index_name = input_file[0:(len(input_file)-4)]+".ind"

    if not config.os.path.exists(index_name):
        with open(input_file, "r") as f:
            for line in f:
                line = line.replace("\s+", " ")
                if line.strip() != "":
                    words = line.split(" ")
                    i = len(words) - 1
                    if i > 0:
                        add_rhyme(words[i].strip().lower())
                    while i > 0:
                        add_markov(words[i].strip().lower(), words[i-1].strip().lower())
                        i -= 1
                    add_markov(words[i].strip().lower(), "--")
        save(index_name)
    else:
        load(index_name)

    lyrics = []
    # number of verses to generate
    for i in range(1):
        # pick a rhyme scheme randomly
        if end_words == None or len(end_words) == 0:
            rhyme_scheme = random.randint(1,4)
        elif len(end_words) == 1:
            rhyme_scheme = 1
        else:
            rhyme_scheme = random.randint(2,4)
        if rhyme_scheme == 1: #AAAA
            lyrics.extend(get_bars(chosen_words=end_words,num_bars=1))
        elif rhyme_scheme == 2: #AABB
            lyrics.extend(get_bars(chosen_words=end_words,num_bars=2))
        elif rhyme_scheme == 3: #ABAB
            lyrics.extend(get_bars(chosen_words=end_words,num_bars=2))
            temp = lyrics[2]
            lyrics [2] = lyrics[1]
            lyrics [1] = temp
        elif rhyme_scheme == 4: #ABBA
            lyrics.extend(get_bars(chosen_words=end_words,num_bars=2))
            temp = lyrics[1]
            lyrics[1] = lyrics[3]
            lyrics[3] = temp
        # censoring
        for i in range(len(lyrics)):
            if "nigg" in lyrics[i]:
                lyrics[i] = lyrics[i].replace("nigg","n*gg")
            if "fag" in lyrics[i]:
                lyrics[i] = lyrics[i].replace("fag","f*g")
    return lyrics

def print_lyrics(final_lyrics):
    for i in range((len(final_lyrics))):
        print(final_lyrics[i])

def process_mentions(client):
    result = []
    mentions = client.mentions_timeline()
    done = False
    if len(mentions) > 0:
        tweet = mentions[0]
    else:
        done = True
    while not done:
        if tweet.favorited:
            return result
        if tweet not in result:
            result.insert(0,tweet)
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
    for i in range(len(result)):
        result[i] = result[i].lower()
    return result

def polling(event, context):
    main()
    return

def tweet_random_verse(event, context):
    client = config.login()
    new_tweet = ""
    new_tweet_list = get_lyrics()
    for bar in new_tweet_list:
        new_tweet += bar
        new_tweet += "\n"
    tweet = client.update_status(status=new_tweet)
    client.create_favorite(tweet.id)
    return

def main():
    client = config.login()
    tweets = process_mentions(client)
    for i in range(len(tweets)):
        client.create_favorite(tweets[i].id)
        new_tweet = "https://twitter.com/"
        new_tweet += tweets[i].user.screen_name
        new_tweet += "/status/"
        new_tweet += str(tweets[i].id)
        words = extract_words(tweets[i])
        new_tweet += "\n"
        try:
            new_tweet_list = get_lyrics(words)
        except (RuntimeError, KeyError, IndexError):
            new_tweet += "One of your requested words cannot be used. Here's a random verse instead:\n"
            new_tweet_list = get_lyrics()
            for bar in new_tweet_list:
                new_tweet += bar
                new_tweet += "\n"
        else:
            for bar in new_tweet_list:
                new_tweet += bar
                new_tweet += "\n"
        tweet = client.update_status(status=new_tweet)
        client.create_favorite(tweet.id)
    return

if __name__ == "__main__":
    words = ['shrek','god']
    print_lyrics(get_lyrics(words))
