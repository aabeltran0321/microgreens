# Import packages
import os
import cv2
import numpy as np
import sys
import glob
import importlib.util
from tensorflow.lite.python.interpreter import Interpreter
from config import min_conf_threshold


### Define function for inferencing with TFLite model and displaying results

# Load the label map into memory
with open("labelmap.txt", 'r') as f:
        labels = [line.strip() for line in f.readlines()]

# Load the Tensorflow Lite model into memory
modelpath="detect.tflite"
interpreter = Interpreter(model_path=modelpath)
interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

float_input = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

  #Confidence threshold (try changing this to 0.01 if you don't see any detection results)

def detection_process(image):
        interpreter = Interpreter(model_path=modelpath)
        interpreter.allocate_tensors()

        # Get model details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()        
        # Load image and resize to expected shape [1xHxWx3]
        if isinstance(image,str):
                image = cv2.imread(image)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imH, imW, _ = image.shape 
        image_resized = cv2.resize(image_rgb, (width, height))
        input_data = np.expand_dims(image_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if float_input:
                input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[1]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[3]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(output_details[0]['index'])[0] # Confidence of detected objects
        return image, boxes, classes, scores


def framers(image, boxes, classes, scores):
        # Loop over all detections and draw detection box if confidence is above minimum threshold
        #print(classes,scores)
        imH, imW, _ = image.shape 
        num_recognized = 0
        for i in range(len(scores)):
                if (scores[i] > min_conf_threshold):
        
                        # Get bounding box coordinates and draw box
                        # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                        ymin = int(max(1,(boxes[i][0] * imH)))
                        xmin = int(max(1,(boxes[i][1] * imW)))
                        ymax = int(min(imH,(boxes[i][2] * imH)))
                        xmax = int(min(imW,(boxes[i][3] * imW)))
                
                        cv2.rectangle(image, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
                        cv2.putText(image, f"{labels[int(classes[i])]} - {round(scores[i]*100,1)}%", (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        #return image,xmin,ymin,xmax,ymax,labels[int(classes[i])]
                        return image, f"{labels[int(classes[i])]}"

        return image, ""

if __name__=="__main__":
        # fname = "cone.jpg"#r"images\test\-0ACAD937-70A4-46F0-8E49-0CAE6F942CF2-png_jpg.rf.17ff21f067f60d0e78b4189f11a53ece.jpg"
        # frame = cv2.imread(fname)
        # h,w,s = frame.shape  
        # #frame = cv2.resize(frame,(int(w/3), int(h/3)))
        # #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # frame, boxes, classes, scores=detection_process(frame)
        # frame, num_recog = framers(frame, boxes,classes,scores)
        # cv2.imshow("data",frame)
        # #cv2.imwrite(f"images/results/{a}",frame)
        # cv2.waitKey(0)

        cap = cv2.videoCapture(0)

        while True:
                ret, frame = cap.read()

                if ret:
                        frame, boxes, classes, scores=detection_process(frame)
                        frame, num_recog = framers(frame, boxes,classes,scores)

                        cv2.imshow("frame", frame)
                        cv2.waitKey(1)