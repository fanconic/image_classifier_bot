'''
Assignment 2
This is the ChatBot for image classification

Author: fanconic
'''
import time
import telepot
from telepot.loop import MessageLoop
from threading import Thread
from queue import Queue
from PIL import Image
import socket, base64, json, requests
from io import BytesIO

queue1 = Queue()
queue2 = Queue()

PORT = 50002
ADDRESS = 'localhost'
TOKEN = '### insert your telegram token here ###'

# Process Message from user
def receive_thread(msg):
    content_type, _, chat_id = telepot.glance(msg)

    if (content_type == 'text' or content_type == 'photo'):

        if content_type == 'text':
            # Download file from URL
            img_data = requests.get(msg['text']).content
            with open('photo.png', 'wb') as handler:
                handler.write(img_data)

        if content_type == 'photo':
            # Download Photo
            bot.download_file(msg['photo'][-1]['file_id'], 'photo.png')

        # load image
        image = Image.open('photo.png')

        data = {
            'chat_id': chat_id,
            'image': image
        }
        queue1.put(data)

# Communicate with server
def client_thread():
    while True:
        # Create Socket
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        data = queue1.get()
        chat_id = data['chat_id']
        image = data['image']

        # Encode picture to binary data
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        encoded_image = base64.b64encode(buffered.getvalue())

        data = {
            'chat_id': chat_id, #chat_id received by telegram
            'encoded_image': encoded_image.decode('utf-8') # base64-encoded string of the image object
        }

        # Converting to a JSON Package
        data = json.dumps(data) + '##END##'

        try:
            # connect to the server
            soc.connect((ADDRESS, PORT))

            # Send a message to the server
            soc.sendall(data.encode('utf-8'))

            # Receive data from the server
            # Receive TCP and check with end string, if everything has arrived
            data = ''
            while True:
                part = soc.recv(1024)
                data += part.decode('utf-8')
                if '##END##' in data:
                    break

            # laod from JSON file and replace the end string
            data = data.replace('##END##', '')
            data = json.loads(data)
            queue2.put(data)

        finally: 
            # Close socket
            soc.close()


# send response to user
def response_thread():
    while True:
        data = queue2.get()
        chat_id = data['chat_id']
        predictions = data['predictions']

        # Transfrom dict to reply
        reply = ''
        for i in range(5):
            reply += (str(i+1) + '. ' + predictions[i]['Label'] + ' (' + predictions[i]['Probability'] + ')\n')
        bot.sendMessage(chat_id, reply)

if __name__ == "__main__":
    # Start threads
    Thread(target= client_thread).start()
    Thread(target= response_thread).start()

    # Provide your bot's token
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, receive_thread).run_as_thread()

    while True:
        time.sleep(10)
