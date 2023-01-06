# -*- coding: utf-8 -*-
"""Term project analysis GCP GPU .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1U1zx2hckK5QVK25qHWODBuTEKJlIwJbG

### Mkhanyisi Gamedze
#### COSI 165B Deep Learning
#### Term Project Analysis - Google Cloud
#### 10 May 2022



DataSet link: https://competitions.codalab.org/competitions/4081#participate-get-data or https://chalearnlap.cvc.uab.cat/dataset/17/description/
"""

import os
import pandas as pd
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
from scipy import ndimage, misc
import imageio
import cv2

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import torchvision.models as models

from tqdm import tqdm



"""### Load Data

Build labels Dataframe

<b>Train Labels</b>
"""

from google.colab import drive
drive.mount('/content/drive')

r="/content/drive/MyDrive/COSI 165B data"
os.chdir(r)
print(os.getcwd())

"""### Load saved data"""

os.chdir(r)
print(os.getcwd())
os.listdir()

#os.chdir('./Numpy Clean Dataset')

fulldataX=np.load('smallerdataX.npy')

fulldataX.shape

fulldataY=np.load('reencoded_smallerdataY.npy')
fulldataY.shape

"""<b>Test Transform</b>"""

plt.imshow(fulldataX[1])
plt.show()

fulldataY[1]



"""#### To Tensor"""

tensordataX = torch.FloatTensor(fulldataX)

tensordataY = torch.FloatTensor(fulldataY.astype(int))


tensordataX.shape, tensordataY.shape

"""<b>Permute Images so input channel is color for convolution</b>"""

tensordataX=tensordataX.permute(0,3,1,2)
tensordataX.shape

"""### Train-Test split (80 : 20)"""

p=int(0.8*(tensordataX.shape[0]))

trainX=tensordataX[:p]
testX=tensordataX[p:]
trainY=tensordataY[:p]
testY=tensordataY[p:]

trainX.shape, trainY.shape, testX.shape, testY.shape

"""### Visualize Categories"""

labels = ['Ballon Fiesta', 'Diwali Festival of Lights', 'Holi Festival', 'Frozen Dead guys', 'Buffalo Roundup','Battle of Oranges', 'Oktoberfest', 'Eid Al Adha', 'Chinese New Year', 'Boston Marathon', "Non Class"]


# Let's view more images in a grid format
# Define the dimensions of the plot grid 
W_grid = 5
L_grid = 5

fig, axes = plt.subplots(L_grid, W_grid, figsize = (20,20))

axes = axes.ravel() # flaten the 15 x 15 matrix into 225 array

n_train = len(trainX) # get the length of the train dataset

# Select a random number from 0 to n_train
for i in np.arange(0, W_grid * L_grid): # create evenly spaces variables 

    # Select a random number
    index = np.random.randint(0, n_train)
    # read and display an image with the selected index    
    axes[i].imshow(fulldataX[index])
    label_index = int(trainY[index])
    axes[i].set_title(labels[label_index], fontsize = 8)
    axes[i].axis('off')

plt.subplots_adjust(hspace=0.4)





"""### Vanilla CNN model"""

# CNN model
class Net(nn.Module):

    def __init__(self):
        super().__init__()
        
        # define convolution layers
        """
        self.conv1 = nn.Conv2d(3, 96, kernel_size=(7,7), stride=2)
        self.conv2 = nn.Conv2d(96, 512, kernel_size=(3,3), stride=1)
        """
        self.conv1 = nn.Conv2d(3, 6, kernel_size=(5,5), stride=1)
        self.conv2 = nn.Conv2d(6, 16, kernel_size=(5,5), stride=1)
        
        
        # figure out output conv flat length
        x = torch.randn(1,3,256,256)
        self._to_linear = None
        self.convs(x)
        
        # fully connected layers
        self.fc1 = nn.Linear(self._to_linear, 500)
        self.fc2 = nn.Linear(500,250)
        self.fc3 = nn.Linear(250, 11)
        self.softmax = nn.Softmax(dim=1)

        
    def convs(self, x):
        # max pooling over 2x2 both Conv layers
        x=self.conv1(x)
        x=F.relu(x)
        x =F.max_pool2d(x, (2, 2))
        
        x = F.max_pool2d(F.relu(self.conv2(x)), (2, 2))
        
        
        #print(x.shape)
        # first pass, figure flat length
        if self._to_linear is None:
            print("x[0] : ",x[0].shape)
            self._to_linear = x[0].shape[0]*x[0].shape[1]*x[0].shape[2]
        return x
    
    def forward(self, x):
        x = self.convs(x) # first two convolutional layers
        x = x.reshape(-1, self._to_linear) # flatten x
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        #x = F.sigmoid(self.fc3(x)) # Sigmoidal activation for output layer since two class problem
        x=F.log_softmax(self.fc3(x), dim=1)
        
        #x=self.softmax(self.fc3(x))
        #print("x:",x.shape)
        #print("x:",x)
        return x

vanillaCNN=Net()

dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('Using device "%s" for training' % dev)

print("Vanilla CNN:\n",vanillaCNN.to(dev))

#transform = torchvision.transforms.ToTensor()
img=trainX[:19].cuda()
print("image shape: ",img.shape)
print("reshaped img: ",img.view(-1,3,256,256).shape)

v=torch.randn(1,3,256,256).cuda()
print("v shape: ",v.shape)
r=vanillaCNN.forward(v)
simg=torch.squeeze(img.view(-1,3,256,256))
print("squezzed img: ",simg.shape)


im= torch.rand(10, 3, 256,256).cuda()
print("rand tensor shape: ",im.shape)
c=vanillaCNN.forward(im)

print("output: ",r)
print("rand img output: ",c.shape)

b=vanillaCNN.forward(img)
print("batch result: ",b.shape)

print("CNN Model:\n",vanillaCNN)

"""#### Train model"""

gc.collect()

EPOCHS = 150
BATCH_SIZE = 50

min_loss = np.Inf #lowest loss will be the loaded model

loss_function = nn.CrossEntropyLoss().to(dev) 

optimizer = optim.Adam(vanillaCNN.parameters(),lr=0.00001)

epoch_num=[]
loss_arr=[]

enum=0
for epoch in range(EPOCHS):
    train_loss = 0
    vanillaCNN.train()
    for i in tqdm(range(0, len(trainX), BATCH_SIZE)): 
        #print(f"{i}:{i+BATCH_SIZE}")
        
        batch_X = trainX[i:i+BATCH_SIZE].to(dev)
        batch_y = trainY[i:i+BATCH_SIZE].to(dev)
        batch_y=batch_y.view(len(batch_y)).type(torch.LongTensor)
        
        vanillaCNN.zero_grad()
        #print("batch shape: ",batch_X.shape)
        batch_X=batch_X.cuda()
        batch_y=batch_y.cuda()

        outputs = vanillaCNN(batch_X)
        outputs.to(dev)
        #print("result shape: ",outputs.shape,batch_y.shape)
        
        #print(outputs.dtype)
        #print(batch_y.dtype)
        #print(outputs.shape," <=> ",batch_y.shape)
        
        loss = loss_function(outputs, batch_y)
        loss.backward()
        optimizer.step()    #update weights
        
        #print(loss.item())
        #print(loss.item()," - ",len(train_x))
        train_loss += loss.item()/len(trainX)
    #print("train loss: ",train_loss)
    if epoch % 5 == 0:
        print('Epoch: {}, Train Loss: {:.4f}, Current Min Loss: {:.4f}\n'.format(   #print training loss at each step
            epoch,
            train_loss,
            min_loss
        )) 
    if train_loss < min_loss:   
        min_loss = train_loss
    print(train_loss)
    epoch_num.append(enum)
    loss_arr.append(train_loss)
    enum+=1

plt.plot(epoch_num, loss_arr)
plt.title('Vannilla CNN - Train Loss vs Epoch number')
plt.xlabel('Epoch number')
plt.ylabel('Train Loss')
plt.show()

"""#### Test"""

#def test(model,test_x,test_y):
def model_test(test_x,test_y, model, epoch_num=EPOCHS):
    model.train(False)
    correct = 0
    total = 0

    #print(test_y)
    with torch.no_grad():
        for i in tqdm(range(len(test_x))):
            real_class = test_y[i].to(dev)
            images=test_x[i].view(-1,3,256,256).to(dev)
            net_out = model(images) # returns a list, 

            predicted_class = torch.argmax(net_out,dim=1)
            #print(net_out," =>",predicted_class," : ",real_class)
            if predicted_class == real_class:
                correct += 1
                #print(net_out," =>",predicted_class," : ",real_class)
            total += 1
    print("Accuracy: ", round((correct/total)*100, 3)," % ")

vanillaCNN.train(False)
correct = 0
total = 0

#print(test_y)

with torch.no_grad():
    for i in tqdm(range(len(testX))):
        real_class = testY[i].to(dev)
        images=testX[i].view(-1,3,256,256).to(dev)
        net_out = vanillaCNN(images) # returns a list, 
        
        predicted_class = torch.argmax(net_out,dim=1)
        #print(net_out," =>",predicted_class," : ",real_class)
        #print(predicted_class.shape," : ",real_class.shape)
        if predicted_class == real_class:
            correct += 1
            #print(net_out," =>",predicted_class," : ",real_class)
        total += 1
print("Initial Model Accuracy: ", round((correct/total)*100, 3)," % ")

"""### Model Train function"""

def model_train(model,trainX,trainY,testX,testY):
    trainX.to(dev)
    testX.to(dev)
    trainY.to(dev)
    testY.to(dev)
    model.to(dev)

    min_loss = np.Inf
    epoch_num=[]
    loss_arr=[]

    enum=0
    for epoch in range(EPOCHS):
        train_loss = 0
        model.train()

        for i in tqdm(range(0, len(trainX), BATCH_SIZE)): 
            #print(f"{i}:{i+BATCH_SIZE}")

            batch_X = trainX[i:i+BATCH_SIZE].to(dev)
            batch_y = trainY[i:i+BATCH_SIZE].to(dev)
            batch_y=batch_y.view(len(batch_y)).type(torch.LongTensor)

            # Clear accumulated gradients from previous iteration
            # before backpropagating. 
            model.zero_grad()
            batch_X=batch_X.cuda()
            batch_y=batch_y.cuda()
            #print(batch_X.shape)
            outputs = model(batch_X)
            outputs.to(dev)

            #print("result shape: ",outputs.shape,batch_y.shape)

            #print(outputs.dtype)
            #print(batch_y.dtype)

            loss = loss_function(outputs, batch_y)
            loss.backward()
            optimizer.step()    #update weights

            #print(loss.item())
            #print(loss.item()," - ",len(train_x))
            train_loss += loss.item()/len(trainX)
        #print("train loss: ",train_loss)
        if epoch % 5 == 0:
            print('Epoch: {}, Train Loss: {:.4f}, Current Min Loss: {:.4f}\n'.format(   #print training loss at each step
                epoch,
                train_loss,
                min_loss
            )) 
            model_test(testX,testY, model, EPOCHS)
        if train_loss < min_loss:   
            min_loss = train_loss
        epoch_num.append(enum)
        loss_arr.append(train_loss)
        enum+=1
    
    model_test(testX,testY, model, EPOCHS)

    return model,epoch_num,loss_arr

EPOCHS = 50
BATCH_SIZE = 100

trained_vanillaCNN, epoch_num,loss_arr = model_train(vanillaCNN, trainX,trainY,testX,testY)

plt.plot(epoch_num, loss_arr)
plt.title('Vannilla CNN - Train Loss vs Epoch number')
plt.xlabel('Epoch number')
plt.ylabel('Train Loss')
plt.show()

"""### ResNet18"""

resNet = models.resnet18(pretrained=True)

num_ftrs = resNet.fc.in_features
print(num_ftrs)

import gc
gc.collect()

resNet.fc = nn.Linear(num_ftrs, 11)
resNet.to(dev)

EPOCHS = 150
BATCH_SIZE = 100

optimizer = optim.Adam(resNet.parameters(),lr=0.00001)
criterion = nn.CrossEntropyLoss().to(dev)

trained_resNet, epoch_num,loss_arr = model_train(resNet, trainX,trainY,testX,testY)

plt.plot(epoch_num, loss_arr)
plt.title('ResNet18 - Train Loss vs Epoch number')
plt.xlabel('Epoch number')
plt.ylabel('Train Loss')
plt.show()

"""### AlexNet"""

class AlexNet(nn.Module):
    def __init__(self, num_classes=11):
        super(AlexNet, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, stride=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(64, 192, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(192, 384, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.Conv2d(384, 256, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
        )
        self.classifier = nn.Sequential(
            nn.Dropout(),
            nn.Linear(256 * 12 * 12, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        #print("conv output shape: ",x.shape)
        x = x.reshape(x.size(0), 256 * 12 * 12)
        x = F.log_softmax(self.classifier(x),dim=1)
        return x

alexNet=AlexNet(11)

alexNet.to(dev)

EPOCHS = 100
BATCH_SIZE = 100

optimizer = optim.Adam(alexNet.parameters(),lr=0.00001)

print(img.shape)
b=alexNet(img)
print("batch result: ",b.shape)
b

trained_alexNet , epoch_num,loss_arr= model_train(alexNet, trainX,trainY,testX,testY)

plt.plot(epoch_num, loss_arr)
plt.title('AlexNet - Train Loss vs Epoch number')
plt.xlabel('Epoch number')
plt.ylabel('Train Loss')
plt.show()

"""### Pretrained on ImageNet AlexNet"""

pretrained_AlexNet = torch.hub.load('pytorch/vision:v0.10.0', 'alexnet', pretrained=True)

#pretrained_AlexNet

num_ftrs = pretrained_AlexNet.classifier[6].in_features
num_ftrs

pretrained_AlexNet.classifier[6]= nn.Linear(num_ftrs, 11)
pretrained_AlexNet

optimizer = optim.Adam(pretrained_AlexNet.parameters(),lr=0.00001)

EPOCHS = 150
BATCH_SIZE = 200

retrained_AlexNet, epoch_num,loss_arr = model_train(pretrained_AlexNet, trainX,trainY,testX,testY)

plt.plot(epoch_num, loss_arr)
plt.title('pretrained(ImageNet) AlexNet - Train Loss vs Epoch number')
plt.xlabel('Epoch number')
plt.ylabel('Train Loss')
plt.show()

"""### VGG16"""

vgg16 = models.vgg16()

vgg16

num_ftrs = vgg16.classifier[0].in_features
num_ftrs

vgg16.classifier=nn.Sequential(nn.Linear(num_ftrs,1000),  nn.ReLU(inplace=True),nn.Dropout(0.5,inplace=True),nn.Linear(1000, out_features=11, bias=True))



vgg16

optimizer = optim.Adam(vgg16.parameters(),lr=0.00001)

EPOCHS = 40
BATCH_SIZE = 2

gc.collect()

#trained_vgg16, epoch_num,loss_arr = model_train(vgg16, trainX,trainY,testX,testY)

"""Tried reducing BATCH_SIZE and I still get this error, so model will be skipped :("""



"""### GoogLeNet"""

googLeNet=torch.hub.load('pytorch/vision:v0.10.0', 'googlenet', pretrained=True)

#googLeNet

num_ftrs = googLeNet.fc.in_features
num_ftrs

googLeNet.fc= nn.Linear(num_ftrs, 11)
#googLeNet

optimizer = optim.Adam(googLeNet.parameters(),lr=0.00001)

BATCH_SIZE = 2
EPOCHS = 140

trained_googLeNet, epoch_num,loss_arr = model_train(googLeNet, trainX,trainY,testX,testY)

model_test(testX,testY, trained_googLeNet, epoch_num=EPOCHS)

plt.plot(epoch_num, loss_arr)
plt.title('googLeNet - Train Loss vs Epoch number')
plt.xlabel('Epoch number')
plt.ylabel('Train Loss')
plt.show()

"""### ResNet34"""

#resNext50 = models.resnext50_32x4d(pretrained=True)
resNet34=models.resnet34(pretrained=True)

resNet34

num_ftrs = resNet34.fc.in_features
num_ftrs

resNet34.fc= nn.Linear(num_ftrs, 11)

optimizer = optim.Adam(resNet34.parameters(),lr=0.00001)

BATCH_SIZE = 100
EPOCHS = 150

trained_resNet34, epoch_num,loss_arr = model_train(resNet34, trainX,trainY,testX,testY)

plt.plot(epoch_num, loss_arr)
plt.title('ResNet34 - Train Loss vs Epoch number')
plt.xlabel('Epoch number')
plt.ylabel('Train Loss')
plt.show()





len(loss_arr)

"""### ResNext 50 32x4d"""

resNext50=models.resnext50_32x4d(pretrained=True)

resNext50

num_ftrs = resNext50.fc.in_features
num_ftrs

resNext50.fc = nn.Linear(num_ftrs, 11)

optimizer = optim.Adam(resNext50.parameters(),lr=0.00001)

BATCH_SIZE = 5
EPOCHS = 100

gc.collect()

trained_resNext50, epoch_num,loss_arr = model_train(resNext50, trainX,trainY,testX,testY)

plt.plot(epoch_num, loss_arr)
plt.title('ResNext50 - Train Loss vs Epoch number')
plt.xlabel('Epoch number')
plt.ylabel('Train Loss')
plt.show()

"""### VGGNet - VGG 11-layer model (configuration “A”) """

vgg11= models.vgg11(pretrained=True)

vgg11

num_ftrs = vgg11.classifier[0].in_features
num_ftrs

vgg11.classifier=nn.Sequential(nn.Linear(num_ftrs,1000),  nn.ReLU(inplace=True),nn.Dropout(0.5,inplace=True),nn.Linear(1000, out_features=11, bias=True))

optimizer = optim.Adam(vgg11.parameters(),lr=0.00001)
loss_function = nn.CrossEntropyLoss().to(dev)

EPOCHS = 50
BATCH_SIZE = 1

trained_vgg11, epoch_num,loss_arr = model_train(vgg11, trainX,trainY,testX,testY)

"""#### Model training could not be completed with resources"""







"""### Resources

- https://competitions.codalab.org/competitions/4081#participate-get-data
- 


- https://blog.keras.io/running-jupyter-notebooks-on-gpu-on-aws-a-starter-guide.html

#####
"""