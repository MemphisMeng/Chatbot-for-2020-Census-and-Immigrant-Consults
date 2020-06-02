from flask import Flask, request
from pymessenger.bot import Bot
from FBMessengerChatbot.TFIDF.Transformer import Transformer

app = Flask(__name__)
ACCESS_TOKEN = 'EAAlE2KkA5dYBAI6q0sW3hOFsMBGhXpHHVuLK9cQLiwjdvhXjyZC7f0enLVm7mDVe3EPP6hObCCTK4dRTZBOQrqUFyErweY9Pf04ObTaZCJvJOSPYohhoFZBQjHxvVuy7vITHgv4whpZAnfS60pU56I4kdDC1D4vcbuHmgSaZAR92BUI8NIZBEVg'
VERIFY_TOKEN = 'L1ZOlsiRrlBSbs/xFesH6jjkDm1OzJlwEmPa93iBNz4='
bot = Bot(ACCESS_TOKEN)
transformer = Transformer('FBMessengerChatbot/data/train/QnA.csv', 'FBMessengerChatbot/data/train/ChineseQnA.csv')


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
                                    message['message']['nlp']['entities']['greetings'][0]['confidence'] >= 0.7:
                                if 'en' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    bot.send_text_message(recipient_id, "Hello! Nice to meet you!")
                                elif 'zh' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    bot.send_text_message(recipient_id, "您好！很高兴为您服务！")
                                elif 'es' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    bot.send_text_message(recipient_id, "¡Mucho gusto! ¿Cómo estás?")
                                continue
                            # bye detected
                            if message['message']['nlp']['entities'].get('bye') and \
                                    message['message']['nlp']['entities']['bye'][0]['confidence'] >= 0.7:
                                if 'en' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    bot.send_text_message(recipient_id, "See you next time!")
                                elif 'zh' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    bot.send_text_message(recipient_id, "再见！")
                                elif 'es' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    bot.send_text_message(recipient_id, "¡Adiós!")
                                continue
                            # thank detected
                            if message['message']['nlp']['entities'].get('thanks') and \
                                    message['message']['nlp']['entities']['thanks'][0]['confidence'] >= 0.7:
                                if 'en' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    bot.send_text_message(recipient_id, "You are welcome!")
                                elif 'zh' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    bot.send_text_message(recipient_id, "不用谢！")
                                elif 'es' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    bot.send_text_message(recipient_id, "¡De nada!")
                                continue
                        response = transformer.match_query(message['message'].get('text'))
                        bot.send_text_message(recipient_id, response)
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
