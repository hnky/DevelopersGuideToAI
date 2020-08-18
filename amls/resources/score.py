import os
import torch
import torch.nn as nn
import torchvision
from torchvision import transforms
import json
import urllib
from PIL import Image

from azureml.core.model import Model

def init():
    global model
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'outputs','model.pth')
    labels_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'outputs','labels.txt')
    
    print('Loading model...', end='')
    model = torch.load(model_path, map_location=lambda storage, loc: storage)
    model.eval()
    
    print('Loading labels...', end='')
    with open(labels_path, 'rt') as lf:
        global labels
        labels = [l.strip() for l in lf.readlines()]
    print(len(labels), 'found. Success!')

    
def run(input_data):
    url = json.loads(input_data)['url']
    urllib.request.urlretrieve(url, filename="tmp.jpg")
    
    input_image = Image.open("tmp.jpg")

    preprocess = transforms.Compose([
        transforms.Resize(225),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model

    # move the input and model to GPU for speed if available
    if torch.cuda.is_available():
        input_batch = input_batch.to('cuda')
        model.to('cuda')

    with torch.no_grad():
        output = model(input_batch)

    index = output.data.cpu().numpy().argmax()
    probability = torch.nn.functional.softmax(output[0], dim=0).data.cpu().numpy().max()

    result = {"label": labels[index], "probability": round(probability*100,2)}
    os.remove("tmp.jpg")
    return result