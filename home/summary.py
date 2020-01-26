#For getting vectors from bert
from bert_serving.client import BertClient

#for clustering
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances as cdist
import numpy as np

def get_sentences(tracks,
                  num_words):
    words = " ".join(tracks).split(" ")
    new_words = []
    result = []
    while True:
        # store the word
        new_words.append(words[0])

        if len(new_words) > num_words:
            # abort the insert(remove the last element)
            new_words.pop(-1)
            # Then store it in the result
            result.append(new_words)
            # deallocate, create a new one
            new_words = []
        else:
            # else, pop what you've appended
            words.pop(0)
            # now, if the words have run out, break it
            if len(words) < 1:
                # store the current new words
                result.append(new_words)
                # and break
                break

    # wrap up the words
    for j in range(len(result)):
        result[j] = " ".join(result[j])

    return result

def pre_process(tracks,
                max_length,
                stride):
    # initialse an empty bucket
    processed = []
    words = " ".join(tracks).split(" ")
    new_words = []
    result = []
    while True:
        # fill words into the bucket
        new_words.append(words[0])
        if len(" ".join(new_words)) > max_length:
            # abort the insert(remove the last element)
            new_words.pop(-1)
            # Then store it in the result
            result.append(new_words)
            # deallocate, create a new one
            new_words = new_words[len(new_words) - stride:]

        else:
            # else, pop what you've appended
            words.pop(0)
            # now, if the words have run out, break it
            if len(words) < 1:
                # now store the new words
                result.append(new_words)
                # and break the outer loop
                break

    # wrap up the words
    for j in range(len(result)):
        result[j] = " ".join(result[j])

        # store it in the processed
    for sentence in result:
        processed.append(sentence.strip())

    return processed


def get_embeddings(processed):
    bc = BertClient()
    vectors = bc.encode(processed)

    return vectors


def make_clusters(processed,
                  vectors,
                  n_clusters):
    # first run the clustering algorithm
    kmeans = KMeans(n_clusters=n_clusters, n_init=200).fit(vectors)

    clusters = dict()
    for cluster_index in range(n_clusters):
        centroid = kmeans.cluster_centers_[cluster_index].reshape(1, -1)
        sentences_vector = []
        # initialise with a bucket
        clusters[cluster_index] = {"sentences": {},
                                   "highlight_index": None}
        for index in range(len(kmeans.labels_)):
            # if they equal
            if kmeans.labels_[index] == cluster_index:
                # insert the sentence into the cluster
                # use dictionary!
                clusters[cluster_index]["sentences"][index] = processed[index]
                # insert the vector form as well
                sentences_vector.append(vectors[index])

        sentences_sorted = []
        #sort the sentences by key
        for key in sorted(clusters[cluster_index]["sentences"].keys()):
            sentences_sorted.append(clusters[cluster_index]["sentences"][key])

        #update it with the sorted list
        clusters[cluster_index]["sentences"] = sentences_sorted

        # turn the vector into numpy array
        sentences_vector = np.asarray(sentences_vector)

        # compute the distance to the centroid to each sentence vector.
        pairwise_distance = cdist(X=sentences_vector, Y=centroid, metric='euclidean')

        # and then arg sort it
        pairwise_distance_argsorted = np.argsort(pairwise_distance, axis=0)

        # pick the closest one
        highlight_index = pairwise_distance_argsorted[0][0]

        # store it in the cluster.
        clusters[cluster_index]["highlight_index"] = highlight_index
    return clusters




#now, let's see the summary!
def generate_summary(clusters,
                     processed,
                     tracks):
    summary = dict()
    for cluster in clusters.values():
        highlight_index = cluster['highlight_index']
        highlight_sentence = cluster['sentences'][highlight_index]

        for index in range(len(processed)):
            if highlight_sentence == processed[index]:
                #this is the global index.
                summary[index] = {"highlight_sentence": highlight_sentence,
                                  "cluster": cluster,}
    #sort by the key
    highlights_sorted = []
    clusters_sorted = []
    originals = set()
    for key in sorted(summary.keys()):
        #store them in a sorted order
        highlight_sentence = summary[key]['highlight_sentence']
        cluster = summary[key]['cluster']
        #reset the originals sorted
        originals_sorted = []
        #this is ridiculous, but there is no other way
        for cluster_sentence in cluster['sentences']:
            for track in tracks:
                #try adding it to the set.
                if track in cluster_sentence:
                    already_exist = track in originals
                    if already_exist is False:
                        originals.add(track)
                        if cluster_sentence == highlight_sentence:
                            originals_sorted.append("<strong>{}</strong>".format(track))
                        else:
                            originals_sorted.append(track)



        #after this ends, update the cluster sentences with the originals
        cluster['sentences'] = originals_sorted

        #collec the highlights and clusters
        highlights_sorted.append(highlight_sentence)
        clusters_sorted.append(cluster)


    #update the summary
    summary = []
    for index in range(len(highlights_sorted)):
        summary.append((highlights_sorted[index],
                        clusters_sorted[index]))

    return summary







