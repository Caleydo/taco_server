#!/usr/bin/python
import numpy as np
import timeit
from enum import Enum
import logging

__author__ = 'Reem'

_log = logging.getLogger(__name__)

D_ROWS = 0
D_COLS = 1
D_ROWS_COLS = 2


class Levels(Enum):
  detail = 4
  middle = 2
  overview = 0


# reads a csv file (using full file path) and returns the data table with the IDs
def get_full_table(file):
  # data = np.genfromtxt(file, dtype=None, delimiter=',', names=True)
  data = np.genfromtxt(file, dtype='object', delimiter=',')
  row_ids = data[1:][:, 0]
  col_ids = data[0, :][1:]
  table = data[1:, 1:]
  return Table(row_ids, col_ids, table)


# Helper functions #

# get the IDs available only in the first one
def get_deleted_ids(ids1, ids2):
  # might want to use this instead for numpy arrays http://docs.scipy.org/doc/numpy/reference/generated/numpy.setdiff1d.html
  return list(set(ids1) - set(ids2))


# get the IDs available only in the second one
def get_added_ids(ids1, ids2):
  return list(set(ids2) - set(ids1))


def get_intersection(ids1, ids2):
  # return np.array(list(set(ids1).intersection(ids2)))
  return np.intersect1d(ids1, ids2)


def get_union_ids(ids1, ids2):
  if ids1.shape[0] < ids2.shape[0]:
    first = ids2
    second = ids1
  else:
    first = ids1
    second = ids2

  u = np.array(second, dtype='object')
  # u = list(second)

  deleted = get_deleted_ids(first, second)
  for i in deleted:
    index1 = np.where(first == i)[0][0]

    if index1 == 0:
      # it's deleted from the first position
      # add it at position index1
      u = np.insert(u, 0, i)

    else:
      # it's somewhere in the middle, find the position of the one before
      index1 -= 1
      pre_element = first[index1]

      while pre_element not in u:
        index1 -= 1
        if index1 >= 0:
          pre_element = first[index1]

        else:
          print("CORNER CASE: there's no element before that exists in the list then just add it at 0!")
          pre_element = None
          break

      if pre_element is not None:
        pre_index = np.where(u == pre_element)[0][0]
        # insert the new element after the pre_element
        u = np.insert(u, pre_index + 1, i)
      else:
        u = np.insert(u, 0, i)

      # todo if the index is not available
  return u


# this returns values between [0,1]
def normalize_float01(diff_matrix):
  min = diff_matrix.min()
  max = diff_matrix.max()
  # notice float(1)/2 * m gives a float result better than m/2
  # x = (x - min) / (max - min)
  normalized = (diff_matrix - min) * (float(1) / (max - min))
  return normalized


# this returns values between [-1,1]
def normalize_float_11(diff_matrix):
  min = diff_matrix.min()
  max = diff_matrix.max()
  max = abs(min) if abs(min) > abs(max) else abs(max)
  # notice float(1)/2 * m gives a float result better than m/2
  if max > 0:
    normalized = diff_matrix * (float(1) / max)
    return normalized
  return None


# helping functions from caleydo
def assign_ids(ids, idtype):
  import phovea_server.plugin

  manager = phovea_server.plugin.lookup('idmanager')
  return np.array(manager(ids, idtype))


# calcuate the percentage of changed cells regarding the intersection table
def calc_ch_percentage(chc, rc, cc):
  return float(chc) / (rc * cc)


def generate_diff_from_files(file1, file2):
  # full_table1 = get_full_table(file1)
  # full_table2 = get_full_table(file2)
  # todo use the classes
  # return generate_diff(full_table1, full_table2, None, None, 2)
  pass


# Table data structure
class Table:
  def __init__(self, rows, cols, content):
    self.row_ids = np.asarray(rows, 'object').astype(str)
    self.col_ids = np.asarray(cols, 'object').astype(str)
    self.content = content


# Diff object data structure
class Diff:
  def __init__(self, content=None, structure=None, merge=None, reorder=None, union=None, direction=D_ROWS_COLS):
    self._direction = direction
    self.content = [] if content is None else content
    self.structure = {} if structure is None else structure
    self.merge = {} if merge is None else merge
    self.reorder = {'rows': [], 'cols': []} if reorder is None else reorder
    self.union = {} if union is None else union

  # todo decide if the union should be here or in the diff finder
  def add_union(self, union):
    self.union = {}
    self.union["uc_ids"] = union["uc_ids"].tolist()
    self.union["c_ids"] = union["c_ids"]
    self.union["ur_ids"] = union["ur_ids"].tolist()
    self.union["r_ids"] = union["r_ids"]

  def serialize(self):
    return {
        "content": self.content,
        "structure": self.structure,
        "merge": self.merge,
        "reorder": self.reorder,
        "union": self.union
    }

  def unserialize(self, json_obj):
    self.content = json_obj['content'] if 'content' in list(json_obj.keys()) else []
    self.structure = json_obj['structure'] if 'structure' in list(json_obj.keys()) else {}
    self.merge = json_obj['merge'] if 'merge' in list(json_obj.keys()) else {}
    self.reorder = json_obj['reorder'] if 'reorder' in list(json_obj.keys()) else {'rows': [], 'cols': []}
    self.union = json_obj['union'] if 'union' in list(json_obj.keys()) else {}
    return self

  def content_counts_percell(self):
    return float(len(self.content))

  def content_ratio_percell(self, ucells, counts=None):
    if counts is None:
      counts = self.content_counts_percell()
    return counts / ucells

  # rowAdd rowDel colAdd colDel
  def struct_counts(self, urows, ucols, dir, st_op):
    operation = st_op + "eted" if st_op == "del" else st_op + "ed"
    return float(len(self.structure[operation + "_" + dir + "s"]))

  # rowAdd rowDel colAdd colDel
  def struct_ratio(self, urows, ucols, dir, st_op, counts=None):
    rows = urows if dir == "row" else ucols

    if counts is None:
      counts = self.struct_counts(urows, ucols, dir, st_op)

    return counts / rows

  def struct_add_counts(self, width, height):
    addc = 0
    h = height
    w = width
    if "deleted_rows" in self.structure:
      h -= len(self.structure["deleted_rows"])
    if "deleted_cols" in self.structure:
      w -= len(self.structure["deleted_cols"])
    if "added_rows" in self.structure:
      addc += len(self.structure["added_rows"]) * w
      h -= len(self.structure["added_rows"])
    if "added_cols" in self.structure:
      addc += len(self.structure["added_cols"]) * h
      w -= len(self.structure["added_cols"])  # we might need this later!
    # the type here should be just add but i'm using row-add for css
    return float(addc)

  def struct_add_ratio(self, width, height, counts=None):
    cells = width * height
    if counts is None:
      counts = self.struct_add_counts(width, height)
    return counts / cells

  def struct_del_counts(self, width, height):
    delc = 0
    h = height
    w = width
    if "deleted_rows" in self.structure:
      delc += len(self.structure["deleted_rows"]) * w
      h -= len(self.structure["deleted_rows"])
    if "deleted_cols" in self.structure:
      delc += len(self.structure["deleted_cols"]) * h
    # the type here should be just add and del but i'm using row-add and row-del for css
    return float(delc)

  def struct_del_ratio(self, width, height, counts=None):
    cells = width * height
    if counts is None:
      counts = self.struct_del_counts(width, height)
    return counts / cells

  def nochange_counts(self, width, height):
    h = height
    w = width
    # the height without the removed or added rows
    if "deleted_rows" in self.structure:
      h -= len(self.structure["deleted_rows"])
    if "added_rows" in self.structure:
      h -= len(self.structure["added_rows"])
    # if "rows" in self.reorder:
    #   h -= len(self.reorder["rows"])
    # the width without the deleted or removed cols
    if "deleted_cols" in self.structure:
      w -= len(self.structure["deleted_cols"])
    if "added_cols" in self.structure:
      w -= len(self.structure["added_cols"])
    # if "cols" in self.reorder:
    #   w -= len(self.reorder["cols"])
    # the rest cells without the changed ones
    noc = (h * w) - len(self.content)
    return float(noc)

  def nochange_ratio(self, width, height, counts=None):
    cells = width * height
    if counts is None:
      counts = self.nochange_counts(width, height)
    return counts / cells

  def nochange_rows_counts(self, width, height):
    h = height
    w = width
    # the width without the deleted or removed cols
    if "deleted_cols" in self.structure:
      w -= len(self.structure["deleted_cols"])
    if "added_cols" in self.structure:
      w -= len(self.structure["added_cols"])
    # if "cols" in self.reorder:
    #   w -= len(self.reorder["cols"])
    # the height without the removed or added rows
    if "deleted_rows" in self.structure:
      h -= len(self.structure["deleted_rows"])
    if "added_rows" in self.structure:
      h -= len(self.structure["added_rows"])
    # if "rows" in self.reorder:
    #   h -= len(self.reorder["rows"])
    # the rest cells without the changed ones
    noc = (h * w) - len(self.content)
    return float(noc)

  def nochange_rows_ratio(self, width, height, counts=None):
    h = height
    w = width

    # the width without the deleted or removed cols
    if "deleted_cols" in self.structure:
      w -= len(self.structure["deleted_cols"])
    if "added_cols" in self.structure:
      w -= len(self.structure["added_cols"])
    # if "cols" in self.reorder:
    #   w -= len(self.reorder["cols"])

    cells = w * h

    if counts is None:
      counts = self.nochange_rows_counts(width, height)

    return counts / cells

  def nochange_cols_counts(self, width, height):
    h = height
    w = width
    # the height without the removed or added rows
    if "deleted_rows" in self.structure:
      h -= len(self.structure["deleted_rows"])
    if "added_rows" in self.structure:
      h -= len(self.structure["added_rows"])
    # if "rows" in self.reorder:
    #   h -= len(self.reorder["rows"])
    # the width without the deleted or removed cols
    if "deleted_cols" in self.structure:
      w -= len(self.structure["deleted_cols"])
    if "added_cols" in self.structure:
      w -= len(self.structure["added_cols"])
    # if "cols" in self.reorder:
    #   w -= len(self.reorder["cols"])
    # the rest cells without the changed ones
    noc = (h * w) - len(self.content)
    return float(noc)

  def nochange_cols_ratio(self, width, height, counts=None):
    h = height
    w = width

    # the height without the removed or added rows
    if "deleted_rows" in self.structure:
      h -= len(self.structure["deleted_rows"])
    if "added_rows" in self.structure:
      h -= len(self.structure["added_rows"])
    # if "rows" in self.reorder:
    #   h -= len(self.reorder["rows"])

    cells = w * h

    if counts is None:
      counts = self.nochange_cols_counts(width, height)

    return counts / cells

  def reorder_rows_counts(self):
    """
    Count only cells with content changes
    :param width:
    :param height:
    :return:
    """
    ids = [r['id'] for r in self.reorder['rows']]
    filtered_content = [r for r in self.content if r['row'] in ids]
    return float(len(filtered_content))

  def reorder_cols_counts(self):
    """
    Count only cells with content changes
    :param width:
    :param height:
    :return:
    """
    ids = [r['id'] for r in self.reorder['cols']]
    filtered_content = [r for r in self.content if r['col'] in ids]
    return float(len(filtered_content))

  def reorder_rows_cols_counts(self):
    """
    Count only cells with content changes
    :param width:
    :param height:
    :return:
    """
    row_ids = [r['id'] for r in self.reorder['rows']]
    col_ids = [r['id'] for r in self.reorder['cols']]
    filtered_content = [r for r in self.content if r['col'] in col_ids and r['row'] in row_ids]
    return float(len(filtered_content))

  def reorder_counts(self):
    reordered_counts = 0

    if "rows" in self.reorder and "cols" in self.reorder:
      reordered_counts = self.reorder_rows_cols_counts()

    elif "rows" in self.reorder:
      reordered_counts = self.reorder_rows_counts()

    elif "cols" in self.reorder:
      reordered_counts = self.reorder_cols_counts()

    return float(reordered_counts)

  def reorder_ratio(self, width, height, counts=None):
    cells = width * height
    if counts is None:
      counts = self.reorder_counts()
    return counts / cells

  def aggregate(self, bins, bins_col=2):
    if bins == 1:
      _log.info('aggregation for timeline bar chart')
      # todo do we want to return it as an array of one element?
      # the ratios for line up
      # todo change this and remove the serialize
      return self.ratios(True)

    elif bins == -1:
      _log.info('aggregation for 2D ratio')
      # the ratios for the 2d histogram
      return self.ratios(False)

    else:
      _log.info('aggregation for 2D ratio histogram')
      # it's the case of histogram or bar plot
      result = {}
      if self._direction == D_ROWS_COLS or self._direction == D_ROWS:
        union_rows = self.union['ur_ids'] if 'ur_ids' in list(self.union.keys()) else []
        max_height = len(union_rows)
        if bins >= max_height:
          # this is the case of bar plot
          # assume that the bins are the max_height
          result["rows"] = self.per_entity_ratios(D_ROWS)
        else:
          # bins < max_height:
          # this is the case of histogram
          # calculate the sqrt(rows) and take the smaller integer as number of bins
          autobins = min(bins, len(union_rows))
          result["rows"] = self.per_bin_ratios(autobins, "rows")

      # todo the rows might have different bins number than the cols
      if self._direction == D_ROWS_COLS or self._direction == D_COLS:
        # if it's the cols not the rows then switch
        union_cols = self.union['uc_ids'] if 'uc_ids' in list(self.union.keys()) else []
        max_width = len(union_cols)
        if bins_col >= max_width:
          # todo handle the > alone or?
          # this is the case of bar plot
          # assume that the bins are the max_height
          result["cols"] = self.per_entity_ratios(D_COLS)
        else:  # bins < max_width:
          # this is the case of histogram
          # calculate the sqrt(rows) and take the smaller integer as number of bins
          autobins = min(bins_col, len(union_cols))
          result["cols"] = self.per_bin_ratios(autobins, "cols")

      return result

  def per_bin_ratios(self, bins, e_type):
    # get a partial diff where every row is a diff
    # get the direction
    if e_type == "rows":
      union_rows = self.union['ur_ids']
      union_cols = self.union['uc_ids']
      dir = D_ROWS
      row = 'row'
    elif e_type == "cols":
      # if it's the cols not the rows then switch
      union_rows = self.union['uc_ids']
      union_cols = self.union['ur_ids']
      dir = D_COLS
      row = 'col'
    else:
      return []  # this should not happen!
      # todo handle the case of both rows and columns
    ratios_list = []
    length = len(union_rows)
    last_bin = bins - 1
    bins_list = [0] * bins

    indices = np.arange(length)
    bin_range = np.linspace(1, length, bins)
    index2bin = np.digitize(indices, bin_range)

    # todo handle the error here when there's no row !
    pcontent = [[] for x in range(bins)]
    for c in self.content:
      ci = union_rows.index(c[row])
      bin_index = index2bin[ci]
      if bin_index > last_bin:
        bin_index = last_bin
      bins_list[bin_index] += 1  # we don't add the value changes for now
      pcontent[bin_index] += [c]

    # for structure changes
    pstructure = [{"added_" + e_type: [], "deleted_" + e_type: []} for x in range(bins)]
    # filter for the structure changes, because once there's a structure change, there's no need to find content #what!!
    for a in self.structure["added_" + e_type]:
      ai = union_rows.index(a['id'])
      a_index = index2bin[ai]
      if a_index > last_bin:
        a_index = last_bin
      pstructure[a_index]["added_" + e_type] += [a]

    # find the deleted
    for d in self.structure["deleted_" + e_type]:
      di = union_rows.index(d['id'])
      d_index = index2bin[di]
      if d_index > last_bin:
        d_index = last_bin
      pstructure[d_index]["deleted_" + e_type] += [d]

    # convert to np.array to use np.where
    union_rows = np.array(union_rows)
    for i in range(bins):
      temp = union_rows[np.where(index2bin == i)[0]].astype('str').tolist()
      if dir == D_ROWS:
        punion = {
            "ur_ids": temp,
            "uc_ids": union_cols,
        }
      else:
        punion = {
            "ur_ids": union_cols,  # which are union rows
            "uc_ids": temp,
        }

      # 2. create the partial diff
      if len(pcontent[i]) == 0:
        pcontent[i] = None
      partial = Diff(content=pcontent[i], structure=pstructure[i], merge=None, reorder=None, union=punion,
                     direction=dir)
      # 3. calcualte the ratio for this part :|
      # todo remove the serialize
      partial_ratio = partial.ratios()
      ratios_list += [{"ratios": partial_ratio.ratios.serialize(),
                       "counts": partial_ratio.counts.serialize(),
                       "id": temp[0] + '-' + temp[-1],  # first and last id
                       "pos": i}]

    return ratios_list

  def per_entity_ratios(self, dir):
    # get a partial diff where every row is a diff
    # 1. Partition
    # get the direction
    union_rows = self.union['ur_ids'] if 'ur_ids' in list(self.union.keys()) else []
    union_cols = self.union['uc_ids'] if 'uc_ids' in list(self.union.keys()) else []
    e_type = "rows"
    row_id = "row"

    if dir == D_COLS:
      # if it's the cols not the rows then switch
      union_rows = self.union['uc_ids'] if 'uc_ids' in list(self.union.keys()) else []
      union_cols = self.union['ur_ids'] if 'ur_ids' in list(self.union.keys()) else []
      # todo handle the case of both rows and columns
      e_type = "cols"
      row_id = "col"

    ratios_list = []

    for i, id in enumerate(union_rows):
      # todo change this in case of columns
      punion = {
          "ur_ids": [id],  # should be a list or might cause troubles :|
          "uc_ids": union_cols
      }
      pcontent = None
      pstructure = {}
      # filter for the structure changes, because once there's a structure change, there's no need to find content
      # idk why but obj is Diff!
      pstructure["added_" + e_type] = [obj for obj in self.structure["added_" + e_type] if obj['id'] == id]
      if len(pstructure["added_" + e_type]) != 0:
        # create a ratio where it's only added
        ratio_counts = RatiosAndCounts(Ratios(0, 1, 0, 0), Counts(0, len(union_cols), 0, 0))
      else:
        # find the deleted
        pstructure["deleted_" + e_type] = [obj for obj in self.structure["deleted_" + e_type] if obj['id'] == id]
        if len(pstructure["deleted_" + e_type]) != 0:
          ratio_counts = RatiosAndCounts(Ratios(0, 0, 1, 0), Counts(0, 0, len(union_cols), 0))
        else:
          # find the content
          pcontent = [obj for obj in self.content if obj[row_id] == id]
          if len(pcontent) == 0:
            pcontent = None
          # more resonable in the case of subtable
          # 2. create the partial diff
          partial = Diff(content=pcontent, structure=pstructure, merge=None, reorder=None, union=punion,
                         direction=D_ROWS)
          # 3. calcualte the ratio for this part :|
          # todo remove the serialize
          ratio_counts = partial.ratios()
      ratios_list += [{"ratios": ratio_counts.ratios.serialize(),
                       "counts": ratio_counts.counts.serialize(),
                       "id": id,
                       "pos": i}]

    return ratios_list

  def ratios(self, combined=True):
    # todo check that the union already exists!!
    urows = len(self.union['ur_ids'])
    ucols = len(self.union['uc_ids'])
    union_cells = urows * ucols

    # content and no changes are the same for both directions
    if combined:

      # Lineup relevant
      ccounts = self.content_counts_percell()
      no_counts = self.nochange_counts(ucols, urows)
      scounts_a = self.struct_add_counts(ucols, urows)
      scounts_d = self.struct_del_counts(ucols, urows)
      reorder_counts = self.reorder_counts()
      counts = Counts(ccounts, scounts_a, scounts_d, no_counts, reorder_counts)

      cratio = self.content_ratio_percell(union_cells, counts.c_counts)
      no_ratio = self.nochange_ratio(ucols, urows, counts.no_counts)
      sratio_a = self.struct_add_ratio(ucols, urows, counts.a_counts)
      sratio_d = self.struct_del_ratio(ucols, urows, counts.d_counts)
      reorder_ratio = self.reorder_ratio(ucols, urows, counts.r_counts)
      ratios = Ratios(cratio, sratio_a, sratio_d, no_ratio, reorder_ratio)

      return RatiosAndCounts(ratios, counts)

    else:
      # Lineup not relevant

      # ROWS

      # calc new union cells as the are less now
      # todo check if the attribute is there
      r_union_cells = (ucols - len(self.structure["added_cols"]) - len(self.structure["deleted_cols"])) * urows

      ra_counts = self.struct_counts(urows, ucols, "row", "add")
      rd_counts = self.struct_counts(urows, ucols, "row", "del")
      r_ccounts = self.content_counts_percell()
      r_no_counts = self.nochange_rows_counts(ucols, urows)
      row_counts = Counts(r_ccounts, ra_counts, rd_counts, r_no_counts)

      ra_ratio = self.struct_ratio(urows, ucols, "row", "add", row_counts.a_counts)
      rd_ratio = self.struct_ratio(urows, ucols, "row", "del", row_counts.d_counts)
      r_cratio = self.content_ratio_percell(r_union_cells, row_counts.c_counts)
      r_no_ratio = self.nochange_rows_ratio(ucols, urows, row_counts.no_counts)
      row_ratio = Ratios(r_cratio, ra_ratio, rd_ratio, r_no_ratio)

      # COLUMNS

      # TODO check if the attribute is there
      c_union_cells = (urows - len(self.structure["added_rows"]) - len(self.structure["deleted_rows"])) * ucols

      ca_counts = self.struct_counts(urows, ucols, "col", "add")
      cd_counts = self.struct_counts(urows, ucols, "col", "del")
      c_ccounts = self.content_counts_percell()
      c_no_counts = self.nochange_cols_counts(ucols, urows)
      col_counts = Counts(c_ccounts, ca_counts, cd_counts, c_no_counts)

      ca_ratio = self.struct_ratio(urows, ucols, "col", "add", col_counts.a_counts)
      cd_ratio = self.struct_ratio(urows, ucols, "col", "del", col_counts.d_counts)
      c_cratio = self.content_ratio_percell(c_union_cells, col_counts.c_counts)
      c_no_ratio = self.nochange_cols_ratio(ucols, urows, col_counts.no_counts)
      col_ratio = Ratios(c_cratio, ca_ratio, cd_ratio, c_no_ratio)

      return RowsAndCols(RatiosAndCounts(row_ratio, row_counts), RatiosAndCounts(col_ratio, col_counts))


class Ratios:
  """
  Relative number of changes (aka ratios)
  """
  def __init__(self, cr=0.0, ar=0.0, dr=0.0, no=100.0, rr=0.0, mr=0.0):
    self.c_ratio = cr
    self.a_ratio = ar
    self.d_ratio = dr
    self.no_ratio = no
    self.r_ratio = rr
    self.m_ratio = mr

  def serialize(self):
    return {
        "c_ratio": self.c_ratio,
        "a_ratio": self.a_ratio,
        "d_ratio": self.d_ratio,
        "no_ratio": self.no_ratio,
        "r_ratio": self.r_ratio,
        "m_ratio": self.m_ratio
    }


class Counts:
  """
  Absolute number of changes (aka counts)
  """
  def __init__(self, cc=0.0, ac=0.0, dc=0.0, no=100.0, rc=0.0, mc=0.0):
    self.c_counts = cc
    self.a_counts = ac
    self.d_counts = dc
    self.no_counts = no
    self.r_counts = rc
    self.m_counts = mc

  def serialize(self):
    return {
        "c_counts": self.c_counts,
        "a_counts": self.a_counts,
        "d_counts": self.d_counts,
        "no_counts": self.no_counts,
        "r_counts": self.r_counts,
        "m_counts": self.m_counts
    }


class RatiosAndCounts:
  def __init__(self, ratios, counts):
    self.ratios = ratios
    self.counts = counts

  def serialize(self):
    return {
        "ratios": self.ratios.serialize(),
        "counts": self.counts.serialize()
    }


class RowsAndCols:
  def __init__(self, rows, cols):
    self.rows = rows
    self.cols = cols

  def serialize(self):
    return {
        "rows": self.rows.serialize(),
        "cols": self.cols.serialize()
    }


# DiffFinder class
class DiffFinder:
  # todo add the operations?
  def __init__(self, t1, t2, rowtype, coltype, direction):
    self._table1 = t1
    self._table2 = t2
    self._direction = int(direction)
    self.diff = Diff(direction=self._direction)
    self.union = {}
    self.intersection = {}  # we only need this for rows when we have content changes
    self.intersection["ic_ids"] = get_intersection(self._table1.col_ids, self._table2.col_ids.astype(str))
    if self.intersection["ic_ids"].shape[0] > 0:
      # there's at least one common column between the tables
      # otherwise there's no need to calculate the unions
      # for now drop the if about directions because we need the unions for showing the details level and for calculating the content changes :|
      # todo reuse the these conditions when we know when we really need them
      # if self._direction == D_COLS or self._direction == D_ROWS_COLS:
      # generate the union columns
      self.union["uc_ids"] = get_union_ids(self._table1.col_ids, self._table2.col_ids)
      c_ids = assign_ids(self.union["uc_ids"], coltype)
      # use tolist() to solve the json serializable problem
      self.union["c_ids"] = c_ids.tolist()
      # if self._direction == D_ROWS or self._direction == D_ROWS_COLS:
      # generate the union rows
      self.union["ur_ids"] = get_union_ids(self._table1.row_ids, self._table2.row_ids)
      r_ids = assign_ids(self.union["ur_ids"], rowtype)
      self.union["r_ids"] = r_ids.tolist()

  def generate_diff(self, ops):
    if len(self.union) == 0:
      # todo return a special value
      # there's no diff possible
      return {}
    operations = ops.split(",")
    has_merge = "merge" in operations
    # has_reorder = "reorder" in operations
    has_structure = "structure" in operations
    has_content = "content" in operations
    if self._direction == D_COLS or self._direction == D_ROWS_COLS:
      if has_structure or has_merge:
        # t1 = timeit.default_timer()
        self._compare_ids("col", self._table1.col_ids, self._table2.col_ids, self.union["uc_ids"], has_merge,
                          has_structure)
        # t2 = timeit.default_timer()
        # todo check for reorder for cols here
    if self._direction == D_ROWS or self._direction == D_ROWS_COLS:
      if has_structure or has_merge:
        # t3 = timeit.default_timer()
        self._compare_ids("row", self._table1.row_ids, self._table2.row_ids, self.union["ur_ids"], has_merge,
                          has_structure)

        # todo check for reorder for rows here
    # check for content change
    # todo move this to be before checking for other changes so that we can aggregate if necessary?
    if has_content:
      # todo do we need both rows and columns here anyway?
      # first calculate the rows intersections
      self.intersection["ir_ids"] = get_intersection(self._table1.row_ids, self._table2.row_ids)
      # now we have both intersections for rows and columns
      # t7 = timeit.default_timer()
      self._compare_values()
      # t8 = timeit.default_timer()
      # print("content: ", t8 - t7)
      # todo check this here
      # ch_perc = calc_ch_percentage(len(self.diff.content), len(self.intersection["ir_ids"]), len(self.intersection["ic_ids"]))
    return self.diff

  # compares two lists of ids
  # todo consider sorting
  def _compare_ids(self, e_type, ids1, ids2, u_ids, has_merge, has_structure, merge_delimiter="+"):
    deleted = get_deleted_ids(ids1, ids2)
    deleted_log = []
    added_log = []
    # TODO use this only for merge operations :|
    merged_log = []
    split_log = []
    to_filter = []
    merge_id = 0
    for i in deleted:
      # check for a + for a split operation
      if str(i).find(merge_delimiter) == -1:
        # no delimiter found
        if i in u_ids:
          pos = np.where(u_ids == i)[0][0]
          deleted_log += [{"id": i, "pos": pos}]
      else:
        # split found
        split_log += [{"id": str(i), "pos": np.where(u_ids == i)[0][0], "split_id": merge_id, "is_added": False}]
        split_ids = str(i).split(merge_delimiter)
        to_filter += split_ids  # will be filtered in next step
        for s in split_ids:
          split_log += [{"id": s, "pos": np.where(u_ids == s)[0][0], "split_id": merge_id, "is_added": True}]
        merge_id += 1  # increment it
    for j in get_added_ids(ids1, ids2):
      # check for a + for merge operations!
      if str(j).find(merge_delimiter) == -1:
        # no delimiter found
        if j not in to_filter:
          apos = np.where(u_ids == j)[0][0]
          added_log += [{"id": j, "pos": apos}]
          # else:
          #   print("this should not be logged because it's part of a split", j)
      else:
        # merge found
        merged_log += [{"id": str(j), "pos": np.where(u_ids == j)[0][0], "merge_id": merge_id, "is_added": True}]
        merged_ids = str(j).split(merge_delimiter)
        for s in merged_ids:
          # delete the delete operations related to those IDs
          deleted_log = [obj for obj in deleted_log if obj['id'] != s]
          merged_log += [{"id": s, "pos": np.where(u_ids == s)[0][0], "merge_id": merge_id, "is_added": False}]
        merge_id += 1  # increment it
    # log
    if has_merge:
      self.diff.merge["merged_" + e_type + "s"] = merged_log
      self.diff.merge["split_" + e_type + "s"] = split_log
    if has_structure:
      self.diff.structure["added_" + e_type + "s"] = added_log
      self.diff.structure["deleted_" + e_type + "s"] = deleted_log

  # content changes
  """
  def _compare_values1(self):
    for i in self.intersection["ir_ids"]:
      r1 = np.where(self._table1.row_ids == i)[0][0]
      r2 = np.where(self._table2.row_ids == i)[0][0]
      for j in self.intersection["ic_ids"]:
        c1 = np.where(self._table1.col_ids == j)[0][0]
        c2 = np.where(self._table2.col_ids == j)[0][0]
        # cell_diff = full_table1.content[r1,c1] - full_table2.content[r2,c2]
        # doesn't work like this because it's a string
        if self._table1.content[r1, c1] != self._table2.content[r2, c2]:
          # todo find a diff for different datatypes!
          cell_diff = float(self._table1.content[r1, c1]) - float(self._table2.content[r2, c2])
          rpos = np.where(self.union["ur_ids"] == i)[0][0]
          cpos = np.where(self.union["uc_ids"] == j)[0][0]
          self.diff.content += [{"row": str(i), "col": str(j), "diff_data": cell_diff, "rpos": rpos, "cpos": cpos}]
          # return diff_arrays
  """

  # @disordered is an array of the IDs that are available in x and not in the matching position in y (or not available at all)
  # in case x and y are a result of the intersection then disordered is the list of disordered IDs in x
  def _find_reorder(self, ids1, ids2, x, y, disordered, direction):
    import numpy
    # todo this should be as the size of the original ids not just the intesection ids
    # x shape or y shape should be the same
    # or the shape of the IDs in the second table (original y)
    indices = np.arange(x.shape[0])
    reordered = []
    for i in disordered:
      # todo check this with more than 2 changes
      if isinstance(i, numpy.ndarray):
        i = i[0]
      try:
        pos_table1 = np.where(ids1 == i)[0][0]
        pos_table2 = np.where(ids2 == i)[0][0]
      except IndexError:
        print('index error')
      # todo substitute this with the new one!
      reordered.append({'id': i, 'from': pos_table1, 'to': pos_table2, 'diff': pos_table2 - pos_table1})

      old = np.where(x == i)[0][0]
      new = np.where(y == i)[0][0]
      np.put(indices, old, new)
      # index = []
      # for i in x:
      #     if i != y[np.where(x == i)[0][0]]:
      #         index += [np.where(y == i)[0][0]]
      #     else:
      #         index += [np.where(x == i)[0][0]]
    self._reorder_to_json(direction, reordered)
    return indices

  def _compare_values(self):
    # todo remove the intersection assignment
    # get the intersection of rows as numpy
    r_inter = self.intersection["ir_ids"]
    # get the intersection of cols as numpy
    c_inter = self.intersection["ic_ids"]
    # create a boolean array that represents where the intersection values are available in the first table
    r_bo1 = np.in1d(self._table1.row_ids, r_inter)
    # create a boolean array for where the intersection is in the second table (rows)
    r_bo2 = np.in1d(self._table2.row_ids, r_inter)
    # the same for columns
    # create a boolean array that represents where the intersection values are available in the first table
    c_bo1 = np.in1d(self._table1.col_ids, c_inter)
    # create a boolean array for where the intersection is in the second table (cols)
    c_bo2 = np.in1d(self._table2.col_ids, c_inter)
    #####
    # ru_bo = np.in1d(self.union["ur_ids"], r_inter)
    rids1 = self._table1.row_ids[r_bo1]
    rids2 = self._table2.row_ids[r_bo2]
    rdis = rids1[rids1 != rids2]
    # ruids = self.union["ur_ids"][ru_bo]
    # diff_order = np.where(rids2 != rids1)
    # ri = np.argsort(r_inter)
    # condition = diff_order[0].shape[0] > 0
    #####
    # slicing work to get the intersection tables
    inter1 = np.asmatrix(self._table1.content)[:, c_bo1][r_bo1, :]
    inter2 = np.asmatrix(self._table2.content)[:, c_bo2][r_bo2, :]
    if (rdis.shape[0] > 0):
      # todo do this in one step
      r_indices = self._find_reorder(self._table2.row_ids, self._table1.row_ids, rids1, rids2, rdis, 'rows')
      inter2 = inter2[r_indices, :]
    # for columns
    cids1 = self._table1.col_ids[c_bo1]
    cids2 = self._table2.col_ids[c_bo2]
    try:
      cdis = cids1[cids1 != cids2]
    except ValueError:
      # fixing an ungly bug when there are NO  unique ids!
      # ## warning! bug ###
      # this happens when one of the tables does NOT have unique ids and the sizes are different... couldn't fix
      print(("Oops! it seems that sizes are not matching", cids1.shape[0], cids2.shape[0]))
      set_boolean = (np.array(list(set(cids1))) != np.array(list(set(cids2))))
      cdis = cids1[set_boolean]
      # ignore and leave
      self._content_to_json(None)
      return
    # if there's a disorder in the columns
    if (cdis.shape[0] > 0):
      c_indices = self._find_reorder(self._table2.col_ids, self._table1.col_ids, cids1, cids2, cdis, 'cols')
      inter2 = inter2[:, c_indices]
    # at this point inter2 should look good hopefully!
    # diff work
    diff = inter2.astype('float') - inter1.astype('float')
    # done :)
    # normalization
    normalized_diff = normalize_float_11(diff)
    # create a serialized thing for the log
    before = timeit.default_timer()
    self._content_to_json(normalized_diff)
    after = timeit.default_timer()
    _log.debug("TIMER: logging", after - before)

  def _reorder_to_json(self, direction, disorder):
    self.diff.reorder[direction] = disorder

  def _content_to_json(self, diff):
    # check if the diff is None (the case of all 0s diff)
    if diff is None:
      return
    # find the position of the intersection things in union ids
    # assuming that we have the same order of the intersection!
    r_bo_inter_u = np.in1d(self.union["ur_ids"], self.intersection["ir_ids"])
    c_bo_inter_u = np.in1d(self.union["uc_ids"], self.intersection["ic_ids"])
    r_indices = np.arange(self.union["ur_ids"].shape[0])[r_bo_inter_u]
    c_indices = np.arange(self.union["uc_ids"].shape[0])[c_bo_inter_u]
    ru = self.union["ur_ids"][r_indices]
    cu = self.union["uc_ids"][c_indices]
    for (i, j), value in np.ndenumerate(diff):
      # todo if the normalization gives results between [0,1] this should change as it considers values between [-1,1]
      if value != 0:
        self.diff.content += [{"row": ru[i], "col": cu[j],
                               # todo to get the original change value we can pass the original diff matrix then get the element m.item((i,j))
                               "diff_data": float(value),
                               "rpos": r_indices[i], "cpos": c_indices[j]}]
        # other idea could be
        # doing something like res = np.where(m!=0) //not in the case of normalization
        # the res is 2 matrices
        # res[0] is the indices of the rows (where the values are != 0)
        # res[1] is the indices of the cols
        # res[1].item(0,0)
        # to access the value it would be m[res[0].item(0,0), res[1].item(0,0)] (the 0,0 would be i,j)
        # np.apply_along_axis(myfunc, 0, res)
        # array([['x is [0 2]', 'x is [1 1]', 'x is [2 5]']], dtype='|S10') --> these are the i,j of where i have changes, i can just wrap them and send them

# todo might be an idea to find the merged things first then handle the rest separately
