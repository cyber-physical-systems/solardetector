# -*- coding: utf-8 -*-
"""Solar_detector_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DKl6Enkvt3L6197pEiZKEgNIy858vyI9

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
my_dataset_train_metadata = MetadataCatalog.get("my_dataset_train")
dataset_dicts = DatasetCatalog.get("my_dataset_train")

import random
from detectron2.utils.visualizer import Visualizer

for d in random.sample(dataset_dicts, 5):
    # print(d)
    ann = d['annotations']
    # print(ann)
    classes = []
    for j, b in enumerate(ann):
      print(j,b['category_id'])
      classes.append(b['category_id'])
    class_names = MetadataCatalog.get("my_dataset_train").thing_classes
    gt_class_names = list(map(lambda x: class_names[x], classes))
    print(gt_class_names)



    # print(ann["segmentation"])
    img = cv2.imread(d["file_name"])
    visualizer = Visualizer(img[:, :, ::-1], metadata=my_dataset_train_metadata, scale=0.5)
    vis = visualizer.draw_dataset_dict(d)
    cv2_imshow(vis.get_image()[:, :, ::-1])

"""# Train Custom Detectron2 Detector"""

#We are importing our own Trainer Module here to use the COCO validation evaluation during training. Otherwise no validation eval occurs.

from detectron2.engine import DefaultTrainer
from detectron2.evaluation import COCOEvaluator

class CocoTrainer(DefaultTrainer):

  @classmethod
  def build_evaluator(cls, cfg, dataset_name, output_folder=None):

    if output_folder is None:
        os.makedirs("coco_eval", exist_ok=True)
        output_folder = "coco_eval"

    return COCOEvaluator(dataset_name, cfg, False, output_folder)

# from detectron2.tools.train_net import Trainer
# from detectron2.engine import DefaultTrainer
# select from modelzoo here: https://github.com/facebookresearch/detectron2/blob/master/MODEL_ZOO.md#coco-object-detection-baselines

from detectron2.config import get_cfg
from detectron2.evaluation.coco_evaluation import COCOEvaluator
import os

cfg = get_cfg()
# cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"))
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
cfg.DATASETS.TRAIN = ("my_dataset_train",)
cfg.DATASETS.TEST = ("my_dataset_val",)

cfg.DATALOADER.NUM_WORKERS = 4
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")  # Let training initialize from model zoo
cfg.SOLVER.IMS_PER_BATCH = 4
cfg.SOLVER.BASE_LR = 0.001


cfg.SOLVER.WARMUP_ITERS = 200
cfg.SOLVER.MAX_ITER = 2000 #adjust up if val mAP is still rising, adjust down if overfit
cfg.SOLVER.STEPS = (1000, 1500)
cfg.SOLVER.GAMMA = 0.05




cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 64
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 6 #your number of classes + 1

cfg.TEST.EVAL_PERIOD = 200


os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
trainer = CocoTrainer(cfg)
trainer.resume_or_load(resume=False)
# trainer.train()

# Look at training curves in tensorboard:
# %load_ext tensorboard
# %tensorboard --logdir output

#test evaluation
# from detectron2.data import DatasetCatalog, MetadataCatalog, build_detection_test_loader
# from detectron2.evaluation import COCOEvaluator, inference_on_dataset

# cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
# cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.90
# predictor = DefaultPredictor(cfg)
# evaluator = COCOEvaluator("my_dataset_test", cfg, False, output_dir="./output/")
# val_loader = build_detection_test_loader(cfg, "my_dataset_test")
# inference_on_dataset(trainer.model, val_loader, evaluator)

"""# Inference with Detectron2 Saved Weights


"""

# Commented out IPython magic to ensure Python compatibility.
# %ls ./output/

cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")
cfg.DATASETS.TEST = ("my_dataset_test", )
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7 # set the testing threshold for this model
predictor = DefaultPredictor(cfg)
test_metadata = MetadataCatalog.get("my_dataset_test")

# from detectron2.utils.visualizer import ColorMode
# import glob
# i = 0 
# for imageName in glob.glob('/content/train/*.jpg'):
#   i = i + 1
#   if i <10:
#     im = cv2.imread(imageName)
#     # cv2_imshow(im)
#     outputs = predictor(im)
#     v = Visualizer(im[:, :, ::-1],
#                   metadata=test_metadata, 
#                   scale=0.8
#                   )
#     out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
#     cv2_imshow(out.get_image()[:, :, ::-1])
#   else:
#     pass

# from detectron2.utils.visualizer import ColorMode
# import glob
# i = 0 

# for imageName in glob.glob('/content/train/*.jpg'):
#   i = i + 1
#   if i <10:
#     im = cv2.imread(imageName)
#     # cv2_imshow(im)
#     outputs = predictor(im)
#     pred_classes = outputs['instances'].pred_classes.cpu().tolist()
#     class_names = MetadataCatalog.get("my_dataset_train").thing_classes
#     pred_class_names = list(map(lambda x: class_names[x], pred_classes))
#     print(pred_class_names)
#   else:
#     pass

#visualize training data
import math
my_dataset_train_metadata = MetadataCatalog.get("my_dataset_test")
dataset_dicts = DatasetCatalog.get("my_dataset_test")

import random
from detectron2.utils.visualizer import Visualizer
import csv

ojects_list = ['panels','shadow','window','chimney','trees']
for object_ in ojects_list:
  TP = 0
  TN = 0
  FP = 0
  FN = 0
  for d in dataset_dicts : 
      im = cv2.imread(d['file_name'])
      ann = d['annotations']
      classes = []
      for j, b in enumerate(ann):    
        classes.append(b['category_id'])
      class_names = MetadataCatalog.get("my_dataset_val").thing_classes
      gt_class_names = list(map(lambda x: class_names[x], classes))
      outputs = predictor(im)
      pred_classes = outputs['instances'].pred_classes.cpu().tolist()
      class_names = MetadataCatalog.get("my_dataset_val").thing_classes
      pred_class_names = list(map(lambda x: class_names[x], pred_classes))
      if object_ in gt_class_names : 
        if  object_ in pred_class_names : 
          TP = TP + 1 
        else:
          FN = FN + 1
      else:
        if  object_ in pred_class_names : 
          FP = FP + 1
        else:
          TN = TN + 1
  try:
    MCC = float((TP * TN - FP * FN)/ math.sqrt((TP + FP) * (FN + TN) * (FP + TN) * (TP + FN)))
  except ZeroDivisionError:
    MCC = 0


  with open('final_original_test.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([object_, TP, TN, FP, FN, MCC])
      # print( object_, TP, TN, FP, FN, MCC)

# visualize training data
import math
my_dataset_train_metadata = MetadataCatalog.get("my_dataset_test")
dataset_dicts = DatasetCatalog.get("my_dataset_test")

import random
from detectron2.utils.visualizer import Visualizer
import csv
from detectron2.structures import Boxes
import numpy 
import cv2

# ojects_list = ['panels','shadow','window','chimney','trees']
ojects_list = ['panels']
# panel is 2, shadow is 3, trees 5 
i = 0 
orientation =0 
for object_ in ojects_list:

  for d in dataset_dicts : 
      im = cv2.imread(d['file_name'])
      ann = d['annotations']
      bounding_box = []
      for j, b in enumerate(ann): 
        if b['category_id'] == 2:
          bounding_box.append(b['bbox'])
      
      if bounding_box != []:
        outputs = predictor(im)
        category_2 = outputs['instances'][outputs['instances'].pred_classes == 2]
        # print(category_2_detections)
        category_2_detections = category_2.pred_boxes.tensor.cpu().numpy()
        if category_2_detections !=[]:
          img = numpy.zeros(im.shape).astype(im.dtype)
          # print(img.shape)
          for bounding in bounding_box:
            Bounding = [[bounding[0],bounding[1]],
                        [bounding[0]+bounding[2],bounding[1]],
                        [bounding[0]+bounding[2],bounding[1]+bounding[3] ],
                        [bounding[0],bounding[1]+bounding[3]]]
            contours = [numpy.array(Bounding)]
            print(contours)
            color = [255, 255, 255]
            # print(contours)
            cv2.fillPoly(img, np.int32([contours]), color)
 
          # result1 = cv2.bitwise_and(im, img)
          # result1 = cv2.cvtColor(result1, cv2.COLOR_BGR2RGB)
        
          # Img = numpy.zeros(im.shape).astype(im.dtype)

          
          # for category_2 in category_2_detections:
          #   Category_2= [[category_2[0],category_2[1]],
          #               [category_2[0]+category_2[2],category_2[1]],
          #               [category_2[0]+category_2[2],category_2[1]+category_2[3] ],
          #               [category_2[0],category_2[1]+category_2[3]]]            
            
          #   contours = [numpy.array(Category_2)]
#             color = [255, 255, 255]
#             cv2.fillPoly(Img, np.int32(contours), color)
#           result2 = cv2.bitwise_and(im, Img)
#           result2 = cv2.cvtColor(result2, cv2.COLOR_BGR2RGB)

#           intersection = numpy.logical_and(result1, result2)
#           union = numpy.logical_or(result1, result2)
#           iou_score = numpy.sum(intersection) / numpy.sum(union)
#           if iou_score > 0.1: 
#             IOU = IOU + iou_score
#             i = i + 1

# print(IOU)
# # print(IOU/i)

# ! rm -r train
# ! rm -r test
# ! rm -r valid
# ! rm README.dataset.txt
# ! rm README.roboflow.txt

# !curl -L "https://app.roboflow.com/ds/VjRZp3DBVM?key=IP7ljQ3VbH" > roboflow.zip; unzip roboflow.zip; rm roboflow.zip

# from detectron2.data.datasets import register_coco_instances
# register_coco_instances("my_dataset_train_", {}, "/content/train/_annotations.coco.json", "/content/train")
# register_coco_instances("my_dataset_val_", {}, "/content/valid/_annotations.coco.json", "/content/valid")
# register_coco_instances("my_dataset_test_", {}, "/content/test/_annotations.coco.json", "/content/test")

# #visualize training data
# import math
# my_dataset_train_metadata = MetadataCatalog.get("my_dataset_test_")
# dataset_dicts = DatasetCatalog.get("my_dataset_test_")

# import random
# from detectron2.utils.visualizer import Visualizer
# import csv

# ojects_list = ['panels','shadow','window','chimney','trees']
# for object_ in ojects_list:
#   TP = 0
#   TN = 0
#   FP = 0
#   FN = 0
#   for d in dataset_dicts : 
#       im = cv2.imread(d['file_name'])
#       ann = d['annotations']
#       classes = []
#       for j, b in enumerate(ann):    
#         classes.append(b['category_id'])
#       class_names = MetadataCatalog.get("my_dataset_test_").thing_classes
#       gt_class_names = list(map(lambda x: class_names[x], classes))
#       outputs = predictor(im)
#       pred_classes = outputs['instances'].pred_classes.cpu().tolist()
#       class_names = MetadataCatalog.get("my_dataset_test_").thing_classes
#       pred_class_names = list(map(lambda x: class_names[x], pred_classes))
#       if object_ in gt_class_names : 
#         if  object_ in pred_class_names : 
#           TP = TP + 1 
#         else:
#           FN = FN + 1
#       else:
#         if  object_ in pred_class_names : 
#           FP = FP + 1
#         else:
#           TN = TN + 1
#   try:
#     MCC = float((TP * TN - FP * FN)/ math.sqrt((TP + FP) * (FN + TN) * (FP + TN) * (TP + FN)))
#   except ZeroDivisionError:
#     MCC = 0


#   with open('augmentation_train_original_test.csv', 'a', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow([object_, TP, TN, FP, FN, MCC])
#       # print( object_, TP, TN, FP, FN, MCC)

# !curl -L "https://app.roboflow.com/ds/EQfrwXHcyv?key=G3EkHnVCo6" > ./augmentation_test/roboflow_original.zip; unzip ./augmentation_test/roboflow_original.zip -d ./augmentation_test/; rm ./augmentation_test/roboflow_original.zip

# from detectron2.data.datasets import register_coco_instances
# register_coco_instances("my_dataset_augmentation_test_test", {}, "/content/augmentation_test/train/_annotations.coco.json", "/content/augmentation_test/train")

#visualize training data
# import math
# my_dataset_train_metadata = MetadataCatalog.get("my_dataset_augmentation_test_test")
# dataset_dicts = DatasetCatalog.get("my_dataset_augmentation_test_test")

# import random
# from detectron2.utils.visualizer import Visualizer
# import csv
# from detectron2.structures import Boxes
# import numpy 
# import cv2

# # ojects_list = ['panels','shadow','window','chimney','trees']
# ojects_list = ['trees']
# # panel is 2, shadow is 3, trees 5 
# i = 0 
# IOU =0 
# for object_ in ojects_list:

#   for d in dataset_dicts : 
#       im = cv2.imread(d['file_name'])
#       ann = d['annotations']
#       bounding_box = []
#       for j, b in enumerate(ann): 
#         if b['category_id'] == 5:
#           bounding_box.append(b['bbox'])
      
#       if bounding_box != []:
        # outputs = predictor(im)
        # category_2 = outputs['instances'][outputs['instances'].pred_classes == 5]
        # # print(category_2_detections)
        # category_2_detections = category_2.pred_boxes.tensor.cpu().numpy()
        # if category_2_detections !=[]:
        #   img = numpy.zeros(im.shape).astype(im.dtype)
        #   # print(img.shape)
        #   for bounding in bounding_box:
        #     Bounding = [[bounding[0],bounding[1]],
        #                 [bounding[0]+bounding[2],bounding[1]],
        #                 [bounding[0]+bounding[2],bounding[1]+bounding[3] ],
        #                 [bounding[0],bounding[1]+bounding[3]]]
        #     contours = [numpy.array(Bounding)]
        #     color = [255, 255, 255]
        #     # print(contours)
        #     cv2.fillPoly(img, np.int32([contours]), color)
        #   result1 = cv2.bitwise_and(im, img)
        #   result1 = cv2.cvtColor(result1, cv2.COLOR_BGR2RGB)
        
        #   Img = numpy.zeros(im.shape).astype(im.dtype)

          
#           for category_2 in category_2_detections:
#             Category_2= [[category_2[0],category_2[1]],
#                         [category_2[0]+category_2[2],category_2[1]],
#                         [category_2[0]+category_2[2],category_2[1]+category_2[3] ],
#                         [category_2[0],category_2[1]+category_2[3]]]            
            
#             contours = [numpy.array(Category_2)]
#             color = [255, 255, 255]
#             cv2.fillPoly(Img, np.int32(contours), color)
#           result2 = cv2.bitwise_and(im, Img)
#           result2 = cv2.cvtColor(result2, cv2.COLOR_BGR2RGB)

#           intersection = numpy.logical_and(result1, result2)
#           union = numpy.logical_or(result1, result2)
#           iou_score = numpy.sum(intersection) / numpy.sum(union)
#           if iou_score > 0.1: 
#             IOU = IOU + iou_score
#             i = i + 1

# print(IOU)
# # print(IOU/i)





  

        # print("prediction", category_2_detections.pred_boxes.tensor.cpu().numpy())

#visualize training data
# import math
# my_dataset_train_metadata = MetadataCatalog.get("my_dataset_augmentation_test_test")
# dataset_dicts = DatasetCatalog.get("my_dataset_augmentation_test_test")

# import random
# from detectron2.utils.visualizer import Visualizer
# import csv
# from detectron2.structures import Boxes
# import numpy 
# import cv2

# # ojects_list = ['panels','shadow','window','chimney','trees']
# ojects_list = ['panels']
# # panel is 2, shadow is 3, trees 5 
# TP = 0
# TN = 0 
# FP = 0 
# FN = 0 
# for object_ in ojects_list:

#   for d in dataset_dicts : 
#       im = cv2.imread(d['file_name'])
#       ann = d['annotations']
#       bounding_box = []
#       for j, b in enumerate(ann): 
#         if b['category_id'] == 2:
#           bounding_box.append(b['bbox'])
     
#       if bounding_box != []:
        
#         outputs = predictor(im)
#         category_2 = outputs['instances'][outputs['instances'].pred_classes == 2]
#         # print(category_2_detections)
#         pred_classes = category_2.pred_classes.cpu().tolist()
#         if pred_classes != []:
#           if len(bounding_box) > 1:
#             if len(pred_classes) > 1:
#               TP = TP + 1
#             else:
#               FN = FN + 1
#           if len(bounding_box) == 1:
#             if len(pred_classes) == 1:
#               TN = TN + 1
#             else:
#               FP = FP + 1


# print(TP, TN, FP, FN)     
# MCC = float((TP * TN - FP * FN)/ math.sqrt((TP + FP) * (FN + TN) * (FP + TN) * (TP + FN))) 
# print(MCC)