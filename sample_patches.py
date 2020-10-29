import pandas as pd
import numpy as np
filenames_path = 'filenames.txt'
filenames = pd.read_csv(filenames_path, header=None)
N = len(filenames)

sample_ids = np.random.randint(0, N, size=1000)

sample_filenames = filenames[0][sample_ids]
sample_filenames.to_csv("filenames_samples.txt", header=None, index=False)