# -*- coding: utf-8 -*-
"""
Original file is located at
https://pyimagesearch.com/2016/10/03/bubble-sheet-multiple-choice-scanner-and-test-grader-using-omr-python-and-opencv/
https://dontrepeatyourself.org/post/bubble-sheet-multiple-choice-test-with-opencv-and-python/
"""

# import the necessary packages
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import json
import imutils
import cv2
from pdf2image import convert_from_path
import os

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
ap.add_argument("-a", "--answers", required=True,
	help="path to the answers file")
ap.add_argument("-q", "--questions", required=True,
	help="Number of questions")
ap.add_argument("-r", "--responses", required=True,
	help="Number of possible answers")
args = vars(ap.parse_args())
# define the answer key which maps the question number
# to the correct answer
def keystoint(x):
    return {int(k): v for k, v in x.items()}

# split the thresholded image into boxes
def split_image(image, questions, answers):
    # make the number of rows and columns 
    # a multiple of 5 (questions = answers = 5)
    r = len(image) // questions * questions 
    c = len(image[0]) // answers * answers
    image = image[:r, :c]
    # split the image horizontally (row-wise)
    rows = np.vsplit(image, questions)
    boxes = []
    for row in rows:
        # split each row vertically (column-wise)
        cols = np.hsplit(row, answers)
        for box in cols:
            boxes.append(box)
    return boxes

with open(args["answers"]) as f:
    ANSWER_KEY = json.load(f, object_hook=keystoint)

correct_ans = list(ANSWER_KEY.values())

questions = int(args["questions"])
answers = int(args["responses"])

fn = args["image"]

if '.pdf' in fn:
    page = convert_from_path(fn)
    page[0].save(fn.replace('pdf', 'png'), "png")
    fn = fn.replace('pdf', 'png')
    image = cv2.imread(fn)
    os.remove(fn)
else:
    image = cv2.imread(fn)

# load the image, convert it to grayscale, blur it
# slightly, then find edges
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 75, 200)

# find contours in the edge map, then initialize
# the contour that corresponds to the document
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
docCnt = None
# ensure that at least one contour was found
if len(cnts) > 0:
	# sort the contours according to their size in
	# descending order
	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
	# loop over the sorted contours
	for c in cnts:
		# approximate the contour
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
		# if our approximated contour has four points,
		# then we can assume we have found the paper
		if len(approx) == 4:
			docCnt = approx
			break

# apply a four point perspective transform to both the
# original image and grayscale image to obtain a top-down
# birds eye view of the paper
paper = four_point_transform(image, docCnt.reshape(4, 2))
warped = four_point_transform(gray, docCnt.reshape(4, 2))

# apply Otsu's thresholding method to binarize the warped
# piece of paper
thresh = cv2.threshold(warped, 0, 255,
	cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

boxes = split_image(thresh, questions, answers)

score = 0

# loop over the questions
for i in range(0, questions):
    user_answer = None

    # loop over the answers
    for j in range(answers):
        pixels = cv2.countNonZero(boxes[j + i * 5])
        # if the current answer has a larger number of
        # non-zero (white) pixels then the previous one
        # we update the `user_answer` variable
        if user_answer is None or pixels > user_answer[1]:
            user_answer = (j, pixels)
    # find the contours of the bubble that the user has filled
    cnt, _ = cv2.findContours(boxes[user_answer[0] + i * 5],
                                      cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if correct_ans[i] == user_answer[0]:
        score += 1

print("The score is:", score/questions)
