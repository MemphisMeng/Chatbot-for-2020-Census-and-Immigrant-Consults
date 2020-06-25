from flask import Flask, request
from pymessenger.bot import Bot
from FBMessengerChatbot.TFIDF.Transformer import Transformer
from translate import Translator
import os

en_translator = Translator(to_lang="en")
zh_translator = Translator(to_lang='zh')
es_translator = Translator(to_lang='es')
# define on heroku settings tab
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']


app = Flask(__name__)
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
        print('OUTPUT', output)
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        # NLP detection
                        if message['message'].get('nlp'):
                            try:
                                # detected English
                                if 'en' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    # greeting detected
                                    if message['message']['nlp']['entities'].get('greetings') and \
                                            message['message']['nlp']['entities']['greetings'][0]['confidence'] >= 0.9:
                                        bot.send_text_message(recipient_id, "Hello! Nice to meet you!")
                                        continue
                                    # bye detected
                                    elif message['message']['nlp']['entities'].get('bye') and \
                                            message['message']['nlp']['entities']['bye'][0]['confidence'] >= 0.9:
                                        bot.send_text_message(recipient_id, "See you next time!")
                                        continue
                                    # thank detected
                                    elif message['message']['nlp']['entities'].get('thanks') and \
                                            message['message']['nlp']['entities']['thanks'][0]['confidence'] >= 0.9:
                                        bot.send_text_message(recipient_id, "You are welcome!")
                                        continue
                                # detected Spanish
                                elif 'es' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    # greeting detected
                                    if message['message']['nlp']['entities'].get('greetings') and \
                                            message['message']['nlp']['entities']['greetings'][0]['confidence'] >= 0.6:
                                        bot.send_text_message(recipient_id, "¡Mucho gusto! ¿Cómo estás?")
                                        continue
                                    elif message['message']['nlp']['entities'].get('bye') and \
                                            message['message']['nlp']['entities']['bye'][0]['confidence'] >= 0.6:
                                        bot.send_text_message(recipient_id, "¡Adiós!")
                                        continue
                                    elif message['message']['nlp']['entities'].get('thanks') and \
                                            message['message']['nlp']['entities']['thanks'][0]['confidence'] >= 0.6:
                                        bot.send_text_message(recipient_id, "¡De nada!")
                                        continue
                                # detected Chinese
                                elif 'zh' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    # greeting detected
                                    if message['message']['nlp']['entities'].get('greetings') and \
                                            message['message']['nlp']['entities']['greetings'][0]['confidence'] >= 0.5:
                                        bot.send_text_message(recipient_id, "您好！很高兴为您服务！")
                                        continue
                                    elif message['message']['nlp']['entities'].get('bye') and \
                                            message['message']['nlp']['entities']['bye'][0]['confidence'] >= 0.5:
                                        bot.send_text_message(recipient_id, "再见！")
                                        continue
                                    elif message['message']['nlp']['entities'].get('thanks') and \
                                            message['message']['nlp']['entities']['thanks'][0]['confidence'] >= 0.5:
                                        bot.send_text_message(recipient_id, "不用谢！")
                                        continue
                            except KeyError:
                                print('NLP is not deployed.')

                        response, similarity = transformer.match_query(message['message'].get('text'))
                        if message['message'].get('nlp'):
                            if 'zh' in message['message']['nlp']['detected_locales'][0]['locale']:
                                translated_query = en_translator.translate(message['message'].get('text'))
                                response, similarity = transformer.match_query(translated_query)
                                print('second similarity', similarity)
                                response = zh_translator.translate(response)

                        # no acceptable answers found in the pool
                        if similarity < 0.5:
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


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Connected sucessfully!'


if __name__ == "__main__":
    app.run()
