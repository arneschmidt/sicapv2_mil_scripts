import os
import pandas as pd
filenames_path = 'filenames.txt'
input_split_dir = 'partition/'
output_split_dir = 'partition_MIL'
split_paths = ['Validation/Val1/',
               'Validation/Val2/',
               'Validation/Val3/',
               'Validation/Val4/',
               'Test/']

input_split_paths =  [input_split_dir + s for s in split_paths]
output_split_paths =  [output_split_dir + s for s in split_paths]

split_names = ['Train.xlsx', 'Test.xlsx']

filenames = pd.read_csv(filenames_path)

for split_path in input_split_paths:
    for split_name in split_names:
        dataframe = pd.read_excel(split_path + split_name)
        wsi_names = dataframe['image_name'].str.split('_').str[0]
        