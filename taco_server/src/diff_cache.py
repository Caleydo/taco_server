# This file contains the main functions that deal with caching the diff
# at different levels of details
# detail (as detail), middle (as count), overview (as ratios)

from __future__ import print_function
from diff_finder import Table, DiffFinder, Diff, Ratios
import phovea_server.dataset as dataset
import timeit
import json
import ujson
import os
import hashlib
from collections import namedtuple
from os import path

__author__ = 'Reem'
data_directory = path.normpath(path.join(path.dirname(__file__), '../../cache')) + '/'
os.makedirs(data_directory)
print(data_directory)


def get_diff_cache(name):
  file_name = data_directory + name + '.json'
  if os.path.isfile(file_name):
    with open(file_name) as data_file:
      data = json.load(data_file)
      # todo why i don't use ujson here?
    return data
  # if the file doesn't exist
  return None


def set_diff_cache(name, data):
  file_name = data_directory + name + '.json'
  with open(file_name, 'w') as outfile:
    json.dump(data, outfile)


# this is now by default for the detail diff
def get_diff(id1, id2, direction, ops, jsonit=True):
  hash_name = create_hashname(id1, id2, 0, 0, direction, ops)
  if jsonit:
    t1 = timeit.default_timer()
    json_result = get_diff_cache(hash_name)
    t2 = timeit.default_timer()
    print("get diff: cache (json)", t2 - t1)
    # it's not in the cache
    if json_result is None:
      # get one for the detail
      diffobj = calc_diff(id1, id2, direction, ops)
      if isinstance(diffobj, Diff):
        # log the detail
        json_result = ujson.dumps(diffobj.serialize())
        set_diff_cache(hash_name, json_result)
      else:
        # todo later find a way to send the error
        # e.g. there's no matching column in this case
        json_result = ujson.dumps(diffobj)  # which is {} for now!
        set_diff_cache(hash_name, json_result)
    return json_result
  else:
    # not jsonit
    # calc diff for the detail
    t3 = timeit.default_timer()
    diffobj = calc_diff(id1, id2, direction, ops)
    t4 = timeit.default_timer()
    print("get diff: calc diff ", t4 - t3)
    return diffobj


# get the ratios for the overview or the aggregated results for the middle view
def get_ratios(id1, id2, direction, ops, bins=1, bins_col=1, jsonit=True):
  hashname = create_hashname(id1, id2, bins, bins_col, direction, ops)
  json_ratios = get_diff_cache(hashname)
  if json_ratios is None:
    # we calculate the new one
    # get the detail diff
    t4 = timeit.default_timer()
    diffobj = get_diff(id1, id2, direction, ops, False)
    t5 = timeit.default_timer()
    print("get diff in get ratios ", t5 - t4)
    # calculate the ratios for the overview
    t1 = timeit.default_timer()
    ratios = diffobj.aggregate(bins, bins_col)
    t2 = timeit.default_timer()
    print("time to aggregate with ", bins, bins_col, t2 - t1)
    # todo find a better solution for this serialize thing :|
    if bins == 1:
      json_ratios = ujson.dumps(ratios.serialize())
    else:
      json_ratios = ujson.dumps(ratios)
    # cache this as overview
    set_diff_cache(hashname, json_ratios)
    if not jsonit:
      return ratios
  if not jsonit:
    t0 = timeit.default_timer()
    rj = ratio_from_json(json_ratios)
    t3 = timeit.default_timer()
    print("time ratio from json", bins, bins_col, t3 - t0)
    return rj
  return json_ratios


# calc the detailed diff
def calc_diff(id1, id2, direction, ops):
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


def create_hashname(id1, id2, bins, bins_col, direction, ops):
  name = str(id1) + '_' + str(id2) + '_' + str(bins) + '_' + str(bins_col) + '_' + str(direction) + '_' + str(ops)
  return hashlib.md5(name).hexdigest()


def ratio_from_json(jsonobj):
  # idk
  r = json.loads(jsonobj, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
  # todo find a smarter way, really
  cr = 0 if not hasattr(r, "c_ratio") else r.c_ratio
  ar = 0 if not hasattr(r, "a_ratio") else r.a_ratio
  dr = 0 if not hasattr(r, "d_ratio") else r.d_ratio
  no = 100 if not hasattr(r, "no_ratio") else r.no_ratio
  return Ratios(cr, ar, dr, no)

# todo make sure that both dataset have same rowtype and coltype before calling this api function
# todo return a value that could be handled to show an error in the client side
