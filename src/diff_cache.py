__author__ = 'Reem'

from diff_finder import Table, DiffFinder, Diff, Levels, Ratios
import caleydo_server.dataset as dataset
import timeit
import json
import ujson
import os
import hashlib
from collections import namedtuple

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
    hash_name = create_hashname(id1, id2, lod, direction, ops)
    json_result = get_diff_cache(hash_name)
    ## it's not in the cache
    if json_result is None:
        #get one for the detail
        diffobj = calc_diff(id1, id2, Levels.detail, direction, ops)
        if isinstance(diffobj, Diff):
            #log the detail
            json_result = ujson.dumps(diffobj.serialize())
            set_diff_cache(hash_name, json_result)
            if not jsonit:
                return diffobj
        else:
            # todo later find a way to send the error
            # e.g. there's no matching column in this case
            json_result = ujson.dumps(diffobj)  # which is {} for now!
            set_diff_cache(hash_name, json_result)
    if not jsonit:
        return diff_from_json(json_result)
    return json_result

def get_ratios(id1, id2, direction, ops, jsonit=True):
    overview_hashname = create_hashname(id1, id2, Levels.overview, direction, ops)
    json_ratios = get_diff_cache(overview_hashname)
    if json_ratios is None:
        #we calculate the new one
        diffobj = get_diff(id1, id2, Levels.detail, direction, ops, False)
        # calculate the ratios for the overview
        ratios = diffobj.ratios()
        json_ratios = ujson.dumps(ratios.seraialize())
        # cache this as overview
        set_diff_cache(overview_hashname, json_ratios)
        if not jsonit:
            return ratios
    if not jsonit:
        return ratio_from_json(json_ratios)
    return json_ratios

def calc_diff(id1, id2, lod, direction, ops):
    ds1 = dataset.get(id1)
    ds2 = dataset.get(id2)
    # create the table object
    table1 = Table(ds1.rows(), ds1.cols(), ds1.asnumpy())
    table2 = Table(ds2.rows(), ds2.cols(), ds2.asnumpy())
    dfinder = DiffFinder(table1, table2, ds1.rowtype, ds2.coltype, direction)
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

# todo as this just normal conversion
# we have to assign every attribute or so?
def diff_from_json(jsonobj):
    # http://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object#answer-15882054
    # Parse JSON into an object with attributes corresponding to dict keys.
    x = json.loads(jsonobj, object_hook=lambda d: namedtuple('Diff', d.keys())(*d.values()))
    d = Diff()
    d.content = x.content
    d.structure = {}
    d.structure["deleted_rows"] = x.structure.deleted_rows
    d.structure["added_rows"] = x.structure.added_rows
    d.structure["deleted_cols"] = x.structure.deleted_cols
    d.structure["added_cols"] = x.structure.added_cols
    d.merge = x.merge
    d.reorder = x.reorder
    d.union = {}
    d.union['ur_ids'] = x.union.ur_ids
    d.union['uc_ids'] = x.union.uc_ids
    return d #todo

def ratio_from_json(jsonobj):
    #idk
    r = json.loads(jsonobj, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    #todo find a smarter way, really
    cr = 0 if not hasattr(r, "c_ratio") else r.c_ratio
    ar = 0 if not hasattr(r, "a_ratio") else r.a_ratio
    dr = 0 if not hasattr(r, "d_ratio") else r.d_ratio
    no = 100 if not hasattr(r, "no_ratio") else r.no_ratio
    return Ratios(cr , ar, dr, no)

# todo make sure that both dataset have same rowtype and coltype before calling this api function
# todo return a value that could be handled to show an error in the client side
