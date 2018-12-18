'''
This is the ChatBot for image classification, via asynchronous connection

This Skript is multithreated: 
one threat receives the messages and puts them in the download redis message queue
The second threat listens to responses from the predictions redis message queue

Author: fanconic
'''

import time, json
import telepot
from telepot.loop import MessageLoop
from threading import Thread
from redis import StrictRedis

PORT = 6379
HOST = 'localhost'
TOKEN = #Insert Token here

# Defining Redis Message Queue
r = StrictRedis(host= HOST, port= PORT)

# Process Message from user
def thread1(msg):
        content_type, _, chat_id = telepot.glance(msg)
        if (content_type == 'text' or content_type == 'photo'):

                # message is URL
                if content_type == 'text':
                        data = {
                                'chat_id': chat_id,
                                'url': msg['text']
                        }

                # Message is Picture
                if content_type == 'photo':
                        data = {
                                'chat_id': chat_id,
                                'file_id': msg['photo'][-1]['file_id']
                        }

                # Compress to JSON
                data = json.dumps(data)
                r.rpush('download', data.encode('utf-8'))

# send response to user
def thread2():
        while True:
                data = r.blpop('prediction')[1].decode('utf-8')
                data = json.loads(data)
                chat_id = data['chat_id']
                predictions = data['predictions']

                # Transfrom dict to reply
                reply = ''
                for i in range(5):
                        reply += (str(i+1) + '. ' + predictions[i]['label'] + ' (' + predictions[i]['score'] + ')\n')
                bot.sendMessage(chat_id, reply)

# Main function
if __name__ == "__main__":
        # Start threads
        Thread(target= thread2).start()
        
        # Provide your bot's token
        bot = telepot.Bot(TOKEN)
        MessageLoop(bot, thread1).run_as_thread()
    

        while True:
                time.sleep(10)
