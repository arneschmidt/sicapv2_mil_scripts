import os
import argparse
import pandas as pd


def delete_patch_from_filenames(patch_name, all_filenames_copy):
    # drop this patch from all
    for j in range(len(all_filenames_copy)):
        if all_filenames_copy[j] == patch_name:
            all_filenames_copy.drop(index=j)
            break
        if j == len(all_filenames_copy):
            raise Exception("Patch name not found in images: ", patch_name)

def check_duplicates(dataframe):
    for i in range(len(dataframe['image_name'])):
        if i == len(dataframe['image_name'])-1:
            break
        if dataframe['image_name'][i] == dataframe['image_name'][i+1]:
            raise Exception('Oh no! There is a duplicate path: ' + dataframe['image_name'][i])

def add_filenames_to_dataframe(dataframe, all_filenames):
    all_filenames_copy = all_filenames.copy()[0] # copy because later we delete entries
    dataframe.sort_values(by='image_name')
    wsi_names = dataframe['image_name'].str.split('_').str[0]
    dataframe['unlabeled'] = 0
    num_wsi = 0
    original_dataframe_length = len(dataframe['image_name'])
    for i in range(original_dataframe_length):
        patch_name =  dataframe['image_name'][i]
        wsi_name = wsi_names[i]

        delete_patch_from_filenames(patch_name, all_filenames_copy)

        # avoid out of range error
        next_wsi_name = ('last_wsi' if i == original_dataframe_length-1 else wsi_names[i+1])
        # going through all patches in dataframe, add the ones that are additional in all_filenames
        if wsi_name != next_wsi_name:
            num_wsi = num_wsi+1
            for j in range(len(all_filenames_copy)):
                if all_filenames_copy[j].split('_')[0] == wsi_name:
                    dataframe = dataframe.append({'image_name': all_filenames_copy[j],
                                      'NC':0, 'G3':0, 'G4':0, 'G5':0, 'unlabeled':1}, ignore_index=True)
    print('Number of WSIs: ' + str(num_wsi))
    dataframe.sort_values(by='image_name')
    check_duplicates(dataframe)

    return dataframe


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", "-i", type=str, default="../partition/")
    parser.add_argument("--output_dir", "-o", type=str, default="../partition_mil/")
    parser.add_argument("--filenames_path", "-f", type=str, default="filenames.txt")
    args = parser.parse_args()

    filenames_path = args.filenames_path
    input_dir = args.input_dir
    output_dir = args.output_dir
    split_paths = ['Validation/Val1/',
                   'Validation/Val2/',
                   'Validation/Val3/',
                   'Validation/Val4/',
                   'Test/']

    input_split_paths =  [input_dir + s for s in split_paths]

    split_names = ['Train.xlsx', 'Test.xlsx']

    all_filenames = pd.read_csv(filenames_path, header=None)

    for split_path in input_split_paths:
        for split_name in split_names:
            print('Working on file: ', split_path+split_name)
            dataframe = pd.read_excel(split_path + split_name)
            no_images_before = len(dataframe['image_name'])
            completed_dataframe = add_filenames_to_dataframe(dataframe, all_filenames)
            no_images_after = len(completed_dataframe['image_name'])
            print('Added total number of unlabeled images: ' + str(no_images_after - no_images_before))
            output_split_dir = output_dir + split_path
            os.makedirs(output_split_dir, exist_ok=True)
            completed_dataframe.to_csv(output_split_dir + split_name, index=False)

