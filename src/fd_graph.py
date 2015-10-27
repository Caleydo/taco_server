__author__ = 'Reem'

import diff_cache
import json
import os
from diff_finder import Levels

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


#@ids: should be a list of the table's ids
def calc_fd_graph(ids, lod, direction, ops):
    if len(ids) > 0:
        # all elements except the last one
        for i, id1 in enumerate(ids[:-1]):
            # all elements except the i and all before
            # +1 to make sure that they are not identical
            for j, id2 in enumerate(ids[i+1:]):
                hashname_detail = diff_cache.create_hashname(id1, id2, Levels.detail, direction, ops)
                json_result = diff_cache.get_diff_cache(hashname_detail)
                if json_result is None:
                    json_result = diff_cache.calc_diff(id1, id2, lod, direction, ops)
                    diff_cache.set_diff_cache(hashname_detail, json_result)
                if lod < Levels.detail: #or less than middle
                    hashname_overview = diff_cache.create_hashname(id1, id2, Levels.overview, direction, ops)
                    diff_cache.set_diff_cache(hashname_overview, json_result)
                #todo use this json_result

    return None
