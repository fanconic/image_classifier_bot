'''
Assignment
This is the ChatBot for image classification, via asynchronous connection

This script predicts an image based on the pretrained inception v3 model and passess it on to the predictions redis message queue.

Author: fanconic
'''
from redis import StrictRedis
import torchvision.models as models
import json, base64, requests
from torch.autograd import Variable
import torchvision.transforms as transforms
from io import BytesIO
from PIL import Image


# Constant Variables
PORT = 6379
HOST = 'localhost'

# Start Model
model = models.inception_v3(pretrained=True)
model.transform_input = True

# Download the dictionary of labels
content = requests.get("https://s3.amazonaws.com/deep-learning-models/image-models/imagenet_class_index.json").text
labels = json.loads(content)

# Defining Redis Message Queue
r = StrictRedis(host= HOST, port= PORT)

# Listening to incoming messages
while True:
        data = r.blpop('image')[1].decode('utf-8')
        data = json.loads(data)
       
        chat_id = data['chat_id']
        encoded_image = data['encoded_image']
        img = base64.b64decode(encoded_image)
        img = Image.open(BytesIO(img))

        # Normalize
        normalize = transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
                )

        # Preprocess
        preprocess = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(299),
                transforms.ToTensor(),
                normalize
                ])

        # Convert to tensors
        img_tensor = preprocess(img)
        img_tensor.unsqueeze_(0)
        img_variable = Variable(img_tensor)

        # Make prediction
        model.eval()
        preds = model(img_variable)

        # Convert the prediction into text labels
        predictions = []
        for i, score in enumerate(preds[0].data.numpy()):
                predictions.append((score, labels[str(i)][1]))
        
        # Get the top five predicitions and their score
        predictions.sort(reverse=True)
        temp = []
        for score, label in predictions[:5]:
            temp.append({'label': label, 'score': str(score)})
        predictions = temp
        
        # prepare data to be sent back
        data = {
            'chat_id': chat_id,
            'predictions': predictions
        }

        data = json.dumps(data)
        r.rpush('prediction', data.encode('utf-8'))
