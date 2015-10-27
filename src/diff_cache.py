__author__ = 'Reem'

from diff_finder import Table, DiffFinder, Diff, Levels, Ratios
import caleydo_server.dataset as dataset
import timeit
import json
import ujson
import os
import hashlib

data_directory = 'plugins/taco_server/cache/'

def get_diff_cache(name):
    file_name = data_directory + name + '.json'
    if os.path.isfile(file_name):
        with open(file_name) as data_file:
          data = json.load(data_file)
        return data
    #if the file doesn't exist
    return None


def set_diff_cache(name, data):
    file_name = data_directory + name + '.json'
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

def get_diff(id1, id2, lod, direction, ops, jsonit=True):
    # todo either lod here should be 0 for overview (not 1) or we make sure of this in the client
    hash_name = create_hashname(id1, id2, lod, direction, ops)
    json_result = get_diff_cache(hash_name)
    if not jsonit and lod < Levels.detail:
        r = Ratios(0,0,0,100)
        return r.from_json(json_result)
    ## it's not in the cache
    if json_result is None:
        #get one for the detail
        diffobj = calc_diff(id1, id2, Levels.detail, direction, ops)
        if isinstance(diffobj, Diff):
            #log the detail
            json_result = ujson.dumps(diffobj.serialize())
            set_diff_cache(hash_name, json_result)
            if lod < Levels.detail: # or check for being overview or +1
                # calculate the ratios for the overview
                ratios = diffobj.ratios()
                json_result = ujson.dumps(ratios.seraialize())
                # cache this as overview
                overview_hashname = create_hashname(id1, id2, Levels.overview, direction, ops)
                set_diff_cache(overview_hashname, json_result)
                if not jsonit:
                    return ratios
        else:
            # todo later find a way to send the error
            # e.g. there's no matching column in this case
            json_result = ujson.dumps(diffobj)  # which is {} for now!
            set_diff_cache(hash_name, json_result)
    return json_result

def calc_diff(id1, id2, lod, direction, ops):
    ds1 = dataset.get(id1)
    ds2 = dataset.get(id2)
    # create the table object
    table1 = Table(ds1.rows(), ds1.cols(), ds1.asnumpy())
    table2 = Table(ds2.rows(), ds2.cols(), ds2.asnumpy())
    dfinder = DiffFinder(table1, table2, ds1.rowtype, ds2.coltype, lod, direction)
    t2 = timeit.default_timer()
    d = dfinder.generate_diff(ops)
    t3 = timeit.default_timer()
    print("time to generate diff", t3 - t2)
    if isinstance(d, Diff):
        d.add_union(dfinder.union)
    return d

def create_hashname(id1, id2, lod, direction, ops):
    name = str(id1) + '_' + str(id2) + '_' + str(lod) + '_' + str(direction) + '_' + str(ops)
    return hashlib.md5(name).hexdigest()

# todo make sure that both dataset have same rowtype and coltype before calling this api function
# todo return a value that could be handled to show an error in the client side
