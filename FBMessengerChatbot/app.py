import random
from flask import Flask, request
import nltk
import string
import numpy as np
from pymessenger.bot import Bot
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
ACCESS_TOKEN = 'EAAlE2KkA5dYBAI6q0sW3hOFsMBGhXpHHVuLK9cQLiwjdvhXjyZC7f0enLVm7mDVe3EPP6hObCCTK4dRTZBOQrqUFyErweY9Pf04ObTaZCJvJOSPYohhoFZBQjHxvVuy7vITHgv4whpZAnfS60pU56I4kdDC1D4vcbuHmgSaZAR92BUI8NIZBEVg'
VERIFY_TOKEN = 'L1ZOlsiRrlBSbs/xFesH6jjkDm1OzJlwEmPa93iBNz4='
bot = Bot(ACCESS_TOKEN)

f = open('chatbot.txt', 'r', errors='ignore')
raw = f.read().lower()
nltk.download('punkt')
nltk.download('wordnet')

sent_tokens = nltk.sent_tokenize(raw)
word_tokens = nltk.word_tokenize(raw)

lemmer = nltk.stem.WordNetLemmatizer()

GREETING_INPUTS = ('hello', 'hi', 'greetings', 'sup', "what's up", 'hey', 'hola', 'ciao',)
GREETING_OUTPUTS = ['hi', 'hey', '*nods*', 'hi there', 'hello', "I'm glad to talk with you!"]

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook.""" 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    # response_sent_text = get_message()
                    send_message(recipient_id, message['message'].get('text'))
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    # response_sent_nontext = get_message()
                    send_message(recipient_id, message['message'].get('attachments'))
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.", "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    if type(response) is not str:
        bot.send_text_message(recipient_id, "Interesting picture! Is there anything else that I could help?")
    bot_response = ''
    sent_tokens.append(response)

    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    if (req_tfidf == 0):
        bot_response = bot_response + "I'm sorry! I don't understand you."
        return bot_response
    else:
        bot_response = bot_response + sent_tokens[idx]
    bot.send_text_message(recipient_id, bot_response)
    return "success"

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

def LemNormalize(text):
    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_OUTPUTS)


if __name__ == "__main__":
    app.run()