__author__ = 'Reem'

import diff_cache
import json
import os
import numpy as np
from sklearn import manifold
from sklearn.decomposition import PCA

data_directory = 'plugins/taco_server/MDS_data/'

def get_fd_cache(name):
    file_name = data_directory + name + '.json'
    if os.path.isfile(file_name):
        with open(file_name) as data_file:
          data = json.load(data_file)
        return data
    #if the file doesn't exist
    return None


def set_fd_cache(name, data):
    file_name = data_directory + name + '.json'
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)


#@param ids: should be a list of the table's ids
def calc_fd_graph(ids, direction, ops):
    links = []
    if len(ids) > 0:
        # all elements except the last one
        for i, id1 in enumerate(ids[:-1]):
            # all elements except the i and all before
            # +1 to make sure that they are not identical
            for j, id2 in enumerate(ids[i+1:]):
                r = diff_cache.get_ratios(id1, id2, direction, ops, False)
                links += [{"source": ids.index(id1), "target": ids.index(id2), "value": 100 - float(r.no_ratio * 100)}]
    # todo cache this in the MDS data
    return links


def calc_mds_graph(ids):
    # this is diff not similarities :|!
    distances = []
    for i, id1 in enumerate(ids):
        sim_row = []
        for j, id2 in enumerate(ids):
            if id1 == id2:
                sim_row += [0]
            else:
                r = diff_cache.get_ratios(id1, id2, 2, "structure,content", False)
                sim_row += [1 - r.no_ratio]
        distances.append(sim_row)

    # http://baoilleach.blogspot.co.at/2014/01/convert-distance-matrix-to-2d.html
    # it doesn't really change the result :|
    # adist = np.array(similarities)
    # amax = np.amax(adist)
    # adist /= amax

    mds = manifold.MDS(n_components=2, max_iter=3000, random_state=6, eps=1e-9,
                       dissimilarity="precomputed", n_jobs=1)
    res = mds.fit(distances)
    # res = mds.fit(adist)
    pos = res.embedding_

    # Rescale the data
    # pos *= np.sqrt((X_true ** 2).sum()) / np.sqrt((pos ** 2).sum())
    # npos *= np.sqrt((X_true ** 2).sum()) / np.sqrt((npos ** 2).sum())

    # Rotate the data
    # clf = PCA(n_components=2)
    #
    # pos = clf.fit_transform(pos)
    #
    # npos = clf.fit_transform(npos)

    #np
    #similarities = similarities.max() / similarities * 100
    #similarities[np.isinf(similarities)] = 0

    # Plot the edges
    #start_idx, end_idx = np.where(pos)

    #return pos
    return pos_to_json(pos)


def graph_nodes(ids):
    # dataset.get(ids).name
    # todo get the name from the dataset caleydo api
    nodes = [{"name": str(i)} for i in ids]
    return nodes


# convert the ndarray to a parsable json thing :|
def pos_to_json(pos):
  json_pos = []
  for i, p in enumerate(pos):
    json_pos += [{'x': p[0], 'y': p[1]}]
  return {'pos': json_pos, 'xmin': pos[:,0].min(), 'xmax': pos[:,0].max(), 'ymin': pos[:,1].min(), 'ymax': pos[:,1].max()}
