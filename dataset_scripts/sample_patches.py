import glob
import argparse
import os
import numpy as np
from shutil import copy2


parser = argparse.ArgumentParser()
parser.add_argument("--input", "-i", type=str, default="../input/")
parser.add_argument("--output", "-o", type=str, default="../output/")
parser.add_argument("--number", "-n", type=int, default=20)
args = parser.parse_args()
print(args)
image_list = glob.glob(str(args.input) + "/*.jpg")
N = len(image_list)
os.makedirs(args.output, exist_ok=True)
sample_ids = np.random.randint(0, N, size=args.number)

sample_paths = np.array(image_list)[sample_ids]
for path in sample_paths:
    filename = os.path.basename(path)
    out_path = os.path.join(args.output, filename)
    copy2(path, out_path)

print("Number of copied files: " + str(args.number))
