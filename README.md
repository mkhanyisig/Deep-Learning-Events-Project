# Deep-Learning Cultural Events Recognition Project

## World Event Recognition using Deep Convolutional Neural Network Architectures

<img src="[https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.researchgate.net%2Ffigure%2FExamples-of-event-images-from-the-ChaLearn-Cultural-Event-Recognition-dataset-top-row_fig1_319695330&psig=AOvVaw3fzOir7cSemTLhNhhfqyYi&ust=1673087226098000&source=images&cd=vfe&ved=0CA8QjRxqFwoTCIDZh-DdsvwCFQAAAAAdAAAAABAS](https://www.researchgate.net/publication/319695330/figure/fig1/AS:962204711002115@1606418888444/Examples-of-event-images-from-the-ChaLearn-Cultural-Event-Recognition-dataset-top-row.gif)" >

Mkhanyisi Gamedze
COSI 165B Deep Learning
Final Report

## Abstract

Human scene context analysis and classification into event categories is a very challenging problem within Computer Vision. The ChaLearn challenge in 2015 curated a world cultural event dataset consisting of 99 famous world cultural events and a 1 none class, for the ChaLearn Looking at People challenge. Most of the top performing submissions on this challenge utilized deep convolutional neural network architectures. This paper presents an exploration of deep learning models applied to this recognition task and tries to reimplement some of the results from the winning submissions and publication models from the competition. The dataset is trimmed down to only 11 event categories from the challenge, including the none-class as images as well. Pretraining models on the famous deep models ImageNet dataset improved the object recognition accuracy of the models explored. The 8-layer pre-trained AlexNet had the best performance with 61% test accuracy, compared to the other deeper models, as the ResNet34 was the second closes. Perhaps the deeper model did not perform as well in this task given the relatively small data size more fine-tuning could help improve accuracy.

[Data downlaod link](https://drive.google.com/drive/folders/1VdGjJeYA7JibE1tDaaECP19WJqRh04Gd?usp=share_link)


1. Final Report - Mkhanyisi Gemdze COSI 165B Final Report.pdf
2. Load build report dataset from ChaLearn - Term project analysis I - Loading and exploration of ChaLearn dataset.ipynb
3. Resizing dataset - Resize to smaller dataset Notebook .ipynb
4. Numpy images dataset - smallerdataX.npy
5. Numpy image labels encoded - reencoded_smallerdataY.npy
6. Experiment results models and outputs - Term project analysis II   -  GCP GPU runs Final.ipynb
