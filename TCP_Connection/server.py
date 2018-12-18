'''
Assignment 2
Server for image classification

Author: fanconic
'''
import base64
from threading import Thread
from queue import Queue
from PIL import Image
import socket, json
from keras.preprocessing import image
from keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
from io import BytesIO
import numpy as np
import time


queue = Queue()

PORT = 50002
ADDRESS = 'localhost'

# Listen for incoming connections
def main_thread():
    # Busy Waiting
    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind socket to localhost
    server_socket.bind((ADDRESS, PORT))

    # Listen for incoming connections from clients
    server_socket.listen(10)
    
    while True:

        # Receive data from client
        (client_socket, address) = server_socket.accept()

        queue.put(client_socket)


# Receive data from clients, decode, and feed into neural network
def second_thread():
    # ResNet50 Model adn Predicitons
    model = ResNet50(weights='imagenet')

    while True:
        client_socket = queue.get()

        # Receive TCP and check with end string, if everything has arrived
        data = ''
        while True:
            part = client_socket.recv(1024)
            data += part.decode('utf-8')
            if '##END##' in data:
                break

        # laod from JSON file and replace the end string
        data = data.replace('##END##', '')
        data = json.loads(data)
        
        # Get variables from dict
        chat_id = data['chat_id']
        encoded_image = data['encoded_image']
        img = base64.b64decode(encoded_image)

        # Convert picture from bytes to image
        # https://www.programcreek.com/python/example/89218/keras.preprocessing.image.img_to_array
        img = Image.open(BytesIO(img))

        # Keras ResNet50 uses 224 X 224 images
        img = img.resize((224,224))
        # Write the picture to an array
        X = image.img_to_array(img)

        # Adding additional axis
        X = np.expand_dims(X, axis=0)

        # Preprocess the input
        X = preprocess_input(X)

        pred = model.predict(X)
        pred = decode_predictions(pred)

        # Process Predictions
        predictions = [] 
        for i in range (5):
            predictions.append({'Label': pred[0][i][1], 'Probability': str(pred[0][i][2])})

        # prepare data to be sent back
        data = {
            'chat_id': chat_id,
            'predictions': predictions
        }
        data = json.dumps(data) + '##END##'
        
        try:
            # Send back data
            client_socket.sendall(data.encode('utf-8'))
        
        finally:
            # Close socket
            client_socket.close()

if __name__ == "__main__":
    Thread(target= main_thread).start()
    Thread(target= second_thread).start()

    while True:
        time.sleep(10)


