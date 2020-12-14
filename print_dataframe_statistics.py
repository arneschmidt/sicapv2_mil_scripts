import argparse
import pandas
import numpy as np


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dataframe", "-i", type=str, default="../partition/")
    args = parser.parse_args()
    input_path = args.input_dataframe

    df = pandas.read_excel(input_path)
    df['wsi'] = df['image_name'].str.split('_').str[0]
    wsi_names = np.unique(np.array(df['wsi']))
    patient_ids = np.unique(df['image_name'].str[:10])
    print('wsi_names: ')
    print(wsi_names)
    print('patient_id: ')
    print(patient_ids)

    out_dict = {}

    out_dict['num_wsi'] = len(wsi_names)
    out_dict['num_patients'] = len(patient_ids)
    out_dict['num_nc'] =  np.sum(df['NC'] == 1)
    out_dict['num_g3'] = np.sum(df['G3'] == 1)
    out_dict['num_g4'] = np.sum(df['G4'] == 1)
    out_dict['num_g5'] = np.sum(df['G5'] == 1)
    num_unlabeled = 0
    if 'unlabeled' in df:
        num_unlabeled = np.sum(df['unlabeled'] == 1)
    out_dict['num_unlabeled'] = num_unlabeled

    for a,b in out_dict.items():
        print(a + ' : ' + str(b))




