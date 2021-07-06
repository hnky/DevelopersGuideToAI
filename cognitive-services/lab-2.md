---
description: Create a custom vision model using the Microsoft Custom Vision service.
---

# Lab 2 - Custom Vision

Using Microsoft Azure Custom Vision service you can start to build your own personalized image classification and object detection algorithms with very little code. In this exercise we will create a Lego Simpsons classification model.

#### Lab requirements

* Azure CLI
* Python 3.6+ environment

## 1. Setup the Azure Resources

### Create a resource group

The Custom Vision Endpoint must be created inside a resource group. You can use an existing resource group or create a new one. 

To create a new resource group, use the following command. Replace  &lt;&lt;resource-group-name&gt;&gt; with your name to use for this resource group. Replace &lt;&lt;location&gt;&gt;  with the Azure region to use for this resource group.

```text
az group create --name <resource-group-name> --location <location>
```

### Create the Cognitive Service Account

Run the command below to create a free Custom Vision Training Endpoint. Replace &lt;&lt;resource-group-name&gt;&gt; with the name you used above and use the same location. Replace &lt;&lt;name&gt;&gt; with a name for your resource like: my-custom-vision-training.

```text
az cognitiveservices account create --name <name> --kind CustomVision.Training --sku F0 --resource-group <resource-group-name> --location <location> --yes
```

### Get the endpoint details from the Cognitive Service Account

To get the endpoint from the Cognitive service account run the CLI command below. Replace &lt;&lt;name&gt;&gt; and &lt;&lt;resource-group-name&gt;&gt; with the names used above. 

**Get the API keys**

```text
az cognitiveservices account keys list --name <name> --resource-group <resource-group-name> 
```

**Get the endpoint URL**

```text
az cognitiveservices account show --name <name> --resource-group <resource-group-name> -o json --query properties.endpoint
```

#### At this point you should have:

- An endpoint URL looking like this: https://&lt;region&gt;.api.cognitive.microsoft.com/   
- 2 keys looking like this: 06a611d19f4f4a88a03f3b552a5d2379

## 2. Create a Custom Vision Model

Every Machine Learning journey starts with a question you want to have answered. For this example, you are going to answer the question: Is it a Homer or a Marge Lego figure.

### Download the dataset

Now that we know what to ask the model, we can go on to the next requirement; that is data. Our model is going to be a classification model, meaning the model will look at the picture and scores the pictures against the different classes. So, the output will be I’m 70% confident this is Homer and 1% confident that this is Marge. By taking the class with the highest score and setting a minimum threshold for the confidence score we know what is on the picture.

I have created a dataset for you with 50 pictures of a Homer Simpson Lego figure and 50 pictures of a Marge Simpsons Lego figure. I have taken the photos with a few things in mind, used a lot of different backgrounds and took the photos from different angles. I made sure the only object in the photo was Homer or Marge and the quality of the photos was somehow the consistent.

Use the Python code below to download and extract the dataset to the folder "LegoSimpsons" or [download the dataset](https://github.com/hnky/dataset-lego-figures/raw/master/_download/simpsons-lego-dataset.zip) and extract it manually in the folder "LegoSimpsons".

```text
import os
import urllib.request
import zipfile

# Download the dataset from Github
data_url = "https://github.com/hnky/dataset-lego-figures/raw/master/_download/simpsons-lego-dataset.zip"
data_path = "./LegoSimpsons"
download_path = os.path.join(data_path,"simpsons-lego-dataset.zip")
if not os.path.exists(data_path):
    os.mkdir(data_path);
urllib.request.urlretrieve(data_url, filename=download_path)

# Unzip the dataset
zip_ref = zipfile.ZipFile(download_path, 'r')
zip_ref.extractall(data_path)
zip_ref.close()
print("Data extracted in: {}".format(data_path))

os.remove(download_path)
print("Downloaded file removed: {}".format(download_path))
```

### Create a Custom Vision Project

For the training we are going the use the [Custom Vision Service Python SDK](https://docs.microsoft.com/python/api/overview/azure/cognitiveservices/customvision?view=azure-python&WT.mc_id=aiml-0000-heboelma), you can install this package using pip.

```text
pip install azure-cognitiveservices-vision-customvision
```

Create a new Python file called 'train.py' in Visual Studio code or your favorite editor and start adding code or use a Jupyter Notebook.

Start with importing the packages needed.

```text
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry
```

Next, create variables for the Custom Vision endpoint, Custom Vision training key and the location where the training images are stored.

```text
cv_endpoint = "https://westeurope.api.cognitive.microsoft.com"
training_key = "<INSERT TRAINING KEY>"
training_images = "LegoSimpsons/TrainingImages"
```

To start with the training, we need to create a Training Client. This method takes as input the endpoint and the training key.

```text
trainer = CustomVisionTrainingClient(training_key, endpoint= cv_endpoint)
```

Now you are ready to create your first project. The project takes a name and domain as input, the name can be anything. The domain is a different story. You can ask for a list of all possible domains and choose the one closest to what you are trying to accomplish. For instance if you are trying to classify food you pick the domain “Food” or “Landmarks” for landmarks. Use the code below to show all domains.

```text
for domain in trainer.get_domains():
  print(domain.id, "\t", domain.name) 
```

You might notice that some domains have the word “Compact” behind them. If this is the case it means the Azure Custom Vision Service will create a smaller model, which you will be able to export and run locally on your mobile phone or desktop.

Let’s create a new project with the domain set to “General Compact”.

```text
project = trainer.create_project("Lego - Simpsons - v1","0732100f-1a38-4e49-a514-c9b44c697ab5")
```

### Upload and tag the images

Next you need to create tags, these tags are the same as classes mentioned above. When you have created a few tags we can tag images with them and upload the images to the Azure Custom Vision Service.

Our images are sorted per tag/class in a folder. All the photos of Marge are in the folder named 'Marge' and all the images of Homer are in the folder named 'Homer'.

In the code below we do the following steps:

* We open the directory containing the folders with training images.
* Loop through all the directories found in this folder
* Create a new tag with the folder name
* Open the folder containing the images
* Create, for every image in that folder, an ImageFileEntry that contains the filename, file content and the tag.
* Add this ImageFileEntry to a list.

```text
image_list = []
directories = os.listdir(training_images)

for tagName in directories:
 	tag = trainer.create_tag(project.id, tagName)
 	images = os.listdir(os.path.join(training_images,tagName))
 	for img in images:
 		with open(os.path.join(training_images,tagName,img), "rb") as image_contents:
 			image_list.append(ImageFileCreateEntry(name=img, contents=image_contents.read(), tag_ids=[tag.id]))  
```

Now you have a list that contains all tagged images. So far no images have been added to the Azure Custom Vision service, only the tags have been created.

Uploading images goes in batches with a max size of 64 images per batch. Our dataset is 300+ images big, so first we need to split the list into chunks of 64 images.

```text
def chunks(l, n):
 	for i in range(0, len(l), n):
 		yield l[i:i + n]
batchedImages = chunks(image_list, 64)
```

Now we have our images split in batches of 64, we can upload them batch by batch to the Azure Custom Vision Service. _Note: This can take a while!_

```text
for batchOfImages in batchedImages:
    upload_result = trainer.create_images_from_files(project.id, ImageFileCreateBatch(images=batchOfImages))
    if not upload_result.is_batch_successful:
        print("Image batch upload failed.")
        for image in upload_result.images:
            print("Image status: ", image.status)
    else:
        print("Batch uploaded successfully")
```

### Train the classification model

From this point, there are only two steps remaining before you can access the model through an API endpoint. First you need to train the model and finally you must publish the model, so it is accessible through a prediction API. The training can take a while, so you can create a while loop after the train request that checks the status of the model training every second.

```text
print ("Training...")
iteration = trainer.train_project(project.id)
while (iteration.status != "Completed"):
    iteration = trainer.get_iteration(project.id, iteration.id)
    print ("Training status: " + iteration.status)
    print ("Waiting 10 seconds...")
    time.sleep(10)
```

Now you have successfully trained your model!

A small recap of what have we done:

* You created an Azure Resource group containing an Azure Custom Vision service training and prediction endpoint
* You have created a new Project
* In that project you have created tags
* You have uploaded images in batches of 64 and tagged them
* You have trained an iteration of your model
* You have published the iteration to a prediction endpoint

## 3. Test your model

To test our model we are going to export our model in the ONNX format, download the model and run it locally.

### Export the iteration to an ONNX model

```text
platform = "ONNX"
flavor = "ONNX12"
iteration_id = iteration.id 
project_id = project.id
export = trainer.export_iteration(project_id, iteration_id , platform, flavor, raw=False)
```

```text
while (export.status == "Exporting"):
    print ("Waiting 10 seconds...")
    time.sleep(10)
    exports = trainer.get_exports(project.id, iteration_id)
    # Locate the export for this iteration and check its status  
    for e in exports:
        if e.platform == export.platform and e.flavor == export.flavor:
            export = e
            break
    print("Export status is: ", export.status)
```

### Download and unzip the export

```text
import os
import requests
import zipfile

if export.status == "Done":
    # Success, now we can download it
    export_file = requests.get(export.download_uri)
    with open("export.zip", "wb") as file:
        file.write(export_file.content)
        
# Unzip the downloaded export
if not os.path.exists("./model"):
    os.mkdir("./model");
zip_ref = zipfile.ZipFile("export.zip", 'r')
zip_ref.extractall("./model")
zip_ref.close()
print("Data extracted in: ./model")
```

### Predict an image

```text
pip install onnxruntime
pip install "pillow!=8.3.0" #pillow 8.3.0 and numpy don't work together
```

```text
import onnxruntime as nxrun
import numpy as np
import PIL

image_filepath = "./Bart.jpg"
model_path = "./model/model.onnx"

sess = nxrun.InferenceSession(model_path)
image = PIL.Image.open(image_filepath).resize([224,224])
input_array = np.array(image, dtype=np.float32)[np.newaxis, :, :, :]
input_array = input_array.transpose((0, 3, 1, 2))[:, (2, 1, 0), :, :]

input_name = sess.get_inputs()[0].name
outputs = sess.run(None, {input_name: input_array.astype(np.float32)})

print("Label: " + outputs[0][0][0])
print("Score: " + str(outputs[1][0][outputs[0][0][0]]))
```

**Great work!**   
You have created your specialized Simpsons classification model using the Azure Custom Vision Service.

## Resources

* [https://github.com/Azure-Samples/cognitive-services-onnx-customvision-sample](https://github.com/Azure-Samples/cognitive-services-onnx-customvision-sample)
* [https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/quickstarts/image-classification](https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/quickstarts/image-classification?tabs=visual-studio&pivots=programming-language-python)
* [https://github.com/Azure-Samples/customvision-export-samples](https://github.com/Azure-Samples/customvision-export-samples)
* [https://docs.microsoft.com/python/api/overview/azure/cognitiveservices/customvision?view=azure-python](https://docs.microsoft.com/en-us/python/api/overview/azure/cognitiveservices/customvision?view=azure-python)

[**Continue with lab 3 &gt;**](lab-3.md)

