# This file contains the main functions that deal with caching the diff
# at different levels of details
# detail (as detail), middle (as count), overview (as ratios)


from .diff_finder import Table, DiffFinder, Diff, Ratios
import phovea_server.dataset as dataset
import timeit
import json
from . import json_encoder
import os
import hashlib
from collections import namedtuple
from os import path
import logging

__author__ = 'Reem'

_log = logging.getLogger(__name__)

"""
Path to the cache directory
"""
_cache_directory = path.normpath(path.join(path.dirname(__file__), '../../cache')) + '/'


def create_cache_dir():
  """
  Create cache directory
  :return:
  """
  if os.path.isdir(_cache_directory) is False:
    os.makedirs(_cache_directory)
    _log.info('cache directory created at: ' + _cache_directory)

  else:
    _log.info('use existing cache directory: ' + _cache_directory)


# run immediately!
create_cache_dir()


def get_diff_cache(filename):
  """
  Loads a cache result by filename
  :param filename:
  :return:
  """
  file_name = _cache_directory + filename + '.json'
  if os.path.isfile(file_name):
    with open(file_name) as data_file:
      data = json.load(data_file)
    return data
  # if the file doesn't exist
  return None


def set_diff_cache(filename, data):
  """
  Writing data to a given cached filename
  :param filename:
  :param data:
  :return:
  """
  file_name = _cache_directory + filename + '.json'
  with open(file_name, 'w') as outfile:
    json.dump(data, outfile)


# this is now by default for the detail diff
def get_diff_table(id1, id2, direction, ops, jsonit=True):
  """
  Get cached data for the diff table and if not available calculate and cache it
  :param id1:
  :param id2:
  :param direction:
  :param ops:
  :param jsonit: If True return result as json string. Otherwise return Python object.
  :return:
  """

  # HACK: force calculation of everything. then we only do it once and use the cache in the future
  all_ops = "structure,content,merge,reorder"

  hash_name = create_hashname(id1, id2, 0, 0, direction, all_ops)

  t1 = timeit.default_timer()
  json_result = get_diff_cache(hash_name)
  t2 = timeit.default_timer()
  _log.debug("TIMER: get diff: cache (json)", t2 - t1)
  diffobj = None

  if json_result is None:
    # get one for the detail
    t3 = timeit.default_timer()
    diffobj = calc_diff(id1, id2, direction, all_ops)
    t4 = timeit.default_timer()
    _log.debug("TIMER: get diff: calc diff ", t4 - t3)

    if isinstance(diffobj, Diff):
      # log the detail
      serialize = Diff.serialize # noqa E121
      json_result = (json.dumps(diffobj.__dict__, cls=json_encoder.JsonEncoder))
      set_diff_cache(hash_name, json_result)
    else:
      # todo later find a way to send the error
      # e.g. there's no matching column in this case
      json_result = json.dumps(diffobj, cls=json_encoder.JsonEncoder)  # which is {} for now!
      set_diff_cache(hash_name, json_result)

  elif jsonit is False:
    diffobj = Diff().unserialize(json.loads(json_result))

  if jsonit:
    return json_result
  else:
    return diffobj


def get_ratios(id1, id2, direction, ops, bins=1, bins_col=1, jsonit=True):
  """
  Get the ratios for the overview or the aggregated results for the middle view
  :param id1:
  :param id2:
  :param direction:
  :param ops:
  :param bins:
  :param bins_col:
  :param jsonit: If True return result as json string. Otherwise return Python object.
  :return:
  """
  hashname = create_hashname(id1, id2, bins, bins_col, direction, ops)
  json_ratios = get_diff_cache(hashname)

  if json_ratios is None:
    # we calculate the new one
    # get the detail diff
    t4 = timeit.default_timer()

    diffobj = get_diff_table(id1, id2, direction, ops, False)

    t5 = timeit.default_timer()
    _log.debug("TIMER: get diff in get ratios ", t5 - t4)
    # calculate the ratios for the overview
    t1 = timeit.default_timer()

    ratios = diffobj.aggregate(bins, bins_col)

    t2 = timeit.default_timer()
    _log.debug("TIMER: time to aggregate with ", bins, bins_col, t2 - t1)
    # todo find a better solution for this serialize thing :|
    # bin == 1 -> timeline bar chart
    # bin == -1 -> 2d ratio plot
    if bins == 1 or bins == -1:
      json_ratios = json.dumps(ratios.serialize(), cls=json_encoder.JsonEncoder)
    # bin > 1 -> 2d ratio histogram
    else:
      json_ratios = json.dumps(ratios, cls=json_encoder.JsonEncoder)

    # cache this as overview
    set_diff_cache(hashname, json_ratios)

    if not jsonit:
      return ratios

  if not jsonit:
    t0 = timeit.default_timer()
    rj = ratio_from_json(json_ratios)
    t3 = timeit.default_timer()
    _log.debug("TIMER: time ratio from json", bins, bins_col, t3 - t0)
    return rj

  return json_ratios


# calc the detailed diff
def calc_diff(id1, id2, direction, ops):
  """
  Calculate a detailed difference between two tables
  :param id1:
  :param id2:
  :param direction:
  :param ops:
  :return:
  """
  ds1 = dataset.get(id1)
  ds2 = dataset.get(id2)

  def stratify_matrix(m):
    # NOTE: ids must match with the hard-coded ones in taco/src/data_set_selector.ts -> prepareTCGAData()
    row_strat = dataset.get(m.id + '4CnmfClustering')
    col_strat = dataset.get(m.id + 'TreeClusterer1')

    data = m.asnumpy()
    rows = m.rows() if row_strat is None else row_strat.rows()
    cols = m.cols() if col_strat is None else col_strat.rows()

    if row_strat is not None:
      rowids = list(m.rowids())
      row_indices = [rowids.index(o) for o in row_strat.rowids()]
      data = data[row_indices, ...].astype('str')

    if col_strat is not None:
      colids = list(m.colids())
      col_indices = [colids.index(o) for o in col_strat.rowids()]
      data = data[..., col_indices].astype('str')

    return Table(rows, cols, data)

  # create the table object
  table1 = stratify_matrix(ds1)
  table2 = stratify_matrix(ds2)
  diff_finder = DiffFinder(table1, table2, ds1.rowtype, ds2.coltype, direction)
  t2 = timeit.default_timer()
  d = diff_finder.generate_diff(ops)
  t3 = timeit.default_timer()
  _log.debug("TIMER: time to generate diff", t3 - t2)
  if isinstance(d, Diff):
    d.add_union(diff_finder.union)
  return d


def create_hashname(id1, id2, bins, bins_col, direction, ops):
  """
  Helper function to generate a hash name for the cached filename
  :param id1:
  :param id2:
  :param bins:
  :param bins_col:
  :param direction:
  :param ops:
  :return:
  """
  name = str(id1) + '_' + str(id2) + '_' + str(bins) + '_' + str(bins_col) + '_' + str(direction) + '_' + str(ops)
  return hashlib.md5(name.encode('utf-8')).hexdigest()


def ratio_from_json(jsonobj):
  # idk
  r = json.loads(jsonobj, object_hook=lambda d: namedtuple('X', d.keys())(*list(d.values())))
  # todo find a smarter way, really
  cr = 0 if not hasattr(r, "c_ratio") else r.c_ratio
  ar = 0 if not hasattr(r, "a_ratio") else r.a_ratio
  dr = 0 if not hasattr(r, "d_ratio") else r.d_ratio
  no = 100 if not hasattr(r, "no_ratio") else r.no_ratio
  return Ratios(cr, ar, dr, no)

# todo make sure that both dataset have same rowtype and coltype before calling this api function
# todo return a value that could be handled to show an error in the client side
