# -*- coding: utf-8 -*-
"""contours_models.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eeF--9QNR2otpMQQK-PLJXyy8pF4vWBG

# Install Detectron2 Dependencies
"""

# install dependencies: (use cu101 because colab has CUDA 10.1)
!pip install -U torch==1.5 torchvision==0.6 -f https://download.pytorch.org/whl/cu101/torch_stable.html 
!pip install cython pyyaml==5.1
!pip install -U 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
import torch, torchvision
print(torch.__version__, torch.cuda.is_available())
!gcc --version
# opencv is pre-installed on colab

# install detectron2:
!pip install detectron2==0.1.3 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu101/torch1.5/index.html

!pip install opencv-python==4.1.2.30

# You may need to restart your runtime prior to this, to let your installation take effect
# Some basic setup:
# Setup detectron2 logger

import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import numpy as np
import cv2
import random
from google.colab.patches import cv2_imshow

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog
from detectron2.data.catalog import DatasetCatalog

"""# Import and Register Custom Detectron2 Data"""

!curl -L "https://app.roboflow.com/ds/s80NQUD0ur?key=sn8EDUMqdN" > roboflow.zip; unzip roboflow.zip; rm roboflow.zip

from detectron2.data.datasets import register_coco_instances
register_coco_instances("my_dataset_train", {}, "/content/train/_annotations.coco.json", "/content/train")
register_coco_instances("my_dataset_val", {}, "/content/valid/_annotations.coco.json", "/content/valid")
register_coco_instances("my_dataset_test", {}, "/content/test/_annotations.coco.json", "/content/test")

#visualize training data
my_dataset_train_metadata = MetadataCatalog.get("my_dataset_test")
dataset_dicts = DatasetCatalog.get("my_dataset_test")

import random
from detectron2.utils.visualizer import Visualizer
print(len(dataset_dicts))
image_name = []
for d in random.sample(dataset_dicts, len(dataset_dicts)):
    name = d["file_name"].split("/")[-1]
    Name = name.split(".")[0]
    NAME = Name.split("_")[0]
    image_name.append(NAME)
print(image_name)

"""# Get the contours features"""

!rm -r house10

!mv roof_/*.png house7/roof/

!unzip roof_.zip

import csv 
import os
import cv2
import glob as gb
import numpy as np
import math

house_number = "7"

def getContourStat(img, contour):
    mask = np.zeros((800,800), dtype="uint8")
    cv2.drawContours(mask, [contour], -1, 255, -1)
    mean, stddev = cv2.meanStdDev(img, mask=mask)
    return mean, stddev
def cal_roofarea(image):
    black = cv2.threshold(image, 0, 255, 0)[1]
    contours, hierarchy = cv2.findContours(black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # cv2.drawContours(img, contours, -1, (255, 0, 0), 2)
    area = [cv2.contourArea(c) for c in contours]
    roof_index = np.argmax(area)
    roof_cnt = contours[roof_index]
    # contourArea will return the wrong value if the contours are self-intersections
    roof_area = cv2.contourArea(roof_cnt)
    #print('roof area = '+ str(roof_area))
    return (roof_area,roof_cnt)


def pole(img, contour):
    ori_img = img.copy()
    image_grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cont = cal_roofarea(image_grayscale)[1]
    cv2.drawContours(ori_img, cont, -1, (255, 0, 0), 3)
    #print(len(contour))
    contour_res =[]
    back = 1
    cnt = contour
    leftmost = tuple(cnt[cnt[:, :, 0].argmin()][0])
    rightmost = tuple(cnt[cnt[:, :, 0].argmax()][0])
    topmost = tuple(cnt[cnt[:, :, 1].argmin()][0])
    bottommost = tuple(cnt[cnt[:, :, 1].argmax()][0])
    pole = [leftmost,rightmost,topmost,bottommost]
    for point in pole:
        # check the distance with contours, biggest contour
        # when it is negative, means the point is outside the contours
        dist = cv2.pointPolygonTest(cont, point, True)
        # print(dist)
        if (dist <=0):
            back = 0
        else:
            pass
    return (ori_img,contour,back)
def rotate_rectangle(img_name,img, contour):

    shape= {}
    shape['id'] = img_name
# for c in contour:
    c = contour
    
    area = cv2.contourArea(c)
    x,y,w,h = cv2.boundingRect(c)
    ratiowh  =  min(float(w/h),float(h/w))
    shape['ratiowh'] = ratiowh

    ratioarea = float(area/(w*h))
    shape['ratioarea'] = ratioarea

    epsilon = 0.01 * cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, epsilon, True)

    approxlen = len(approx)
    shape['approxlen'] = approxlen


    #  the original num set to be -1 to be different no operation
    num_angle = 0
    num_angle90 = -1
    num_angle80 = -1
    num_angle70 = -1
    mask = np.zeros(img.shape, np.uint8)
    cv2.drawContours(mask, [approx], -1, (255, 255, 255), -1)
    cv2.drawContours(img, [approx], -1, (255, 255, 255), 2)
    # mask = np.concatenate((mask, mask, mask), axis=-1)
    gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    contour_list = []
    ret, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # get the list of contours
    for points in contours[0]:
        x, y = points.ravel()
        contour_list.append([x, y])
    corners = cv2.goodFeaturesToTrack(gray, 50, 0.01, 10)
    corners = np.int0(corners)
    for i in corners:
        x, y = i.ravel()
        #  decide whether the corner is on the contours
        if (cv2.pointPolygonTest(contours[0], (x, y), True) == 0):
            center_index = contour_list.index([x, y])
            length = len(contour_list)
            # get the point three before, and ignore the end point
            a_index = center_index - 5
            b_index = center_index + 5
            if ((a_index > 0) & (b_index > 0) & (a_index < length)& (b_index < length)):
                xa, ya = contour_list[a_index]
                xb, yb = contour_list[b_index]
                # print(x , y)
                # print(xa, ya)
                a = math.sqrt((x - xa) * (x - xa) + (y - ya) * (y - ya))
                b = math.sqrt((x - xb) * (x - xb) + (y - yb) * (y - yb))
                c = math.sqrt((xa - xb) * (xa - xb) + (ya - yb) * (ya - yb))
                if ((a > 0) & (b > 0)):
                    if(((a * a + b * b - c * c) / (2 * a * b))<1) & (((a * a + b * b - c * c) / (2 * a * b) >-1)):
                        angle = math.degrees(math.acos((a * a + b * b - c * c) / (2 * a * b)))
                        num_angle =num_angle +1
                        # print(angle)
                        if (angle < 90):
                            num_angle90 = num_angle90 + 1
                        if (angle < 80):
                            num_angle80 = num_angle80 + 1
                        if (angle < 70):
                            num_angle70 = num_angle70 + 1
        cv2.circle(img, (x, y), 5, 255, -1)

    shape['numangle'] = num_angle
    shape['numangle90'] = num_angle90
    shape['numangle80'] = num_angle80
    shape['numangle70'] = num_angle70
    return(shape)

csvpath_all = '/content/' + 'features.csv'

# with open(csvpath_all, 'a') as csvfile:
#     myFields = ['id','location','image', 'size','pole','mean','stddev','b_mean','g_mean','r_mean',
#                 'b_stddev','g_stddev','r_stddev','square','ratiowh','ratioarea','approxlen','numangle',
#                 'numangle90','numangle70','label']
#     writer = csv.DictWriter(csvfile, fieldnames=myFields)
#     writer.writeheader()
# csvfile.close()

csv_path = '/content/house' + str(house_number)  + '/contourlabel.csv'

with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      if row['id'].split('_')[0] in image_name:
        print(row['id'])
        contour = row
        img_path = '/content/house' + str(house_number)  + '/roof/' + row['id'].split('_')[0] +'.png'
        npy_path = '/content/house' + str(house_number)  + '/contour/' + row['id'] + '.npy'
        img = cv2.imread(img_path)
        if img is not None:
          c = np.load(npy_path)
          image_grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
          mean = getContourStat(image_grayscale, c)[0]
          # print(getContourStat(image_grayscale, c))
          stddev =getContourStat(image_grayscale, c)[1]

          contour['mean'] = mean[0][0]
          contour['stddev'] = stddev[0][0]
          mean_all = getContourStat(img, c)[0]
          stddev_all = getContourStat(img, c)[1]
          contour['b_mean'] =  mean_all[0][0]
          contour['g_mean'] =  mean_all[1][0]
          contour['r_mean'] =  mean_all[2][0]
          contour['b_stddev'] =  stddev_all[0][0]
          contour['g_stddev'] =  stddev_all[1][0]
          contour['r_stddev'] =  stddev_all[2][0]   
          contour['location'] = house_number
          contour['image'] = row['id'].split('_')[0]
          contour['pole'] = pole(img.copy(), c)[2]
          area = cv2.contourArea(c)
          perimeter = cv2.arcLength(c, True)
          sq = 4 * math.pi * area / (perimeter * perimeter)
          contour['square'] = sq
          # print(sq)
          shape = rotate_rectangle(row['id'].split('_')[0],img.copy(), c)
          contour['ratiowh'] =  shape['ratiowh']
          contour['ratioarea'] = shape['ratioarea']
          contour['approxlen'] = shape['approxlen']
          contour['numangle'] = shape['numangle']
          contour['numangle90'] = shape['numangle90']
          contour['numangle70'] = shape['numangle70']

          with open(csvpath_all, 'a') as csvfile:
              writer = csv.writer(csvfile)
              writer.writerow([contour['id'], contour['location'],contour['image'],contour['size'],
    contour['pole'],contour['mean'],contour['stddev'],contour['b_mean'],contour['g_mean'],contour['r_mean'],
    contour['b_stddev'],contour['g_stddev'],contour['r_stddev'],contour['square'],contour['ratiowh'],
    contour['ratioarea'],contour['approxlen'],contour['numangle'],contour['numangle90'], 
    contour['numangle70'],contour['label']])
          csvfile.close()

