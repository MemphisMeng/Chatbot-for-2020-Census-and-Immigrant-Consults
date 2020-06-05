from flask import Flask, request
from pymessenger.bot import Bot
import requests
from FBMessengerChatbot.TFIDF.Transformer import Transformer
from language_detector import detect_language
import os

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)
transformer = Transformer('FBMessengerChatbot/data/train/QnA.csv', 'FBMessengerChatbot/data/train/ChineseQnA.txt',
                          'FBMessengerChatbot/data/train/SpanishQnA.csv')


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for item in output.items():
            print(item)
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        # NLP detection
                        if message['message'].get('nlp'):
                            # greeting detected
                            if message['message']['nlp']['entities'].get('greetings') and \
                                    message['message']['nlp']['entities']['greetings'][0]['confidence'] >= 0.9:
                                if len(message['message']['nlp']['detected_locales']) != 0:
                                    if detect_language(message['message'].get('text')) == 'English':
                                        bot.send_text_message(recipient_id, "Hello! Nice to meet you!")
                                    elif detect_language(message['message'].get('text')) == 'Mandarin':
                                        bot.send_text_message(recipient_id, "您好！很高兴为您服务！")
                                    elif detect_language(message['message'].get('text')) == 'Spanish':
                                        bot.send_text_message(recipient_id, "¡Mucho gusto! ¿Cómo estás?")
                                    continue
                            # bye detected
                            if message['message']['nlp']['entities'].get('bye') and \
                                    message['message']['nlp']['entities']['bye'][0]['confidence'] >= 0.9:
                                if len(message['message']['nlp']['detected_locales']) != 0:
                                    if detect_language(message['message'].get('text')) == 'English':
                                        bot.send_text_message(recipient_id, "See you next time!")
                                    elif detect_language(message['message'].get('text')) == 'Mandarin':
                                        bot.send_text_message(recipient_id, "再见！")
                                    elif detect_language(message['message'].get('text')) == 'Spanish':
                                        bot.send_text_message(recipient_id, "¡Adiós!")
                                    continue
                            # thank detected
                            if message['message']['nlp']['entities'].get('thanks') and \
                                    message['message']['nlp']['entities']['thanks'][0]['confidence'] >= 0.9:
                                if len(message['message']['nlp']['detected_locales']) != 0:
                                    if detect_language(message['message'].get('text')) == 'English':
                                        bot.send_text_message(recipient_id, "You are welcome!")
                                    elif detect_language(message['message'].get('text')) == 'Mandarin':
                                        bot.send_text_message(recipient_id, "不用谢！")
                                    elif detect_language(message['message'].get('text')) == 'Spanish':
                                        bot.send_text_message(recipient_id, "¡De nada!")
                                    continue

                        response, similarity = transformer.match_query(message['message'].get('text'))
                        if similarity < 0.5:
                            persona_id = create_handler() # create a persona
                            response = "Please wait! Our representative is on the way to help you!"
                            bot.send_text_message(recipient_id, response)
                        else:
                            responses = response.split('|')
                            for r in responses:
                                if r != '':
                                    bot.send_text_message(recipient_id, r.strip())
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        i = 0
                        while i < 1:
                            bot.send_text_message(recipient_id, "Interesting! Anything else I could help?")
                            i += 1
    return "Message Processed"


@app.route("/personas", methods=['POST'])
def create_handler():
    request_body = {
        'name': 'Harry P.',
        'profile_picture_url': 'https://www.facebook.com/photo?fbid=854028385032438&set=a.129292634172687'
    }
    response = requests.post('https://graph.facebook.com/me/personas?access_token='+ACCESS_TOKEN,
                             json=request_body).json()
    return response


@app.route("/messages", methods=['POST'])
def invoke_handler(recipient, persona, message):
    request_body = {
        'recipient': {
            'id': recipient
        },
        "message":{
            "text": message
        },
        'persona_id': persona
    }
    response = requests.post('https://graph.facebook.com/me/personas?access_token=' + ACCESS_TOKEN,
                             json=request_body).json()
    return response

def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Connected sucessfully!'


if __name__ == "__main__":
    app.run()
