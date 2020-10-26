import csv
import numpy as np
import sys
from cStringIO import StringIO
import copy
import datetime
import pickle
import os
import collections
import json

def cossim(v1, v2, signed = True):
    c = np.dot(v1, v2)/np.linalg.norm(v1)/np.linalg.norm(v2)
    if not signed:
        return abs(c)
    return c

def calc_distance_between_vectors(vec1, vec2, distype = 'norm'):
    if distype is 'norm':
        return np.linalg.norm(np.subtract(vec1, vec2))
    else:
        return cossim(vec1, vec2)

def calc_distance_between_words(vectors, word1, word2, distype = 'norm'):
        if word1 in vectors and word2 in vectors:
            if distype is 'norm':
                return np.linalg.norm(np.subtract(vectors[word1], vectors[word2]))
            else:
                return cossim(vectors[word1], vectors[word2])
        return np.nan
def calc_distance_over_time(vectors_over_time, word1, word2, distype = 'norm', vocabd = None, word1lims = [50, 1e25], word2lims = [50, 1e25]):
    ret = []
    for en,vectors in enumerate(vectors_over_time):
        if vocabd is None or vocabd[en] is None:
            ret.append(calc_distance_between_words(vectors, word1, word2, distype))
        elif (vocabd is not None and vocabd[en] is not None and (word1 in vocabd[en] and word2 in vocabd[en])):
            if (vocabd[en][word1] < word1lims[0] or vocabd[en][word2] < word2lims[0] or vocabd[en][word1] > word1lims[1] or vocabd[en][word2] > word2lims[1]):
                ret.append(np.nan)
            else:
                ret.append(calc_distance_between_words(vectors, word1, word2, distype))
        else:
            ret.append(calc_distance_between_words(vectors, word1, word2, distype))

    return ret

def calc_distance_over_time_averagevectorsfirst(vectors_over_time, words_to_average_1, words_to_average_2, distype = 'norm', vocabd = None, word1lims = [50, 1e25], word2lims = [50, 1e25]):
    retbothaveraged = []
    retfirstaveraged = []
    retsecondaveraged = []

    for en,vectors in enumerate(vectors_over_time):
        validwords1 = []
        validwords2 = []
        for word in words_to_average_1:
            if vocabd is not None and vocabd[en] is not None and word in vocabd[en] and word in vectors_over_time[en]:
                if vocabd[en][word] < word1lims[0] or vocabd[en][word] > word1lims[1]: continue
                validwords1.append(word)
            elif (vocabd is None or vocabd[en] is None) and word in vectors_over_time[en]:
                validwords1.append(word)


        for word in words_to_average_2:
            if vocabd is not None and vocabd[en] is not None and word in vocabd[en] and word in vectors_over_time[en]:
                if vocabd[en][word] < word2lims[0] or vocabd[en][word] > word2lims[1]: continue
                validwords2.append(word)
            elif (vocabd is None or vocabd[en] is None) and word in vectors_over_time[en]:
                validwords2.append(word)
        #if lengths of the valids are 0, distance is nan
        if len(validwords1) == 0 or len(validwords2) == 0:
            retbothaveraged.append(np.nan)
            retfirstaveraged.append(np.nan)
            retsecondaveraged.append(np.nan)
        else:
            average_vector_1 = np.mean(np.array([vectors[word] for word in validwords1]), axis = 0)
            average_vector_2 = np.mean(np.array([vectors[word] for word in validwords2]), axis = 0)

            retbothaveraged.append(calc_distance_between_vectors(average_vector_1,average_vector_2, distype))
            retfirstaveraged.append(np.mean([calc_distance_between_vectors(average_vector_1,vectors[word], distype) for word in validwords2]))
            retsecondaveraged.append(np.mean([calc_distance_between_vectors(vectors[word], average_vector_2, distype) for word in validwords1]))

    return retbothaveraged, retfirstaveraged, retsecondaveraged

def load_vectors(filename, words_set):
    print filename
    vectors = {}
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter = ' ')
        for row in reader:
            if words_set is None or len(words_set) ==0 or row[0] in words_set:
                vectors[row[0]] = [float(x) for x in row[1:] if len(x) >0]
    return vectors

def load_vectors_over_time(filenames, words_set):
    vectors_over_time = []
    for f in filenames:
        vectors_over_time.append(load_vectors(f, words_set))
    return vectors_over_time

def single_set_distances_to_single_set(vectors_mult, targetset, otherset, vocabd, word1lims = [50, 1e25], word2lims = [50, 1e25]):
    '''
    returns average distances of targetset to single set over the vectors_mult

    also returns averages done in different way -- average targetset vectors before distance to each, average
        otherset before each, AND average both and return a single value
    '''
    toset = [[] for _ in range(len(vectors_mult))]
    toset_cossim = [[] for _ in range(len(vectors_mult))]

    toset_averageothersetfirst = [[] for _ in range(len(vectors_mult))]
    toset_cossim_averageothersetfirst = [[] for _ in range(len(vectors_mult))]

    toset_averagetargetsetfirst = [[] for _ in range(len(vectors_mult))]
    toset_cossim_averagetargetsetfirst = [[] for _ in range(len(vectors_mult))]

    for word in targetset:
        for word2 in otherset:
            dists = calc_distance_over_time(vectors_mult, word, word2, vocabd = vocabd, word1lims = word1lims, word2lims = word2lims)
            dists_cossim = calc_distance_over_time(vectors_mult, word, word2, distype = 'cossim', vocabd = vocabd, word1lims = word1lims, word2lims = word2lims)
            # print(dists)
            for en,d in enumerate(dists):
                if not np.isnan(d):
                    toset[en].append(d)
                    toset_cossim[en].append(dists_cossim[en])
    # print [len(d) for d in toset]

    toset = [np.mean(d) for d in toset]
    toset_cossim = [np.mean(d) for d in toset_cossim]

    averageboth, averagefirst, averagesecond = calc_distance_over_time_averagevectorsfirst(vectors_mult, targetset, otherset, distype = 'norm', vocabd = vocabd, word1lims = word1lims, word2lims = word2lims)

    averageboth_cossim, averagefirst_cossim, averagesecond_cossim = calc_distance_over_time_averagevectorsfirst(vectors_mult, targetset, otherset, distype = 'cossim', vocabd = vocabd, word1lims = word1lims, word2lims = word2lims)

    return [toset, toset_cossim, averageboth, averagefirst, averagesecond, averageboth_cossim, averagefirst_cossim, averagesecond_cossim]

def set_distances_to_set(vectors_mult, targetset, set0, set1, vocabd, word1lims = [50, 1e25], word2lims = [50, 1e25]):
    '''
    returns average distances of targetset to each of set0 and set1 over the vectors_mult
    '''
    toset0 = [[] for _ in range(len(vectors_mult))]
    toset1 = [[] for _ in range(len(vectors_mult))]
    toset0_cossim = [[] for _ in range(len(vectors_mult))]
    toset1_cossim = [[] for _ in range(len(vectors_mult))]
    for word in targetset:
        for word2 in set0:
            dists = calc_distance_over_time(vectors_mult, word, word2, vocabd= vocabd, word1lims = word1lims, word2lims = word2lims )
            dists_cossim = calc_distance_over_time(vectors_mult, word, word2, distype = 'cossim', vocabd = vocabd, word1lims = word1lims, word2lims = word2lims )
            # print(dists)
            for en,d in enumerate(dists):
                if not np.isnan(d):
                    toset0[en].append(d)
                    toset0_cossim[en].append(dists_cossim[en])

        for word2 in set1:
            dists = calc_distance_over_time(vectors_mult, word, word2,vocabd= vocabd , word1lims = word1lims, word2lims = word2lims)
            dists_cossim = calc_distance_over_time(vectors_mult, word, word2, distype = 'cossim', vocabd= vocabd, word1lims = word1lims, word2lims = word2lims )
            # print(dists)
            for en,d in enumerate(dists):
                if not np.isnan(d):
                    toset1[en].append(d)
                    toset1_cossim[en].append(dists_cossim[en])
    toset0 = [np.mean(d) for d in toset0]
    toset1 = [np.mean(d) for d in toset1]
    toset0_cossim = [np.mean(d) for d in toset0_cossim]
    toset1_cossim = [np.mean(d) for d in toset1_cossim]
    return [toset0, toset0_cossim], [toset1, toset1_cossim]

def load_vocab(fi, words_set=None):
    try:
        res = dict()
        with open(fi, 'r') as f:
            reader = csv.reader(f, delimiter = ' ')
            for d in reader:
                if words_set is None or len(words_set) == 0 or d[0] in words_set:
                    res[d[0]] = float(d[1])
        return res
    except:
        return None

def get_counts_dictionary(vocabd, neutwords):
    dwords = {}
    if vocabd is None or len(vocabd) == 0: return {}
    for en in range(len(vocabd)):
        if vocabd[en] is None: return {}
    for word in neutwords:
        dwords[word] = [vocabd[en].get(word, 0) for en in range(len(vocabd))]
    return dwords

def get_vector_variance(vectors_over_time, words, vocabd = None, word1lims = [50, 1e25], word2lims = [50, 1e25]):

    variances = []
    for en,vectors in enumerate(vectors_over_time):
        validwords = []
        for word in words:
            if vocabd is not None and vocabd[en] is not None and word in vocabd[en] and word in vectors_over_time[en]:
                if vocabd[en][word] < word1lims[0] or vocabd[en][word] > word1lims[1]: continue
                validwords.append(word)
            elif (vocabd is None or vocabd[en] is None) and word in vectors_over_time[en]:
                validwords.append(word)

        #if lengths of the valids are 0, variances are nan
        if len(validwords) == 0:
            variances.append(np.nan)
        else:
            avgvar = np.mean(np.var(np.array([vectors[word] for word in validwords]), axis = 0))
            variances.append(avgvar)

    return variances

def get_top_closest_words(vectors_over_time, vocabd, max_size = 50, target_words = ['anxiety', 'depression', 'schizophrenia', 'schizophrenic', 'dementia', 'demented', 'psychosis', 'psychotic'], convert_to_str=True):
    '''
    :param vectors_over_time:
    :param vocabd:
    :param max_size:
    :param target_words:
    :return:
    target_words_to_closest_words which is a dictionary. The keys are each of 'target_words' plus an additional key that's all the words in 'target_words_to_closest_words' combined.
        Each list is the size of len(vocabd) (which should be identical to len(vectors_over_time).
            Each member of that list is an ordered dictionary (of max_size). Each key is a 2-tuple; The first member is the Euclidean distance, the second member is the soine similarity.
                Each value of that dict is a set of words that are in have that distance and cosine similarity to the target_word in this specific time period
    '''
    target_words_to_closest_words = dict()
    target_words_to_closest_words['entire_mental_words'] = [[] for _ in range(len(vocabd))]
    for t_word in target_words:
        target_words_to_closest_words[t_word] = [[] for _ in range(len(vocabd))]

    for i in range(len(vocabd)):
        dt_string = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print("Analyzing time period no. {} at: {}".format(i, dt_string))
        target_words_to_closest_words['entire_mental_words'][i] = collections.OrderedDict()
        for target_word in target_words:
            target_words_to_closest_words[target_word][i] = collections.OrderedDict()
        j=1
        for vocab_word in vocabd[i]:
            if(j%10000 == 0 or j == len(vocabd[i])):
                print("Word {} out of {}".format(j, len(vocabd[i])))
            j=j+1
            if not (vocab_word in target_words):
                distances = single_set_distances_to_single_set([vectors_over_time[i]], [vocab_word], target_words, vocabd)
                if not (np.isnan(distances[0][0]) or np.isnan(distances[1][0])):
                    euclidean_and_cosim = distances[0][0], distances[1][0]
                    if euclidean_and_cosim not in target_words_to_closest_words['entire_mental_words'][i]:
                        target_words_to_closest_words['entire_mental_words'][i][euclidean_and_cosim] = set()
                    target_words_to_closest_words['entire_mental_words'][i][euclidean_and_cosim].add(vocab_word)
                    target_words_to_closest_words['entire_mental_words'][i] = collections.OrderedDict(sorted(target_words_to_closest_words['entire_mental_words'][i].items(), key=lambda t: t[0]))
                    while len(target_words_to_closest_words['entire_mental_words'][i]) > max_size:
                        key_to_pop = target_words_to_closest_words['entire_mental_words'][i].keys()[len(target_words_to_closest_words['entire_mental_words'][i]) - 1]
                        target_words_to_closest_words['entire_mental_words'][i].pop(key_to_pop)

            for target_word in target_words:
                if target_word.lower() == vocab_word.lower():
                    continue
                distances = single_set_distances_to_single_set([vectors_over_time[i]], [vocab_word], [target_word], vocabd)
                if np.isnan(distances[0][0]) or np.isnan(distances[1][0]):
                    continue
                euclidean_and_cosim = distances[0][0], distances[1][0]
                if euclidean_and_cosim not in target_words_to_closest_words[target_word][i]:
                    target_words_to_closest_words[target_word][i][euclidean_and_cosim]= set()
                target_words_to_closest_words[target_word][i][euclidean_and_cosim].add(vocab_word)
                target_words_to_closest_words[target_word][i] = collections.OrderedDict(sorted(target_words_to_closest_words[target_word][i].items(), key=lambda t: t[0]))
                while len(target_words_to_closest_words[target_word][i]) > max_size:
                    key_to_pop = target_words_to_closest_words[target_word][i].keys()[len(target_words_to_closest_words[target_word][i]) - 1]
                    target_words_to_closest_words[target_word][i].pop(key_to_pop)

    if(convert_to_str):
        for t_word in target_words_to_closest_words.keys():
            for i in range(len(target_words_to_closest_words[t_word])):
                dict_items = target_words_to_closest_words[t_word][i].items()
                target_words_to_closest_words[t_word][i] = collections.OrderedDict()
                for key, value in sorted(dict_items):
                    target_words_to_closest_words[t_word][i][(str(key))] = ', '.join(value)

                # target_words_to_closest_words[t_word][i] = {str(key): str(value) for key, value in sorted(dict_items)}




    # This is by calling directly calc_distance_between_words()
    # for target_word in target_words:
    #     target_words_to_closest_words[target_word] = []
    #     for i in range(len(vocabd)):
    #         distance_to_vocab_word = collections.OrderedDict()
    #         for vocab_word in vocabd[i]:
    #             cur_distance = calc_distance_between_words(vectors_over_time[i], target_word, vocab_word)
    #             if cur_distance not in distance_to_vocab_word:
    #                 distance_to_vocab_word[cur_distance] = set()
    #             distance_to_vocab_word[cur_distance].add(vocab_word)
    #             while len(distance_to_vocab_word) >= max_size:
    #                 distance_to_vocab_word.pop(distance_to_vocab_word.keys()[len(distance_to_vocab_word)-1])
    #         target_words_to_closest_words[target_word].append(distance_to_vocab_word)
    # #Todo: Add another one per vectors set that checks the distnace between the *set of words* target_words to each one in vocabd
    return target_words_to_closest_words








def main(filenames, label, csvname = None, neutral_lists = [], group_lists = ['male_pairs', 'female_pairs'], do_individual_group_words = False, do_individual_neutral_words = False, do_cross_individual = False):

    dt_string = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print("label {} started {}".format(label, dt_string))

    cur_words_set = set()
    # for grouplist in group_lists:
    #     with open('data/' + grouplist + '.txt', 'r') as f2:
    #         groupwords = [x.strip() for x in list(f2)]
    #         cur_words_set = cur_words_set.union(groupwords)
    #
    # for neut in neutral_lists:
    #     with open('data/'+neut + '.txt', 'r') as f:
    #         neutwords = [x.strip() for x in list(f)]
    #         cur_words_set = cur_words_set.union(neutwords)

    vocabs = [fi.replace('vectors/normalized_clean/vectors', 'vectors/normalized_clean/vocab/vocab') for fi in filenames]
    vocabd = [load_vocab(fi, cur_words_set) for fi in vocabs]

    d = {}
    vectors_over_time = load_vectors_over_time(filenames, cur_words_set)
    print('vocab size: ' + str([len(v.keys()) for v in vectors_over_time]))
    d['counts_all'] = {}
    d['variance_over_time'] = {}

    top_closest_words = get_top_closest_words(vectors_over_time, vocabd)

    data_folder ="top_closest_words"
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    full_path = os.path.join(data_folder, "top_closest_words_{}.json".format(label))
    with open(full_path, "w") as outfile:
        json.dump(top_closest_words, outfile, indent=4)
    # full_path = os.path.join(data_folder, "top_closest_words_{}.pkl".format(label))
    # with open(full_path, 'w') as out_file:
    #     pickle.dump(top_closest_words, out_file)

    #
    # for grouplist in group_lists:
    #     with open('data/'+grouplist + '.txt', 'r') as f2:
    #         groupwords = [x.strip() for x in list(f2)]
    #         d['counts_all'][grouplist] = get_counts_dictionary(vocabd, groupwords)
    #         d['variance_over_time'][grouplist] = get_vector_variance(vectors_over_time, groupwords)
    #
    # for neuten, neut in enumerate(neutral_lists):
    #     with open('data/'+neut + '.txt', 'r') as f:
    #         neutwords = [x.strip() for x in list(f)]
    #
    #         d['counts_all'][neut] = get_counts_dictionary(vocabd, neutwords)
    #         d['variance_over_time'][neut] = get_vector_variance(vectors_over_time, neutwords)
    #
    #         dloc_neutral = {}
    #
    #         for grouplist in group_lists:
    #             with open('data/'+grouplist + '.txt', 'r') as f2:
    #                 print neut, grouplist
    #                 groupwords = [x.strip() for x in list(f2)]
    #                 distances = single_set_distances_to_single_set(vectors_over_time, neutwords, groupwords, vocabd)
    #
    #                 d[neut+'_'+grouplist] = distances
    #
    #                 if do_individual_neutral_words:
    #                     for word in neutwords:
    #                         dloc_neutral[word] = dloc_neutral.get(word, {})
    #                         dloc_neutral[word][grouplist] = single_set_distances_to_single_set(vectors_over_time, [word], groupwords, vocabd)
    #                 if do_individual_group_words:
    #                     d_group_so_far = d.get('indiv_distances_group_'+grouplist, {})
    #                     for word in groupwords:
    #                         d_group_so_far[word] = d_group_so_far.get(word, {})
    #                         d_group_so_far[word][neut] = single_set_distances_to_single_set(vectors_over_time, neutwords,[word], vocabd)
    #                     d['indiv_distances_group_'+grouplist] = d_group_so_far
    #
    #                 if do_cross_individual:
    #                     d_cross = {}
    #                     for word in groupwords:
    #                         d_cross[word] = {}
    #                         for neutword in neutwords:
    #                             d_cross[word][neutword] = single_set_distances_to_single_set(vectors_over_time, [neutword],[word], vocabd)
    #                     d['indiv_distances_cross_'+grouplist+'_'+neut] = d_cross
    #
    #
    #         d['indiv_distances_neutral_'+neut] = dloc_neutral
    #
    #
    # data_folder ="data_latest"
    # if not os.path.exists(data_folder):
    #     os.makedirs(data_folder)
    # full_path = os.path.join(data_folder, "data_mental_{}.pkl".format(label))
    # with open(full_path, 'w') as out_file:
    #     pickle.dump(d, out_file)

    del cur_words_set
    del vocabd
    del vectors_over_time

    # with open('run_results/'+csvname, 'ab') as cf:
    #     headerorder = ['datetime', 'label']
    #     headerorder.extend(sorted(list(d.keys())))
    #     print headerorder
    #     d['label'] = label
    #     d['datetime'] = datetime.datetime.now()
    #
    #     csvwriter = csv.DictWriter(cf, fieldnames = headerorder)
    #     csvwriter.writeheader()
    #     csvwriter.writerow(d)
    #     cf.flush()

    dt_string = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print("label {} finished {}".format(label, dt_string))

csv.field_size_limit(int(sys.maxsize/(10**10)))

folder = '../vectors/normalized_clean/'

filenames_nyt = [folder + 'vectorsnyt{}-{}.txt'.format(x, x+3) for x in range(1987, 2005, 1)]
filenames_sgns = [folder + 'vectors_sgns{}.txt'.format(x) for x in range(1910, 2000, 10)] #Todo: need to create vocab files for 1810-1900, 2000
filenames_svd = [folder + 'vectors_svd{}.txt'.format(x) for x in range(1910, 2000, 10)] #Todo: need to create vocab files for 1810-1900, 2000
# filenames_google = [folder + 'vectorsGoogleNews_exactclean.txt']
# filenames_wikipedia = [folder + 'vectorswikipedia.txt']
# filenames_commoncrawl = [folder + 'vectorscommoncrawlglove.txt']

# filename_map = {'nyt' : filenames_nyt, 'sgns' : filenames_sgns, 'svd': filenames_svd, 'google':filenames_google, 'wikipedia':filenames_wikipedia, 'commoncrawlglove':filenames_commoncrawl}
# filename_map = {'nyt' : filenames_nyt, 'sgns' : filenames_sgns, 'svd': filenames_svd}
filename_map = {'sgns' : filenames_sgns, 'svd': filenames_svd}

if __name__ == "__main__":
    param_filename = 'run_params.csv'

    with open(param_filename,'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row['label']
            neutral_lists = eval(row['neutral_lists'])
            group_lists = eval(row['group_lists'])
            do_individual_neutral_words = (row['do_individual_neutral_words'] == "TRUE")
            do_individual_group_words = (row.get('do_individual_neutral_words', '') == "TRUE")

            main(filename_map[label], label = label, csvname = row['csvname'], neutral_lists = neutral_lists, group_lists = group_lists, do_individual_neutral_words = do_individual_neutral_words, do_individual_group_words = do_individual_group_words)
