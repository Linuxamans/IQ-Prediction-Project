# USAGE
# python rec_sign.py --dataset Train --test Test

# import the necessary packages
from __future__ import print_function
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from imutils import paths
import numpy as np
import argparse
import mahotas
import cv2
import pickle as cPickle

def describe(image):
	# extract the mean and standard deviation from each channel of the image
	# in the HSV color space
	image = cv2.resize(image,(500,500))
	(means, stds) = cv2.meanStdDev(cv2.cvtColor(image, cv2.COLOR_BGR2HSV))
	colorStats = np.concatenate([means, stds]).flatten()
	#print("The flattened array is ", colorStats)

	# extract Haralick texture features
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	haralick = mahotas.features.haralick(gray).mean(axis=0)

	# return a concatenated feature vector of color statistics and Haralick
	# texture features
	return np.concatenate([colorStats, haralick]).flatten() # we can also use np.hstack([colorStats, haralick])

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True, help="path to dataset")
ap.add_argument("-t", "--test", required=True, help="path to test ")
args = vars(ap.parse_args())
print("The args variable has ", args)

# grab the set of image paths and initialize the list of labels and matrix of
# features

print("[INFO] extracting features...")
imagePaths = sorted(paths.list_images(args["dataset"]))
labels = []
data = []

# loop over the images in the input directory
for imagePath in imagePaths:
	# extract the label and load the image from disk
	label = imagePath.split("/")[1]
	image = cv2.imread(imagePath)
	print("Labels are", label)
	# extract features from the image, then update the list of lables and
	# features
	features = describe(image)
	print ("Features are ", features)
	labels.append(label)
	data.append(features)

# construct the training and testing split by taking 75% of the data for training
# and 25% for testing
(trainData, testData, trainLabels, testLabels) = train_test_split(np.array(data),
	np.array(labels), test_size=0.25, random_state=42)

# initialize the model as a decision tree
model = DecisionTreeClassifier(random_state=84)



# train the decision tree
print("[INFO] training model...")
model.fit(trainData, trainLabels)

# evaluate the classifier
print("[INFO] evaluating...")
predictions = model.predict(testData)       #prediction 
print("The classification report is:\n")
print(classification_report(testLabels, predictions))

f = open("classifier.cPickle", "wb")
f.write(cPickle.dumps(model))
f.close()


imagePaths1 = sorted(paths.list_images(args["test"]))
print (imagePaths1)

# loop over a few random images													
for imagepath1 in imagePaths1:
	image1 = cv2.imread(imagepath1)
	show1 = cv2.resize(image1,(500,600))
	features = describe(image1)
	prediction = model.predict(features.reshape(1, -1))[0]
	print(prediction)

	# show the prediction
	print("[PREDICTION] {}".format(prediction))
	show1 = cv2.putText(show1, prediction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
	cv2.imshow("Image", show1)
	cv2.waitKey(0)



