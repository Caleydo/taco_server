__author__ = 'Reem'

import diff_cache
import json
import ujson
import os
from collections import namedtuple

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
                hash_name = diff_cache.create_hashname(id1, id2, lod, direction, ops)
                json_result = diff_cache.get_diff_cache(hash_name)
                if json_result is None:
                    json_result = diff_cache.calc_diff(id1, id2, lod, direction, ops)
                    diff_cache.set_diff_cache(hash_name, json_result)
                #todo use this json_result
                # http://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object#answer-15882054
                # Parse JSON into an object with attributes corresponding to dict keys.
                x = json.loads(json_result, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                print ("content", x.structure.added_rows)
    return None
