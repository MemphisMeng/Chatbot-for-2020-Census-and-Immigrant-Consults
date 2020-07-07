from flask import Flask, request
from pymessenger.bot import Bot
from FBMessengerChatbot.TFIDF.Transformer import Transformer
import os
from flask_mysqldb import MySQL
from datetime import datetime

# import mysql

# define on heroku settings tab
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']

app = Flask(__name__)
bot = Bot(ACCESS_TOKEN)
transformer = Transformer('FBMessengerChatbot/data/train/QnA.csv',
                          'FBMessengerChatbot/data/train/SimplifiedChineseQnA.csv',
                          'FBMessengerChatbot/data/train/traditionalChineseQnA.csv',
                          'FBMessengerChatbot/data/train/SpanishQnA.csv')

# MySQL database
app.config['MYSQL_USER'] = 'sql9353097'
app.config['MYSQL_PASSWORD'] = 'vpwQcdCkMN'
app.config['MYSQL_HOST'] = 'sql9.freemysqlhosting.net'
app.config['MYSQL_DB'] = 'sql9353097'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
MYSQL_TABLE = '\'QnA\''

mysql = MySQL(app)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    cur = mysql.connection.cursor()
    # check if the database exists
    if hasDatabase(cur) is False:
        createDatabase(cursor=cur)
    # check if the table exists
    if hasTable(cur) is False:
        createTable(cur)

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
                        question = message['message'].get('text')

                        # NLP detection
                        if message['message'].get('nlp'):
                            try:
                                # detected English
                                if 'en' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    # greeting detected
                                    if message['message']['nlp']['entities'].get('greetings') and \
                                            message['message']['nlp']['entities']['greetings'][0]['confidence'] >= 0.9:
                                        response = "Hello! Nice to meet you!"
                                        bot.send_text_message(recipient_id, response)
                                        time = datetime.fromtimestamp(int(str(message['timestamp'])[:-3])).strftime(
                                            '%Y-%m-%d %H:%M:%S')
                                        cur.execute('''INSERT INTO {} VALUES ({}, {}, {}, {})'''.format(MYSQL_TABLE,
                                                                                                        message[
                                                                                                            'sender'][
                                                                                                            'id'], time,
                                                                                                        message[
                                                                                                            'message'].get(
                                                                                                            'text'),
                                                                                                        response))
                                        continue
                                    # bye detected
                                    elif message['message']['nlp']['entities'].get('bye') and \
                                            message['message']['nlp']['entities']['bye'][0]['confidence'] >= 0.9:
                                        response = "See you next time!"
                                        bot.send_text_message(recipient_id, response)
                                        time = datetime.fromtimestamp(int(str(message['timestamp'])[:-3])).strftime(
                                            '%Y-%m-%d %H:%M:%S')
                                        cur.execute('''INSERT INTO {} VALUES ({}, {}, {}, {})'''.format(MYSQL_TABLE,
                                                                                                        message[
                                                                                                            'sender'][
                                                                                                            'id'], time,
                                                                                                        message[
                                                                                                            'message'].get(
                                                                                                            'text'),
                                                                                                        response))
                                        continue
                                    # thank detected
                                    elif message['message']['nlp']['entities'].get('thanks') and \
                                            message['message']['nlp']['entities']['thanks'][0]['confidence'] >= 0.9:
                                        response = "You are welcome!"
                                        bot.send_text_message(recipient_id, response)
                                        time = datetime.fromtimestamp(int(str(message['timestamp'])[:-3])).strftime(
                                            '%Y-%m-%d %H:%M:%S')
                                        cur.execute('''INSERT INTO {} VALUES ({}, {}, {}, {})'''.format(MYSQL_TABLE,
                                                                                                        message[
                                                                                                            'sender'][
                                                                                                            'id'], time,
                                                                                                        message[
                                                                                                            'message'].get(
                                                                                                            'text'),
                                                                                                        response))
                                        continue
                                # detected Spanish
                                elif 'es' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    # greeting detected
                                    if message['message']['nlp']['entities'].get('greetings') and \
                                            message['message']['nlp']['entities']['greetings'][0]['confidence'] >= 0.6:
                                        response = "¡Mucho gusto! ¿Cómo estás?"
                                        bot.send_text_message(recipient_id, response)
                                        time = datetime.fromtimestamp(int(str(message['timestamp'])[:-3])).strftime(
                                            '%Y-%m-%d %H:%M:%S')
                                        cur.execute('''INSERT INTO {} VALUES ({}, {}, {}, {})'''.format(MYSQL_TABLE,
                                                                                                        message[
                                                                                                            'sender'][
                                                                                                            'id'], time,
                                                                                                        message[
                                                                                                            'message'].get(
                                                                                                            'text'),
                                                                                                        response))
                                        continue
                                    elif message['message']['nlp']['entities'].get('bye') and \
                                            message['message']['nlp']['entities']['bye'][0]['confidence'] >= 0.6:
                                        response = "¡adíos!"
                                        bot.send_text_message(recipient_id, response)
                                        time = datetime.fromtimestamp(int(str(message['timestamp'])[:-3])).strftime(
                                            '%Y-%m-%d %H:%M:%S')
                                        cur.execute('''INSERT INTO {} VALUES ({}, {}, {}, {})'''.format(MYSQL_TABLE,
                                                                                                        message[
                                                                                                            'sender'][
                                                                                                            'id'], time,
                                                                                                        message[
                                                                                                            'message'].get(
                                                                                                            'text'),
                                                                                                        response))
                                        continue
                                    elif message['message']['nlp']['entities'].get('thanks') and \
                                            message['message']['nlp']['entities']['thanks'][0]['confidence'] >= 0.6:
                                        response = "¡De nada!"
                                        bot.send_text_message(recipient_id, response)
                                        time = datetime.fromtimestamp(int(str(message['timestamp'])[:-3])).strftime(
                                            '%Y-%m-%d %H:%M:%S')
                                        cur.execute('''INSERT INTO {} VALUES ({}, {}, {}, {})'''.format(MYSQL_TABLE,
                                                                                                        message[
                                                                                                            'sender'][
                                                                                                            'id'], time,
                                                                                                        message[
                                                                                                            'message'].get(
                                                                                                            'text'),
                                                                                                        response))
                                        continue
                            except KeyError:
                                print('NLP is not deployed.')

                        response, similarity = transformer.match_query(message['message'].get('text'))

                        # no acceptable answers found in the pool
                        if similarity < 0.5:
                            response = "Please wait! Our representative is on the way to help you!"
                            bot.send_text_message(recipient_id, response)
                        else:
                            responses = response.split('|')
                            for r in responses:
                                if r != '':
                                    bot.send_text_message(recipient_id, r.strip())

                        time = datetime.fromtimestamp(int(str(message['timestamp'])[:-3])).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        cur.execute('''INSERT INTO {} VALUES ({}, {}, {}, {})'''.format(MYSQL_TABLE,
                                                                                        message[
                                                                                            'sender'][
                                                                                            'id'], time,
                                                                                        message[
                                                                                            'message'].get(
                                                                                            'text'),
                                                                                        response))
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


def hasDatabase(cursor):
    try:
        cursor.execute("""
            SELECT SCHEMA_NAME
            FROM INFORMATION_SCHEMA.SCHEMATA
            WHERE SCHEMA_NAME = {}
            """.format(app.config['MYSQL_DB']))
        results = cursor.fetchall()
        if results is not None:
            return True
        else:
            return False
    except Exception as err:
        print("Something went wrong: {}".format(err))


def createDatabase(cursor):
    try:
        cursor.execute("""CREATE SCHEMA {}""".format(app.config['MYSQL_DB']))
    except Exception as err:
        print("Something went wrong: {}".format(err))


def hasTable(cursor):
    try:
        cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{}'
        """.format(MYSQL_TABLE))
        results = cursor.fetchall()
        if results is not None:
            return True
        else:
            return False
    except Exception as err:
        print("Something went wrong: {}".format(err))


def createTable(cursor):
    cursor.execute(
        '''CREATE TABLE {} (senderID VARCHAR(20), sent_time TIME, question VARCHAR(100), answer VARCHAR(100))'''.
            format(MYSQL_TABLE))


if __name__ == "__main__":
    app.run()

{'object': 'page',
 'entry': [
     {
         'id': '100614728239050',
         'time': 1594086355849,
         'messaging': [
             {
                 'sender':
                     {
                         'id': '3690323734327683'
                     },
                 'recipient':
                     {
                         'id': '100614728239050'
                     },
                 'timestamp': 1594086355608,
                 'message':
                     {
                         'mid': 'm_S0zcdsrv9gu8V0iKFaS1lULF2Q0d7p7VaJDAVF6mDIX0wVa9CGZWkWQ8ArmKki7qt0A0yvSVoos0ZnT5KtKTZw',
                         'text': '歇息',
                         'nlp':
                             {
                                 'entities':
                                     {
                                         'greetings': [
                                             {
                                                 'confidence': 0.73418509960175,
                                                 'value': 'true'
                                             }
                                         ],
                                         'location': [
                                             {
                                                 'suggested': True,
                                                 'confidence': 0.34195482888008,
                                                 'value': '歇息',
                                                 'type': 'value'
                                             }
                                         ]
                                     },
                                 'detected_locales': [
                                     {
                                         'locale': 'en_XX',
                                         'confidence': 0.4905
                                     }
                                 ]
                             }
                     }
             }
         ]
     }
 ]
 }
