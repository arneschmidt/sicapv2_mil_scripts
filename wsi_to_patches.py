import cv2
import glob
import argparse
import os
from shutil import copy2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def contains_tissue(image):
    colour_threshold = 200
    percentage_white_threshold = 0.9

    white = (255, 255, 255)
    grey = (colour_threshold, colour_threshold, colour_threshold)
    resolution = (512, 512)

    mask = cv2.inRange(image, grey, white)

    white_pixels = np.sum(mask==255)
    # copy file if percentage of white is below threshold
    if white_pixels/(resolution[0]*resolution[1]) < percentage_white_threshold:
        return True
    else: # else only copy for debug
        return False

def slice_image(wsi, wsi_path, resolution, image_path):
    wsi_name = os.path.basename(wsi_path).split('.')[0]
    h, w, _ = wsi.shape
    num_patches_per_row = int(2*np.floor((h/resolution)) - 1)
    num_patches_per_column = int(2*np.floor((w/resolution)) - 1)

    names = []
    wsi_df = pd.DataFrame(columns=['image_name', 'NC', 'G3', 'G4', 'G5', 'unlabeled'])
    for row in range(num_patches_per_row):
        for column in range(num_patches_per_column):
            start_y = int(row*(resolution/2))
            start_x = int(column*(resolution/2))
            patch = wsi[start_y:start_y+resolution, start_x:start_x+resolution]
            if contains_tissue(patch):
                name = wsi_name + '_' + str(row) + '_' + str(column) + '.jpg'
                names.append(name)
                cv2.imwrite(os.path.join(image_path, name), patch)
    wsi_df['image_name'] = names
    wsi_df['NC'] = 0
    wsi_df['G3'] = 0
    wsi_df['G4'] = 0
    wsi_df['G5'] = 0
    wsi_df['unlabeled'] = 1
    return wsi_df


def main(args):
    if args.wsi_list == 'all':
        wsi_list = glob.glob(str(args.image_dir) + "/*.jpg")
    else:
        file = open(args.wsi_list, 'r')
        wsi_list = file.readlines()
    print(' WSI list: ' )
    print(wsi_list)

    number_of_wsi = len(wsi_list)
    image_dir = os.path.join(args.output_dir, 'images')
    print('number_of_wsi  ', number_of_wsi)

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)
    df = pd.DataFrame(columns=['image_name', 'NC', 'G3', 'G4', 'G5', 'unlabeled'])

    for wsi_path in wsi_list:
        print('Slice WSI ' + wsi_path)
        wsi = cv2.imread(wsi_path)
        wsi_df = slice_image(wsi, wsi_path, args.patch_resolution, image_dir)
        df = pd.concat([df, wsi_df])
    df.to_excel(os.path.join(args.output_dir,"Train.xlsx"), index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", "-i", type=str, default="/home/arne/datasets/SICAPv2_add_wsi/slides")
    parser.add_argument("--wsi_list", "-w", type=str, default="all")
    parser.add_argument("--output_dir", "-o", type=str, default="./output/")
    parser.add_argument("--patch_overlap", "-po", action='store_true')
    parser.add_argument("--patch_resolution", "-pr", type=int, default=512)
    parser.add_argument("--debug", "-d", action='store_true')
    args = parser.parse_args()
    main(args)