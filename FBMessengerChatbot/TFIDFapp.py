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
app.config['MYSQL_DATABASE_CHARSET'] = 'utf-16'
MYSQL_TABLE = 'QnA'

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
                                        insertTable(response, message, cur)
                                        continue
                                    # bye detected
                                    elif message['message']['nlp']['entities'].get('bye') and \
                                            message['message']['nlp']['entities']['bye'][0]['confidence'] >= 0.9:
                                        response = "See you next time!"
                                        bot.send_text_message(recipient_id, response)
                                        insertTable(response, message, cur)
                                        continue
                                    # thank detected
                                    elif message['message']['nlp']['entities'].get('thanks') and \
                                            message['message']['nlp']['entities']['thanks'][0]['confidence'] >= 0.9:
                                        response = "You are welcome!"
                                        bot.send_text_message(recipient_id, response)
                                        insertTable(response, message, cur)
                                        continue
                                # detected Spanish
                                elif 'es' in message['message']['nlp']['detected_locales'][0]['locale']:
                                    # greeting detected
                                    if message['message']['nlp']['entities'].get('greetings') and \
                                            message['message']['nlp']['entities']['greetings'][0]['confidence'] >= 0.6:
                                        response = "¡Mucho gusto! ¿Cómo estás?"
                                        bot.send_text_message(recipient_id, response)
                                        insertTable(response, message, cur)
                                        continue
                                    elif message['message']['nlp']['entities'].get('bye') and \
                                            message['message']['nlp']['entities']['bye'][0]['confidence'] >= 0.6:
                                        response = "¡adíos!"
                                        bot.send_text_message(recipient_id, response)
                                        insertTable(response, message, cur)
                                        continue
                                    elif message['message']['nlp']['entities'].get('thanks') and \
                                            message['message']['nlp']['entities']['thanks'][0]['confidence'] >= 0.6:
                                        response = "¡De nada!"
                                        bot.send_text_message(recipient_id, response)
                                        insertTable(response, message, cur)
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

                        insertTable(response, message, cur)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    elif message['message'].get('attachments'):
                        i = 0
                        while i < 1:
                            response = "Interesting! Anything else I could help?"
                            bot.send_text_message(recipient_id, response)
                            i += 1

                        insertTable("\'Interesting! Anything else I could help?\'", message, cur)
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
        """.format(MYSQL_TABLE.replace('\'', '\'\'')))
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


def insertTable(response, message, cursor):
    time = datetime.fromtimestamp(int(str(message['timestamp'])[:-3])).strftime('%Y-%m-%d %H:%M:%S')
    if message['message'].get('attachments') is False:
        cursor.execute('''INSERT INTO {} VALUES ({}, {}, {}, {})'''.format(MYSQL_TABLE, "'" + message['sender']['id'] + "'",
                                                                           time, "'" + message['message'].get('text') + "'",
                                                                           response))
    else:
        cursor.execute(
            '''INSERT INTO {} VALUES ({}, {}, {}, {})'''.format(MYSQL_TABLE, "'" + message['sender']['id'] + "'",
                                                                time, "\'A non-text item sent\'", response))


if __name__ == "__main__":
    app.run()