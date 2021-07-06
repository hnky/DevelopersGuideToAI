---
description: Analyze an image by sending it to the Computer Vision API
---

# Lab 1 - Computer Vision

Microsoft Azure Cognitive Services contain some pre-built models for the most typical tasks, such as object detection in pictures, speech recognition and synthesis, sentiment analysis and so on. Let us test the [**Computer Vision API**](https://azure.microsoft.com/services/cognitive-services/computer-vision/?WT.mc_id=gaic-github-heboelma) service to see if it can recognize some specific objects in one particular problem domain.

Suppose we need to create an application that recognizes Simpson Lego Figures:

We will use the [Simpsons Lego Figure Dataset](https://github.com/hnky/dataset-lego-figures) from Henk Boelman.

Let us start by looking at how pre-trained [Computer Vision cognitive service](https://azure.microsoft.com/services/cognitive-services/computer-vision/?WT.mc_id=gaic-github-heboelma) can see our images:

### 1. Setup the Azure Resources

#### Create a resource group

The Azure Machine Learning workspace must be created inside a resource group. You can use an existing resource group or create a new one. To create a new resource group, use the following command. Replace  &lt;&lt;resource-group-name&gt;&gt; with your name to use for this resource group. Replace &lt;&lt;location&gt;&gt;  with the Azure region to use for this resource group.

```text
az group create --name <resource-group-name> --location <location>
```

#### Create the Cognitive Service Account

Run the command below to create a free Computer Vision Endpoint. Replace &lt;&lt;resource-group-name&gt;&gt; with the name you used above and use the same location. Replace &lt;&lt;name&gt;&gt; with a name for your resource like: my-computervision.

```text
az cognitiveservices account create --name <name> --kind ComputerVision --sku F0 --resource-group <resource-group-name> --location <location> --yes
```

#### Get the endpoint details from the Cognitive Service Account

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

### 2. Test the Computer Vision Endpoint

#### Using the command line

Run the command below to test the endpoint for an image with Bart Simpson on it.

```text
curl -H "Ocp-Apim-Subscription-Key: <<key>>" -H "Content-Type: application/json" "<<endpoint-url>>/vision/v3.2/analyze?visualFeatures=Description" -d "{\"url\":\"https://raw.githubusercontent.com/hnky/dataset-lego-figures/master/_test/Bart.jpg\"}"
```

The response should look like:  
`{  
"description":{   
    "tags":[ "text", "indoor", "toy" ],   
"captions":[ {   
    "text": "a hand holding a toy",   
    "confidence":0.4660031199455261   
}]}}`

#### Using a web interface

Navigate to: [https://cgntv-cv.azurewebsites.net/](https://cgntv-cv.azurewebsites.net/)  
Enter the endpoint URL, the API key, a link to an image and click 'analyze image'. This website shows all the information that comes back from the Computer Vision API.

> **Tip: Try it with your own images!**

### 3. Conclusion

In this lab you have created a Computer Vision Endpoint in Azure and send images to the endpoint using the command line and a through a visual interface.

While some of the objects \(such as Toy\) can be recognized by the pre-trained model, more specialized objects \(like this is Bart Simpson or Marge Simpson\) are not determined correctly.

[**Continue with lab 2 &gt;**](lab-2.md)

