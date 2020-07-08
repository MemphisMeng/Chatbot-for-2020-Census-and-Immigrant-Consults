from datetime import datetime

MYSQL_TABLE = 'QnA'
MYSQL_DB = 'sql9353097'


def hasDatabase(cursor, database):
    try:
        cursor.execute("""
            SELECT SCHEMA_NAME
            FROM INFORMATION_SCHEMA.SCHEMATA
            WHERE SCHEMA_NAME = '{}'
            """.format(database))
        results = cursor.fetchall()
        if results[0]['SCHEMA_NAME']:
            return True
        else:
            return False
    except Exception as err:
        print("Something went wrong: {}".format(err))


def createDatabase(cursor, database):
    try:
        cursor.execute("""CREATE SCHEMA {}""".format(database))
        print("Database created successfully!")
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
        if results[0]['COUNT(*)'] == 1:
            return True
        else:
            return False
    except Exception as err:
        print("Something went wrong: {}".format(err))


def createTable(cursor):
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS {}(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, senderID VARCHAR(20), 
        sent_time DATETIME, question VARCHAR(100), answer VARCHAR(100))'''.
            format(MYSQL_TABLE))
    print('Data table created successfully!')


def insertTable(response, message, cursor):
    time = datetime.fromtimestamp(int(str(message['timestamp'])[:-3])).strftime('%Y-%m-%d %H:%M:%S')
    print("time: ", time)
    if message['message'].get('text'):
        cursor.execute(
            '''INSERT INTO {}(senderID, sent_time, question, answer) VALUES({}, {}, {}, {})'''
                .format(MYSQL_TABLE, "'" + message['sender']['id'] + "'",
                        time, "'" + message['message'].get('text') + "'",
                        "'" + response + "'"))
    elif message['message'].get('assignments'):
        cursor.execute(
            '''INSERT INTO {}(senderID, sent_time, question, answer) VALUES({}, {}, {}, {})'''
                .format(MYSQL_TABLE, "'" + message['sender']['id'] + "'",
                        time, "\"A non-text item sent\"",
                        "\"" + response + "\""))
