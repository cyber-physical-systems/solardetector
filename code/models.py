# -*- coding: utf-8 -*-
"""models.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dWHugbpikYpXQG6CojhqbbfRpZVmZ-le
"""

import pandas
import pandas as pd
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn import datasets
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import csv
import math
import os

data = pd.read_csv("features_train.csv")
data = data.dropna()
feature_cols = ['size','pole','mean','stddev','b_mean','g_mean','r_mean','b_stddev','g_stddev','r_stddev','square','ratiowh','ratioarea','approxlen','numangle','numangle90','numangle70']
X = data[feature_cols]

scaler = StandardScaler()
# try:
#   X = scaler.fit_transform(X)# Features
# except ValueError:
#     print("ops")


y = data.label # Target variable

# from sklearn.model_selection import train_test_split
# X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.3,random_state=0)

from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier

from sklearn import tree

model = tree.DecisionTreeClassifier()
# instantiate the model (using the default parameters)
# model = RandomForestClassifier(max_depth=2, random_state=0)
X_train = X
y_train = y

# from sklearn.svm import SVC
# svclassifier = SVC(kernel='linear',class_weight='balanced',probability=True)
# model = svclassifier.fit(X_train, y_train)


# fit the model with data
model.fit(X_train, y_train)



datatest = pd.read_csv("features_test.csv")
datatest = datatest.dropna()
feature_cols = ['size','pole','mean','stddev','b_mean','g_mean','r_mean','b_stddev','g_stddev','r_stddev','square','ratiowh','ratioarea','approxlen','numangle','numangle90','numangle70']
Xtest = datatest[feature_cols]
scaler = StandardScaler()
Xtest = scaler.fit_transform(Xtest)# Features
ytest = datatest.label # Target variable


y_predict= model.predict(Xtest)
y_pro = model.predict_proba(Xtest)[:,1]
# print(y_pro)


df = pd.DataFrame(datatest) 
df.insert(21, "predict", y_predict, True) 
df.insert(22, "lr_pro", y_pro , True) 
export_csv = df.to_csv ('decisiontree.csv', index = None)
# print(confusion_matrix(ytest, y_predict))
# tn, fp, fn, tp = confusion_matrix(ytest, y_predict, labels=[0,1]).ravel()
# print(tn,fp,fn,tp)
# with open('evaluation.csv', 'a') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow([tn,fp,fn,tp])
# csvfile.close()
# MCC = float((tp * tn - fp * fn)/ math.sqrt((tp + fp) * (fn + tn) * (fp + tn) * (tp + fn)))
# print(MCC)

images = {}
images_list = []
image = '1037587722'
label = 0
predict = 0
TP =0 
TN = 0 
FP = 0 
FN = 0 
with open('lrmodel.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if row['image'] == image: 
        label = label + int(float(row['label']))
        predict = predict + int(float(row['predict']))
      else: 
        image = row['image']
        if label > 0 and predict > 0:
          TP = TP  + 1 
        if label > 0 and predict == 0:
          FN = FN + 1 
        if label == 0 and predict > 0:
          FP = FP + 1 
        if label == 0 and predict == 0:
          TN = TN + 1 
        label = 0 
        predict = 0 

if label > 0 and predict > 0:
  TP = TP  + 1 
if label > 0 and predict == 0:
  FN = FN + 1 
if label == 0 and predict > 0:
  FP = FP + 1 
if label == 0 and predict == 0:
  TN = TN + 1 

metric = {}

ACCURACY = float((TP + TN)/(TP + FP + FN + TN))
PRECISION = float(TP/(TP + FP))
RECALL = float(TP/(TP + FN))
F1 = float(2*PRECISION*RECALL/(PRECISION + RECALL))
MCC = float((TP * TN - FP * FN)/ math.sqrt((TP + FP) * (FN + TN) * (FP + TN) * (TP + FN)))
SPECIFICITY = float(TN/(TN + FP))
metric['TP'] = float(TP/(TP + FN))
metric['FN']  = float(FN /(TP + FN))
metric['TN'] = float(TN /(TN + FP))
metric['FP']  =float(FP /(TN + FP))
metric['ACCURACY'] = ACCURACY
metric['PRECISION'] =PRECISION
metric['RECALL']= RECALL
metric['F1'] = F1
metric['MCC'] = MCC
metric['SPECIFICITY'] = SPECIFICITY
metric['description'] = 'decisiontree'
print(metric)
csvpath = 'evaluation.csv'
with open(csvpath,  'a') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([metric['description'],metric['TP'],metric['FN'],metric['TN'],metric['FP'],metric['ACCURACY'],metric['MCC'],metric['F1'],metric['SPECIFICITY'],metric['PRECISION'],metric['RECALL']])
csvfile.close()

# datatest = pd.read_csv("features_test.csv")
# datatest = datatest.dropna()
# feature_cols = ['size','pole','mean','stddev','b_mean','g_mean','r_mean','b_stddev','g_stddev','r_stddev','square','ratiowh','ratioarea','approxlen','numangle','numangle90','numangle70']
# Xtest = datatest[feature_cols]
# scaler = StandardScaler()
# Xtest = scaler.fit_transform(Xtest)# Features
# ytest = datatest.label # Target variable


# y_predict= model.predict(Xtest)
# y_pro = model.predict_proba(Xtest)[:,1]
# # print(y_pro)


# df = pd.DataFrame(datatest) 
# df.insert(21, "predict", y_predict, True) 
# df.insert(22, "lr_pro", y_pro , True) 
# export_csv = df.to_csv ('svm.csv', index = None)