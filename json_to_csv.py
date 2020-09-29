import pandas as pd
import os
import json

folder_name = "data_latest"

for filename in os.listdir(folder_name):
	if filename.endswith(".json"):
		full_path = os.path.join(folder_name, filename)
		df = pd.read_json (full_path)
		full_path, extension = os.path.splitext(full_path)
		full_path = "{}.csv".format(full_path)
		df.to_csv(full_path, index = None)



