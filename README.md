# Twitter Rap Bot
## https://twitter.com/scuffedrapbot
### Twitter bot that generates rap verses using a set of up to 2 optional user requested words and tweets them. 
---
- The bot is designed to run on an AWS lambda function, polling every other minute on the odd minute. 
    - The bot takes up under 448 MB per invocation with a 30 second timeout. 
    - Every 2 hours between the hours of 8 AM and 10 PM CST the bot will tweet a randomly generated verse. 
- The bot processes tweets in chronological order and likes tweets that it has finished processing. 
- The bot will retweet with comment the tweet calling it in it's response to a user prompted rap verse.