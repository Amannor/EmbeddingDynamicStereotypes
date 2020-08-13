import numpy as np
import os
import csv
import re
import ntpath
import sys
import traceback

def load_vectors(filename):
	vectors = {}
	with open(filename, 'r') as f:
		reader = csv.reader(f, delimiter = ' ')
		for row in reader:
			word = re.sub('[^a-z]+', '', row[0].strip().lower())
			if len(word) < 2: continue
			vectors[word] = [float(x) for x in row[1:] if len(x) >0]
	return vectors

def find_vector_norms(vectors):
	norms = [np.linalg.norm(vectors[word]) for word in vectors]
	return np.mean(norms), np.var(norms), np.median(norms)


def print_sizes(folder = '../vectors/normalized_clean/'):
	filenames_sgns = [folder + 'vectors_sgns{}.txt'.format(x) for x in range(1910, 2000, 10)]
	filenames_svd = [folder + 'vectors_svd{}.txt'.format(x) for x in range(1910, 2000, 10)]
	filenames_nyt = [folder + 'vectors{}-{}.txt'.format(x, x+5) for x in range(1987, 2000, 1)]
	filenames_coha = [folder + 'vectorscoha{}-{}.txt'.format(x, x+20) for x in range(1910, 2000, 10)]

	filenames_combined = [filenames_nyt, filenames_sgns, filenames_svd, [folder + 'vectorswikipedia.txt'], [folder + 'vectorsGoogleNews_exactclean.txt']]

	for names in filenames_combined:
		for name in names:
			print (name, find_vector_norms(load_vectors(name)))

def normalize(filename, filename_output):
	vectors = {}
	countnorm0 = 0
	countnormal = 0
	skipped_too_short_count = 0
	skipped_norm_too_small_count = 0
	with open(filename_output, 'w') as fo:
		writer = csv.writer(fo, delimiter = ' ')
		with open(filename, 'r', encoding="utf-8") as f:
			reader = csv.reader(f, delimiter = ' ')
			for row in reader:
				rowout = row
				word = re.sub('[^a-z]+', '', row[0].strip().lower())
				rowout[0] = word
				if len(word) < 2:
					skipped_too_short_count = skipped_too_short_count+1
					continue
				# print(word)
				norm = np.linalg.norm([float(x) for x in row[1:] if len(x) >0])
				if norm < 1e-2:
					countnorm0+=1
					skipped_norm_too_small_count = skipped_norm_too_small_count+1
				else:
					countnormal+=1
					for en in range(1, len(rowout)):
						if len(rowout[en])>0:
							rowout[en] = float(rowout[en])/norm
					writer.writerow(rowout)
		fo.flush()
	print (f"skipped_too_short_count {skipped_too_short_count} skipped_norm_too_small_count {skipped_norm_too_small_count}")

def normalize_vectors():
	csv.field_size_limit(int(sys.maxsize/(10**10)))
	# folder = '../../vectors/ldc95/'
	folder = '../vectors/'
	# filenames_ldc95 = [folder + 'vectorsldc95_{}.txt'.format(x) for x in ['NYT', 'LATWP', 'REUFF', 'REUTE', 'WSJ']]
	filenames = [os.path.join(folder, x) for x in os.listdir(folder)]
	filenames = list(filter(lambda fname: fname.endswith(".txt"), filenames))
	for name in filenames:
		# filename_output = name.replace('ldc95/','normalized_clean/')
		filename_output = os.path.join(os.path.dirname(name),f'{ntpath.basename(name)}.normalized_clean')
		print (name,filename_output)
		try:
			normalize(name, filename_output)
		except Exception as e:
			print(f"Exception: {e}")
			print(traceback.format_exc()) #or print(sys.exc_info()[2])
		

if __name__ == "__main__":
	normalize_vectors()
