import cv2
import glob
import argparse
import os
from shutil import copy2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random

def contains_tissue(image):
    colour_threshold = 200
    percentage_white_threshold = 0.8
    blurr_threshold = 70

    white = (255, 255, 255)
    grey = (colour_threshold, colour_threshold, colour_threshold)
    resolution = (512, 512)

    mask = cv2.inRange(image, grey, white)
    white_pixels = np.sum(mask==255)
    not_white = (white_pixels / (resolution[0] * resolution[1]) < percentage_white_threshold)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    not_blurry = fm > blurr_threshold

    # copy file if percentage of white is below threshold
    if not_white and not_blurry:
        return True
    else: # else only copy for debug
        # if not not_white:
        #     print('Patch white!')
        # elif not not_blurry:
        #     print('Patch blurry!')
        return False

def init_patch_df(existing_patch_df):
    if existing_patch_df == 'None':
        df = pd.DataFrame(columns=['image_name', 'NC', 'G3', 'G4', 'G4C', 'G5', 'unlabeled'])
    else:
        df = pd.read_excel(existing_patch_df)
    return df

def slice_image(wsi, wsi_path, wsi_df, resolution, image_path, dataframes_only):
    wsi_name = os.path.basename(wsi_path).split('.')[0]
    h, w, _ = wsi.shape
    num_patches_per_row = int(2*np.floor((h/resolution)) - 1)
    num_patches_per_column = int(2*np.floor((w/resolution)) - 1)

    wsi_row = wsi_df[wsi_df['slide_id']==wsi_name]
    assert len(wsi_row) == 1
    negative_slide = (int(wsi_row['Gleason_primary'])==0)
    names = []
    patch_df = pd.DataFrame(columns=['image_name', 'NC', 'G3', 'G4', 'G5', 'unlabeled'])
    for row in range(num_patches_per_row):
        for column in range(num_patches_per_column):
            start_y = int(row*(resolution/2))
            start_x = int(column*(resolution/2))
            patch = wsi[start_y:start_y+resolution, start_x:start_x+resolution]
            if contains_tissue(patch):
                name = wsi_name + '_' + str(row) + '_' + str(column) + '.jpg'
                names.append(name)
                if not dataframes_only:
                    cv2.imwrite(os.path.join(image_path, name), patch)

    patch_df['image_name'] = names
    if negative_slide:
        patch_df['NC'] = 1
        patch_df['G3'] = 0
        patch_df['G4'] = 0
        patch_df['G4C'] = 0
        patch_df['G5'] = 0
        patch_df['unlabeled'] = 0
    else:
        patch_df['NC'] = 0
        patch_df['G3'] = 0
        patch_df['G4'] = 0
        patch_df['G4C'] = 0
        patch_df['G5'] = 0
        patch_df['unlabeled'] = 1
    return patch_df


def main(args):
    if args.wsi_list == 'all':
        wsi_list = glob.glob(str(args.image_dir) + "/*.jpg")
    else:
        file = open(args.wsi_list, 'r')
        wsi_list = file.readlines()
    print(' WSI list: ' )
    print(wsi_list)

    if args.number_wsi != 'all':
        random.seed(42)
        wsi_list = random.sample(wsi_list, int(args.number_wsi))

    number_of_wsi = len(wsi_list)
    image_dir = os.path.join(args.output_dir, 'images')
    print('number_of_wsi  ', number_of_wsi)
    wsi_df = pd.read_excel(args.wsi_dataframe)

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    df = init_patch_df(args.existing_patch_df)

    filtered_wsi = []
    for wsi_path in wsi_list:
        print('Slice WSI ' + wsi_path)
        wsi = cv2.imread(wsi_path)
        patch_df = slice_image(wsi, wsi_path, wsi_df, args.patch_resolution, image_dir, args.dataframes_only)

        if len(patch_df)==0:
            print('All patches of the WSI have been filtered out. WSI:' + str(wsi_path))
            filtered_wsi.append(wsi_path)

        df = pd.concat([df, patch_df])
    df.to_excel(os.path.join(args.output_dir,"Train.xlsx"), index=False)

    if len(filtered_wsi) > 0:
        print('The following WSI have been filtered out completely because of whiteness or blur:')
        print(filtered_wsi)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", "-i", type=str, default="/home/arne/datasets/SICAPv2_add_wsi/slides")
    parser.add_argument("--wsi_dataframe", "-wd", type=str, default="/home/arne/datasets/SICAPv2_add_wsi/wsi_labels.xlsx")
    parser.add_argument("--wsi_list", "-wl", type=str, default="all")
    parser.add_argument("--existing_patch_df", "-ep", type=str, default="None") #/home/arne/datasets/SICAPv2_add_unlabeled_patches/partition/Validation/Val1/Train.xlsx")

    parser.add_argument("--output_dir", "-o", type=str, default="./output/")
    parser.add_argument("--number_wsi", "-n", type=str, default="all")
    parser.add_argument("--dataframes_only", "-do", action='store_true')

    parser.add_argument("--patch_overlap", "-po", action='store_true')
    parser.add_argument("--patch_resolution", "-pr", type=int, default=512)
    parser.add_argument("--debug", "-d", action='store_true')
    args = parser.parse_args()
    print('Arguments:')
    print(args)
    main(args)