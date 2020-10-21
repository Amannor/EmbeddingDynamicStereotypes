import pickle
import os
import json

folder_name = "top_closest_words"

for filename in os.listdir(folder_name):
	if filename.endswith(".pkl"):
		full_path = os.path.join(folder_name, filename)
		d = pickle.load(open(full_path))
		full_path, pkl_ext = os.path.splitext(full_path)
		full_path = "{}.json".format(full_path)
		with open(full_path, 'w') as outfile:
			json.dump(d, outfile, indent=4)
