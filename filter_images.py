import cv2
import glob
import argparse
import os
from shutil import copy2
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--input_dir", "-i", type=str, default="../patch_samples")
parser.add_argument("--output_dir", "-o", type=str, default="../output/")
parser.add_argument("--debug", "-d", action='store_true')
parser.add_argument("--visualize", "-v", action='store_true')
args = parser.parse_args()
colour_threshold = 200
percentage_white_threshold = 0.9

white = (255, 255, 255)
grey = (colour_threshold, colour_threshold, colour_threshold)
resolution = (512, 512)

os.makedirs(args.output_dir, exist_ok=True)
if args.debug:
    os.makedirs(args.output_dir + 'white_images', exist_ok=True)

for file in glob.glob(args.input_dir + "/*.jpg"):
    image = cv2.imread(file)
    mask = cv2.inRange(image, grey, white)
    if args.visualize:
        plt.subplot(1, 2, 1)
        plt.imshow(mask, cmap="gray")
        plt.subplot(1, 2, 2)
        plt.imshow(image)
        plt.show()

    white_pixels = np.sum(mask==255)
    # copy file if percentage of white is below threshold
    if white_pixels/(resolution[0]*resolution[1]) < percentage_white_threshold:
        copy2(file, args.output_dir)
    elif args.debug: # else only copy for debug
        copy2(file, args.output_dir + "white_images")

