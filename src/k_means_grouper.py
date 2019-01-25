'''
@summary: To remove keywords that are similar.
This is to bring more diversity to the top ranked keywords.
I used an algorithm called K-means for grouping.
This algorithm is implemented and have not used third party library 
other than numpy (for computation) and gensim (loading of data set)
Each word in the keyword list is converted to a vector using word2vec.
I use GoogleNews pre-trained dataset to get vector of word.
Then, I divide the n keywords into k clusters.
Initially, I randomly choose k centroids.
The euclidian distance of each vector is calculated from the centroid.
Each cluster is formed with a centroid and vectors which are closest to it.
Once cluster is formed, a new centroid is found for each cluster.
Based on the distance, new clusters are formed.
This process is continued until, the list of centroid stop changing. 
This is the final list of clusters.
Only one keyword from each cluster will be taken as final keyword.
@author: Srivatsan Ananthakrishnan
'''
from math import sqrt
import random
from gensim import models
from gensim.models.keyedvectors import KeyedVectors
from numpy import float32
import numpy as np
    

def get_clusters(ranked_words):
    """Group the words to K clusters based on similarity between the words (word2vec)"""
    if(len(ranked_words) < 15):
        #Cannot group too small data set, return as it is
        return ranked_words, [];
    #Reference https://stackoverflow.com/questions/42094180/spacy-how-to-load-google-news-word2vec-vectors
    #Loading pre-trained smaller dataset of GoogleNews
    try:
        model = KeyedVectors.load('GoogleNews-vectors-gensim-normed.bin', mmap='r')
    except:
        raise ValueError("Please refer README for data set configuration!");
    #Word and vector mapping 
    word2vec_dict = {}#Key is the word and value is the vector
    #List of words which don't have a vector representation in data set
    no_vector_words = [];
    #list of vectors
    X = [];
    #For each word
    for rw in ranked_words:
        #If the word has a vector representation in the data set
        if rw.getword() in model.wv.vocab:
            word2vec_dict[rw.getword()] = model.wv[rw.getword()]
            X.append(word2vec_dict[rw.getword()].T);
        else:
            no_vector_words.append(rw);
    
    #Reference: https://learn.scientificprogramming.io/python-k-means-data-clustering-and-finding-of-the-best-k-485f66297c06
    #pick K random points as cluster,
    #To computer best K, I try K as 1 to 10 and find the best K
    sum_distance_arr = [];
    for k in range(1, 10):
        #Randomly find K centroid vectors
        centroid_list = random.sample(X, k);
        final_centroid_map = get_centroid(centroid_list, X);
        sum_distance = 0;
        for centroid_key in final_centroid_map.keys():
            for data_value in final_centroid_map[centroid_key]:
                #Sum of the euclidian distance between each vector and cluster
                #is calculated and kept in an array
               sum_distance += euclidian_distance(centroid_key, data_value)
        sum_distance_arr.append(sum_distance);
        if(sum_distance == 0):
            break;
    k = 1;#By default, if any break happens in the previous loop
    if len(sum_distance_arr) > 1:
        #I am comparing the change between each sum and the minimum changed step is taken as K
        list_val = [abs(t - s) for s, t in zip(sum_distance_arr, sum_distance_arr[1:])];
        k = list_val.index(min(list_val))+1;
    #Now I got k, I have to get cluster based on it.
    centroid_list = random.sample(X, k);
    final_centroid_map = get_centroid(centroid_list, X);
    dt=np.dtype('float32')
    counter = 0;
    data_cluster_list = [];
    #Converting cluster vectors to cluster words
    for word_vec in final_centroid_map.keys():
        counter += 1;
        #Getting corresponding word from data set based on the vector.
        centroid_word, centroid_vector = model.most_similar(positive=[np.array(tuple(word_vec),dtype=dt)], topn=1)[0];
        data_clusters = [];
        for val_vec in final_centroid_map[word_vec]:
            data_word, data_vector = model.most_similar(positive=[np.array(tuple(val_vec),dtype=dt)], topn=1)[0];
            data_clusters.append(get_ranked_word(ranked_words, data_word));
        data_cluster_list.append(data_clusters);
    #Returning those keywords which did not have vectors
    #and data clusters (so that highly ranked word from each cluster would be taken later)
    return no_vector_words, data_cluster_list;


def get_ranked_word(ranked_word_list, word):
    """Get RankedWord object containing the given word"""
    for rw in ranked_word_list:
        if word == rw.getword():
            return rw;
        
def euclidian_distance(vector1, vector2):
    """Find euclidian distance between two vectors"""
    #Reference: http://www.codehamster.com/2015/03/09/different-ways-to-calculate-the-euclidean-distance-in-python/
    distance_square = 0;
    if len(vector1) == len(vector2):
        zip_vector = zip(vector1, vector2);
        for member in zip_vector:
            distance_square += (member[1] - member[0]) ** 2;
    euclidean_distance = sqrt(distance_square);    
    return euclidean_distance;
   
def find_closest_centroid(centroid_vector_distance_map):
    """Find the centroid vector which is closest to a vector"""
    shortest_dist = 0;
    closest_centroid = 0;
    count = 0;
    #For all centroids
    for centroid_key in centroid_vector_distance_map.keys():
        #if first time or if current shortest distance greater than current distance from the map 
        if (count == 0) or (shortest_dist > centroid_vector_distance_map[centroid_key]):
            shortest_dist = centroid_vector_distance_map[centroid_key];
            closest_centroid = centroid_key;
        count += 1;
    return closest_centroid;


def rearrange_cluster(centroid_map, word_vectors):
    """Rearrange the clusters based on the closest centroid to each vector"""
    centroid_vector_distance_map = {k:0 for k in centroid_map.keys()};
    #For each vector, getting the closest centroid and hence rearranging the cluster.
    for word_vector in word_vectors:
        for centroid in centroid_map.keys():
            #calculate distance of current vec from each centroid
            distance = euclidian_distance(centroid, word_vector);
            centroid_vector_distance_map[centroid] = distance;
            #shorted distance
        closest_centroid = find_closest_centroid(centroid_vector_distance_map);
        centroid_map[closest_centroid].append(word_vector);
    return centroid_map;


def get_centroid(centroid_list, X): 
    """Get centroids recursively until no more changes are needed"""
    #I use Euclidean distance here
    #This is a map of centroid and list of vectors
    #key is current centroid and list of vectors is the values
    # in that cluster belonging to centroid
    #converting to tuple because key cannot be an array
    centroid_map = {tuple(k):[] for k in centroid_list};
    #Find average of each cluster and assign it as new centroid
    old_centroid_list = centroid_list;
    centroid_map = rearrange_cluster(centroid_map, X);
    centroid_list = [np.mean(arr, axis=0, dtype=float32) for arr in centroid_map.values()]
    if (np.array_equal(old_centroid_list, centroid_list)): 
        return centroid_map;
    #Calling it recursively, until there is no more change between old 
    #centroid list and new centroid list
    return get_centroid(centroid_list, X);
        
        
if __name__ == '__main__':
    print("This file can only be imported!")
