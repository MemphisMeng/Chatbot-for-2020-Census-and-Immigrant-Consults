from flask import Flask, request
import os
from pymessenger.bot import Bot
from TFIDF.Transformer import Transformer

app = Flask(__name__)
ACCESS_TOKEN = 'EAAlE2KkA5dYBAI6q0sW3hOFsMBGhXpHHVuLK9cQLiwjdvhXjyZC7f0enLVm7mDVe3EPP6hObCCTK4dRTZBOQrqUFyErweY9Pf04ObTaZCJvJOSPYohhoFZBQjHxvVuy7vITHgv4whpZAnfS60pU56I4kdDC1D4vcbuHmgSaZAR92BUI8NIZBEVg'
VERIFY_TOKEN = 'L1ZOlsiRrlBSbs/xFesH6jjkDm1OzJlwEmPa93iBNz4='
bot = Bot(ACCESS_TOKEN)
transformer = Transformer('data\\train\\QnA.csv')
dataFile = 'data\\train\\augmented_MIRAquestions.txt'


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
                        # response_sent_text = get_message()
                        response = transformer.match_query(message['message'].get('text'))
                        bot.send_text_message(recipient_id, response)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        # response_sent_nontext = get_message()
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
    return 'Invalid verification token'


if __name__ == "__main__":
    app.run()
