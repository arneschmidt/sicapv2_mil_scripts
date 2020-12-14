import argparse
import numpy as np
import pandas as pd
import os
from shutil import copy2

def main(args):
    old_df = pd.read_excel(args.old_wsi_df)
    new_df = pd.read_excel(args.new_wsi_df)
    in_dir = args.input_dataset_dir
    in_wsi_dir = os.path.join(in_dir,'slides')
    out_dir = args.output_dataset_dir
    out_wsi_dir = os.path.join(out_dir, 'slides')
    os.makedirs(out_wsi_dir, exist_ok=True)

    added_wsi = new_df[~new_df['slide_name'].isin(old_df['slide_id'])]
    added_wsi.rename(columns={"slide_name": "slide_id"}, inplace=True)
    added_wsi['patient_id'] = -1
    added_wsi['Gleason_primary'] = 0
    added_wsi['Gleason_secondary'] = 0
    added_wsi_filenames = added_wsi["slide_id"]
    added_wsi_filenames.to_csv(os.path.join(out_dir,"added_wsi.csv"), header=False, index=False)
    for wsi in added_wsi_filenames:
        for file in os.listdir(in_wsi_dir):
            if file.startswith(wsi + '_'):
                copy2(os.path.join(in_wsi_dir, file), os.path.join(out_wsi_dir, wsi + '.jpg')) # TODO: add suffix from source filename

    for row in range(len(added_wsi)):
        labels = []
        if added_wsi['G5'].iloc[row] == 1:
            labels.append(5)
        if added_wsi['G4'].iloc[row] == 1:
            labels.append(4)
        if added_wsi['G3'].iloc[row] == 1:
            labels.append(3)
        if len(labels) == 1:
            added_wsi['Gleason_primary'].iloc[row] = labels[0]
            added_wsi['Gleason_secondary'].iloc[row] = labels[0]
        if len(labels) == 2:
            added_wsi['Gleason_primary'].iloc[row] = labels[0]
            added_wsi['Gleason_secondary'].iloc[row] = labels[1]

    output_df = pd.concat([old_df, added_wsi], join='inner')
    output_df.to_excel(os.path.join(out_dir, "wsi_labels.xlsx"), index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--old_wsi_df", "-o", type=str, default="/home/arne/datasets/SICAPv2/wsi_labels.xlsx")
    parser.add_argument("--new_wsi_df", "-n", type=str, default="/home/arne/datasets/SICAP_MIL/dataframes/gt_global_slides.xlsx")
    parser.add_argument('--input_dataset_dir', '-in', default="/home/arne/datasets/SICAP_MIL")
    parser.add_argument('--output_dataset_dir', '-out', default="/home/arne/datasets/SICAPv2_add_wsi")
    args = parser.parse_args()
    main(args)