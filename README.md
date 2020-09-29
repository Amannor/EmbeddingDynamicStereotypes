This repository contains code and data associated with [The final report in the course Advanced Machine Learning (IDC, september 2020).](https://github.com/Amannor/EmbeddingDynamicStereotypes/blob/final-proj-temporal-social-stigmas/temporal_changes_in_social_stigmas.pdf) 

This work builds on the work described in the article [Word embeddings quantify 100 years of gender and ethnic stereotypes.](http://gargnikhil.com/files/pdfs/GSJZ18_embedstereotypes.pdf) and it is stringly advised that you familirize yourself with their work beforehand. The master branch of this repo is their latest code & data (as  of September 2020).

Environment and setup:

This code was run on Python 2.7. Please see the file requirements2.txt for a detailed list of the packages used (it's the output of pip freeze). This was run on an Anaconda environmenet created for Python 2.7


To re-run all analyses and plots:

1. Download vectors from online sources (links in paper and below).
   Those should be downloaded to a sister directory of the folder to which this repo eas cloned.
   The vectors (nyt \ svd \ sgns) should be downloaded to vectors/normalized_clean
   The vocab file should be downloaded to vectors/normalized_clean/vocab
2. Set up parameters to run as in run_params.csv (already filled with params for the mental vs. physical stigmas mentioned in the report)
3. Run changes_over_time.py
4. Run pickle_to_json.py
5. The results described in the report from each one of the temporal data sets (nyt, svd, sgns). In each respective file, that data was taken from "mental_stigmas_words_mental" and "mental_stigmas_words_physical". The first two vectors represent the average Euclidean distnace and the average cosine similarity between the two relevent sets, respectively. 

dataset_utilities/ contains various helper scripts to preprocess files and create word vectors. From a corpus, for example LDC95T21-North-American-News, that contains many text files (each containing an article) from a given year, first run create_yrly_datasets.py to create a single text file per year (with only valid words). Then, run pipeline.py on each of these files to create vectors, potentially combining multiple years into a single training set. normalize_vectors.py contains utilities to standardize the vectors.

data_latest/sample_data/ contains the data (json and excel) used for this report


data_latest/orig/ contains the original unprocessed data files for this report

I used the following embeddings publicly available online. If you use these embeddings, please cite the associated papers.


1. [Embeddings from the New York Times Annotated Corpus for every year between 1987 and 2004](https://drive.google.com/file/d/1JNy19NfBwNj5JWj71UipA-zrFVIsYp1p/view?usp=sharing)
2. [Genre-Balanced American English (1900s-2000s), SVD](https://drive.google.com/file/d/1YajeJU2tQOG6GEgX_HXe8uOBveFxDjcc/view?usp=sharing)
3. [Genre-Balanced American English (1810s-2000s), SGNS](https://drive.google.com/file/d/1HdSxw_un9en7G14Kkm38d2ko0uSrSL0A/view?usp=sharing)
4. [The vocabulary file, containing all the vocabulary word counts per vector set](https://drive.google.com/file/d/1nK9u3v6ln_6ObEJmRxWRkEUS2xHSDmgl/view?usp=sharing)


Note: NYT, SVD and SGNS links are to the already normalized ready-to-use vectors set. I normalized using the orignal authors code. You can download the original and normalize yourself (see README in the master branch of this repo for details)




