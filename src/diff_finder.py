#!/usr/bin/python
__author__ = 'Reem'

import numpy as np
import timeit
from enum import Enum
from math import floor

D_ROWS = 0
D_COLS = 1
D_ROWS_COLS = 2


class Levels(Enum):
    detail = 4
    middle = 2
    overview = 0


# reads a csv file (using full file path) and returns the data table with the IDs
def get_full_table(file):
    #data = np.genfromtxt(file, dtype=None, delimiter=',', names=True)
    data = np.genfromtxt(file, dtype=np.string_, delimiter=',')
    row_ids = data[1:][:, 0]
    col_ids = data[0, :][1:]
    table = data[1:, 1:]
    return Table(row_ids, col_ids, table)


### Helper functions ###

# get the IDs available only in the first one
def get_deleted_ids(ids1, ids2):
    #might want to use this instead for numpy arrays http://docs.scipy.org/doc/numpy/reference/generated/numpy.setdiff1d.html
    return list(set(ids1) - set(ids2))


# get the IDs available only in the second one
def get_added_ids(ids1, ids2):
    return list(set(ids2) - set(ids1))


def get_intersection(ids1, ids2):
    #return np.array(list(set(ids1).intersection(ids2)))
    return np.intersect1d(ids1,ids2)


def get_union_ids(ids1, ids2):
    if ids1.shape[0] < ids2.shape[0]:
        first = ids1
        second = ids2
    else:
        first = ids2
        second = ids1
    if (second.dtype.itemsize < first.dtype.itemsize):
        itemsize = first.dtype.itemsize
    else:
        itemsize = second.dtype.itemsize
    u = np.array(second, dtype="S"+str(itemsize))
    #u = list(second)
    deleted = get_deleted_ids(first, second)
    for i in deleted:
        index1 = np.where(first == i)[0][0]
        if index1 == 0:
            #it's deleted from the first position
            #add it at position index1
            u = np.insert(u, 0, i)
        else:
            #it's somewhere in the middle, find the position of the one before
            index1 -= 1
            pre_element = first[index1]
            while pre_element not in u:
                index1 -= 1
                if index1 >= 0:
                    pre_element = first[index1]
                else:
                    print("ERROR: there's no element before that exists in the list then just add it at 0!")
                    u = np.insert(u, 0, i)
                    return u
            pre_index = np.where(u == pre_element)[0][0]
            #insert the new element after the pre_element
            u = np.insert(u, pre_index + 1, i)
            #todo if the index is not available
    return u


#this returns values between [0,1]
def normalize_float01(diff_matrix):
    min = diff_matrix.min()
    max = diff_matrix.max()
    #notice float(1)/2 * m gives a float result better than m/2
    #x = (x - min) / (max - min)
    normalized = (diff_matrix - min) * (float(1)/(max - min))
    return normalized


#this returns values between [-1,1]
def normalize_float_11(diff_matrix):
    min = diff_matrix.min()
    max = diff_matrix.max()
    max = abs(min) if abs(min) > abs(max) else abs(max)
    #notice float(1)/2 * m gives a float result better than m/2
    if max > 0:
        normalized = diff_matrix * (float(1)/max)
        return normalized
    return None

#helping functions from caleydo
def assign_ids(ids, idtype):
    import caleydo_server.plugin

    manager = caleydo_server.plugin.lookup('idmanager')
    return np.array(manager(ids, idtype))


#calcuate the percentage of changed cells regarding the intersection table
def calc_ch_percentage(chc, rc, cc):
    return float(chc)/(rc * cc)


def generate_diff_from_files(file1, file2):
    full_table1 = get_full_table(file1)
    full_table2 = get_full_table(file2)
    #todo use the classes
    #return generate_diff(full_table1, full_table2, None, None, 2)


def dimensionStats(content, selector):
    hist = []
    for e in content:
        sel = selector(e)
        #result = $.grep(hist, function(e){ return e.id == sel.row; });
        result = filter(lambda h: h["id"] == sel["row"], hist)
        if len(result) == 0:
            hist += [{
              "id" : sel["row"],
              "count": 1,
              "pos": sel["rpos"]
            }]
        else:
            result[0]["count"] += 1

    return hist

def rowSelector(entry):
    return {
      "row": entry.row,
      "rpos": entry.rpos
      # "ur_ids" : entry.union['ur_ids'],
      # "uc_ids" : entry.union['uc_ids']
    }

def colSelector(entry):
    return {
        "row": entry.col,
        "rpos": entry.cpos
        # "ur_ids" : entry.union['ur_ids'],
        # "uc_ids" : entry.union['uc_ids']
    }


#Table data structure
class Table:
    def __init__(self, rows, cols, content):
        self.row_ids = np.asarray(rows, np.string_)
        self.col_ids = np.asarray(cols, np.string_)
        self.content = content


#Diff object data structure
class Diff:
    def __init__(self, content=None, structure=None, merge=None, reorder=None, union=None, direction=D_ROWS_COLS):
        self._direction = direction
        self.content = [] if content is None else content
        self.structure = {} if structure is None else structure
        self.merge = {} if merge is None else merge
        self.reorder = {} if reorder is None else reorder
        self.union = {} if union is None else union

    #todo decide if the union should be here or in the diff finder
    def add_union(self, union):
        self.union = {}
        self.union["uc_ids"] = union["uc_ids"].tolist()
        self.union["c_ids"] = union["c_ids"]
        self.union["ur_ids"] = union["ur_ids"].tolist()
        self.union["r_ids"]= union["r_ids"]

    def serialize(self):
        return {
            "content" : self.content,
            "structure": self.structure,
            "merge": self.merge,
            "reorder": self.reorder,
            "union": self.union
        }

    def content_ratio_percell(self, ucells):
        return float(len(self.content)) / ucells

    # rowAdd rowDel colAdd colDel
    def struct_ratio(self, urows, ucols, dir, st_op):
        operation = st_op + "eted" if st_op == "del" else st_op + "ed"
        rows = urows if dir == "row" else ucols
        return float(len(self.structure[operation + "_" + dir + "s"])) / rows

    def struct_add_ratio(self, width, height):
        cells = width * height
        addc = 0
        h = height
        w = width
        if self.structure.has_key("deleted_rows"):
            h -= len(self.structure["deleted_rows"])
        if self.structure.has_key("deleted_cols"):
            w -= len(self.structure["deleted_cols"])
        if self.structure.has_key("added_rows"):
            addc += len(self.structure["added_rows"]) * w
            h -= len(self.structure["added_rows"])
        if self.structure.has_key("added_cols"):
            addc += len(self.structure["added_cols"]) * h
            w -= len(self.structure["added_cols"]) # we might need this later!
        # the type here should be just add but i'm using row-add for css
        return float(addc)/cells

    def struct_del_ratio(self, width, height):
        cells = width * height
        h = height
        w = width
        delc = 0
        if self.structure.has_key("deleted_rows"):
            delc += len(self.structure["deleted_rows"]) * w
            h -= len(self.structure["deleted_rows"])
        if self.structure.has_key("deleted_cols"):
            delc += len(self.structure["deleted_cols"]) * h
        #the type here should be just add and del but i'm using row-add and row-del for css
        return float(delc)/cells

    def nochange_ratio(self, width, height):
        cells = width * height
        h = height
        w = width
        #the height without the removed or added rows
        if self.structure.has_key("deleted_rows"):
            h -= len(self.structure["deleted_rows"])
        if self.structure.has_key("added_rows"):
            h -= len(self.structure["added_rows"])
        #the width without the deleted or removed cols
        if self.structure.has_key("deleted_cols"):
            w -= len(self.structure["deleted_cols"])
        if self.structure.has_key("added_cols"):
            w -= len(self.structure["added_cols"])
        #the rest cells without the changed ones
        noc = (h * w) - len(self.content)
        return float(noc) / cells

    def nochange_rows_ratio(self, width, height):
        cells = width * height
        h = height
        w = width
        #the width without the deleted or removed cols
        if self.structure.has_key("deleted_cols"):
            w -= len(self.structure["deleted_cols"])
        if self.structure.has_key("added_cols"):
            w -= len(self.structure["added_cols"])
        cells = w * h
        #the height without the removed or added rows
        if self.structure.has_key("deleted_rows"):
            h -= len(self.structure["deleted_rows"])
        if self.structure.has_key("added_rows"):
            h -= len(self.structure["added_rows"])
        #the rest cells without the changed ones
        noc = (h * w) - len(self.content)
        return float(noc) / cells

    def nochange_cols_ratio(self, width, height):
        h = height
        w = width
        #the height without the removed or added rows
        if self.structure.has_key("deleted_rows"):
            h -= len(self.structure["deleted_rows"])
        if self.structure.has_key("added_rows"):
            h -= len(self.structure["added_rows"])
        cells = w * h
        #the width without the deleted or removed cols
        if self.structure.has_key("deleted_cols"):
            w -= len(self.structure["deleted_cols"])
        if self.structure.has_key("added_cols"):
            w -= len(self.structure["added_cols"])
        #the rest cells without the changed ones
        noc = (h * w) - len(self.content)
        return float(noc) / cells

    def aggregate(self, bins):
        if bins == 1:
            # todo do we want to return it as an array of one element?
            # the ratios for line up
            # todo change this and remove the serialize
            return self.ratios(True)
        elif bins == -1:
            # the ratios for the 2d histogram
            return self.ratios(False)
        else:
            union_rows = self.union['ur_ids']
            if self._direction == D_COLS:
                # if it's the cols not the rows then switch
                union_rows = self.union['uc_ids']
                # todo handle the case of both rows and columns
            max_height = len(union_rows)
            # it's the case of histogram or bar plot
            if bins >= max_height:
                # this is the case of bar plot
                # assume that the bins are the max_height
                #for i in union_rows:
                    #dimensionStats(self.content, selector)
                return self.per_entity_ratios()
            else: # bins < max_height:
                # this is the case of histogram
                result = {}
                if self._direction == D_ROWS_COLS or self._direction == D_ROWS:
                    result["rows"] = self.per_bin_ratios(bins, "rows")
                #todo the rows might have different bins number than the cols
                if self._direction == D_ROWS_COLS or self._direction == D_COLS:
                    result["cols"] = self.per_bin_ratios(bins, "cols")
                return result
                #todo change this
                #dimensionStats(self.content, selector)


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
            return [] #this should not happen!
            # todo handle the case of both rows and columns
        ratios_list = []
        length = len(union_rows)
        mod = length % bins
        items = length / bins # by default in python you get the floor
        last_bin = bins - 1
        index = 0
        bins_list = [0] * bins

        # todo handle the error here when there's no row !
        pcontent = [[] for x in xrange(bins)]
        for c in self.content:
            ci = union_rows.index(c[row])
            c_index = ci / items
            if c_index > last_bin:
                c_index = last_bin
            bins_list[c_index] += 1 #we don't add the value changes for now
            pcontent[c_index] += [c]

        # for structure changes
        pstructure = [{"added_" + e_type: [], "deleted_" + e_type: []} for x in xrange(bins)]
        # filter for the structure changes, because once there's a structure change, there's no need to find content #what!!
        for a in self.structure["added_" + e_type]:
            ai = union_rows.index(a['id'])
            a_index = ai / items
            if a_index > last_bin:
                a_index = last_bin
            pstructure[a_index]["added_" + e_type] += [a]
        # find the deleted
        for d in self.structure["deleted_" + e_type]:
            di = union_rows.index(d['id'])
            d_index = di / items
            if d_index > last_bin:
                d_index = last_bin
            pstructure[d_index]["deleted_" + e_type] += [d]

        for i in xrange(bins):
            # 1. Partition
            if i != last_bin:
                temp = union_rows[index:index+items]
                index += items
            else:
                temp = union_rows[index:index+items+mod]
            if dir == D_ROWS:
                punion = {
                    "ur_ids" : temp,
                    "uc_ids" : union_cols,
                }
            else:
                punion = {
                    "ur_ids" : union_cols, # which are union rows
                    "uc_ids" : temp,
                }

            # 2. create the partial diff
            if len(pcontent[i]) == 0:
                pcontent[i] = None
            partial = Diff(content=pcontent[i], structure=pstructure[i], merge=None, reorder=None, union=punion, direction=dir)
            # 3. calcualte the ratio for this part :|
            #todo remove the serialize
            partial_ratio = partial.ratios()
            ratios_list += [{"ratio": partial_ratio.serialize(),
                             "id": temp[0] + '-' + temp[-1], #first and last id
                             "pos": i}]

        return ratios_list

    def per_entity_ratios(self):
        # get a partial diff where every row is a diff
        # 1. Partition
        # get the direction
        union_rows = self.union['ur_ids']
        selector = rowSelector
        e_type = "rows"
        if self._direction == D_COLS:
            # if it's the cols not the rows then switch
            union_rows = self.union['uc_ids']
            # todo handle the case of both rows and columns
            selector = colSelector
            e_type = "cols"
        ratios_list = []
        for i, id in enumerate(union_rows):
            # todo change this in case of columns
            punion = {
                "ur_ids" : [id], #should be a list or might cause troubles :|
                "uc_ids" : self.union['uc_ids']
            }
            pcontent = None
            pstructure = {}
            # filter for the structure changes, because once there's a structure change, there's no need to find content
            # idk why but obj is Diff!
            pstructure["added_rows"] = filter(lambda obj: obj.id == id, self.structure["added_rows"])
            if len(pstructure["added_" + e_type]) != 0:
                # create a ratio where it's only added
                partial_ratio = Ratios(0,1,0,0)
            else:
                # find the deleted
                pstructure["deleted_" + e_type] = filter(lambda obj: obj.id == id, self.structure["deleted_" + e_type])
                if len(pstructure["deleted_" + e_type]) != 0:
                    partial_ratio = Ratios(0,0,1,0)
                else:
                    # find the content
                    # todo
                    #result = filter(lambda h: h["id"] == sel["row"], self.content)
                    pcontent = filter(lambda obj: obj.row == id, self.content)
                    # more resonable in the case of subtable
                    # 2. create the partial diff
                    partial = Diff(content=pcontent, structure=pstructure, merge=None, reorder=None, union=punion, direction=D_ROWS)
                    # 3. calcualte the ratio for this part :|
                    #todo remove the serialize
                    partial_ratio = partial.ratios()
            ratios_list += [{"ratio": partial_ratio.serialize(),
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
            cratio = self.content_ratio_percell(union_cells)
            no_ratio = self.nochange_ratio(ucols, urows)
            sratio_a = self.struct_add_ratio(ucols, urows)
            sratio_d = self.struct_del_ratio(ucols, urows)
            return Ratios(cratio, sratio_a, sratio_d, no_ratio)
        else:
        # Lineup not relevant
            # rows
            ra_ratio = self.struct_ratio(urows, ucols, "row", "add")
            rd_ratio = self.struct_ratio(urows, ucols, "row", "del")
            # calc new union cells as the are less now
            # todo check if the attribute is there
            r_union_cells = (ucols - len(self.structure["added_cols"]) - len(self.structure["deleted_cols"])) * urows
            r_cratio = self.content_ratio_percell(r_union_cells)
            r_no_ratio = self.nochange_rows_ratio(ucols, urows)

            # columns
            ca_ratio = self.struct_ratio(urows, ucols, "col", "add")
            cd_ratio = self.struct_ratio(urows, ucols, "col", "del")
            # todo check if the attribute is there
            c_union_cells = (urows - len(self.structure["added_rows"]) - len(self.structure["deleted_rows"])) * ucols
            c_cratio = self.content_ratio_percell(c_union_cells)
            c_no_ratio = self.nochange_cols_ratio(ucols, urows)
            return {
              "rows": Ratios(r_cratio, ra_ratio, rd_ratio, r_no_ratio),
              "cols": Ratios(c_cratio, ca_ratio, cd_ratio, c_no_ratio)
            }


class Ratios:
    def __init__(self,cr=0.0, ar=0.0, dr=0.0, no=100.0):
        self.c_ratio = cr
        self.a_ratio = ar
        self.d_ratio = dr
        self.no_ratio = no

    def serialize(self):
        return {
            "c_ratio" : self.c_ratio,
            "a_ratio" : self.a_ratio,
            "d_ratio" : self.d_ratio,
            "no_ratio": self.no_ratio
        }

#DiffFinder class
class DiffFinder:
    #todo add the operations?
    def __init__(self, t1, t2, rowtype, coltype, direction):
        self._table1 = t1
        self._table2 = t2
        self._direction = int(direction)
        self.diff = Diff(direction=self._direction)
        self.union = {}
        self.intersection = {} #we only need this for rows when we have content changes
        self.intersection["ic_ids"] = get_intersection(self._table1.col_ids, self._table2.col_ids)
        if self.intersection["ic_ids"].shape[0] > 0:
        #there's at least one common column between the tables
        #otherwise there's no need to calculate the unions
            #for now drop the if about directions because we need the unions for showing the details level and for calculating the content changes :|
            #todo reuse the these conditions when we know when we really need them
            #if self._direction == D_COLS or self._direction == D_ROWS_COLS:
            #generate the union columns
            self.union["uc_ids"] = get_union_ids(self._table1.col_ids, self._table2.col_ids)
            c_ids = assign_ids(self.union["uc_ids"], coltype)
            #use tolist() to solve the json serializable problem
            self.union["c_ids"] = c_ids.tolist()
            #if self._direction == D_ROWS or self._direction == D_ROWS_COLS:
            #generate the union rows
            self.union["ur_ids"] = get_union_ids(self._table1.row_ids, self._table2.row_ids)
            r_ids = assign_ids(self.union["ur_ids"], rowtype)
            self.union["r_ids"]= r_ids.tolist()

    def generate_diff(self, ops):
        if len(self.union) == 0:
            #todo return a special value
            #there's no diff possible
            return {}
        operations = ops.split(",")
        has_merge = "merge" in operations
        has_reorder = "reorder" in operations
        has_structure = "structure" in operations
        has_content = "content" in operations
        if self._direction == D_COLS or self._direction == D_ROWS_COLS:
            if has_structure or has_merge:
                t1 = timeit.default_timer()
                self._compare_ids("col", self._table1.col_ids, self._table2.col_ids, self.union["uc_ids"], has_merge, has_structure)
                t2 = timeit.default_timer()
            #todo check for reorder for cols here
        if self._direction == D_ROWS or self._direction == D_ROWS_COLS:
            if has_structure or has_merge:
                t3 = timeit.default_timer()
                self._compare_ids("row", self._table1.row_ids, self._table2.row_ids, self.union["ur_ids"], has_merge, has_structure)

            #todo check for reorder for rows here
        #check for content change
        #todo move this to be before checking for other changes so that we can aggregate if necessary?
        if has_content:
            #todo do we need both rows and columns here anyway?
            #first calculate the rows intersections
            self.intersection["ir_ids"] = get_intersection(self._table1.row_ids, self._table2.row_ids)
            #now we have both intersections for rows and columns
            t7 = timeit.default_timer()
            self._compare_values()
            t8 = timeit.default_timer()
            #print("content: ", t8 - t7)
            #todo check this here
            #ch_perc = calc_ch_percentage(len(self.diff.content), len(self.intersection["ir_ids"]), len(self.intersection["ic_ids"]))
        return self.diff

    #compares two lists of ids
    #todo consider sorting
    def _compare_ids(self, e_type, ids1, ids2, u_ids, has_merge, has_structure, merge_delimiter="+"):
        deleted = get_deleted_ids(ids1, ids2)
        deleted_log = []
        added_log = []
        #TODO use this only for merge operations :|
        merged_log = []
        split_log = []
        to_filter = []
        merge_id = 0
        for i in deleted:
            #check for a + for a split operation
            if str(i).find(merge_delimiter) == -1:
                #no delimiter found
                if i in u_ids:
                    pos = np.where(u_ids == i)[0][0]
                    deleted_log += [{"id": i, "pos": pos}]
            else:
                #split found
                split_log += [{"id": str(i), "pos": np.where(u_ids == i)[0][0] , "split_id": merge_id, "is_added": False}]
                split_ids = str(i).split(merge_delimiter)
                to_filter += split_ids  #will be filtered in next step
                for s in split_ids:
                    split_log += [{"id": s, "pos": np.where(u_ids == s)[0][0] , "split_id": merge_id, "is_added": True}]
                merge_id += 1 #increment it
        for j in get_added_ids(ids1, ids2):
            #check for a + for merge operations!
            if str(j).find(merge_delimiter) == -1:
                #no delimiter found
                if j not in to_filter:
                    apos = np.where(u_ids == j)[0][0]
                    added_log += [{"id": j, "pos": apos}]
                    #else:
                    #   print("this should not be logged because it's part of a split", j)
            else:
                #merge found
                merged_log += [{"id": str(j), "pos": np.where(u_ids == j)[0][0], "merge_id": merge_id, "is_added": True}]
                merged_ids = str(j).split(merge_delimiter)
                for s in merged_ids:
                    #delete the delete operations related to those IDs
                    deleted_log = filter(lambda obj: obj['id'] != s, deleted_log)
                    merged_log += [{"id": s, "pos": np.where(u_ids == s)[0][0], "merge_id": merge_id, "is_added": False}]
                merge_id += 1 #increment it
        #log
        if has_merge:
            self.diff.merge["merged_" + e_type + "s"] = merged_log
            self.diff.merge["split_" + e_type + "s"] = split_log
        if has_structure:
            self.diff.structure["added_" + e_type + "s"] = added_log
            self.diff.structure["deleted_" + e_type + "s"] = deleted_log

    #content changes
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
                    #todo find a diff for different datatypes!
                    cell_diff = float(self._table1.content[r1, c1]) - float(self._table2.content[r2, c2])
                    rpos = np.where(self.union["ur_ids"] == i)[0][0]
                    cpos = np.where(self.union["uc_ids"] == j)[0][0]
                    self.diff.content += [{"row": str(i), "col": str(j), "diff_data": cell_diff, "rpos": rpos, "cpos": cpos}]
        #return diff_arrays

    #@disordered is an array of the IDs that are available in x and not in the matching position in y (or not available at all)
    #in case x and y are a result of the intersection then disordered is the list of disordered IDs in x
    def _find_reorder(self, x, y, disordered):
        #todo this should be as the size of the original ids not just the intesection ids
        #x shape or y shape should be the same
        #or the shape of the IDs in the second table (original y)
        indices = np.arange(x.shape[0])
        for i in disordered:
            #todo check this with more than 2 changes
            old = np.where(x == i)[0][0]
            new = np.where(y == i)[0][0]
            #todo substitute this with the new one!
            np.put(indices, old, new)
        # index = []
        # for i in x:
        #     if i != y[np.where(x == i)[0][0]]:
        #         index += [np.where(y == i)[0][0]]
        #     else:
        #         index += [np.where(x == i)[0][0]]
        return indices

    def _compare_values(self):
        #todo remove the intersection assignment
        #get the intersection of rows as numpy
        r_inter = self.intersection["ir_ids"]
        #get the intersection of cols as numpy
        c_inter = self.intersection["ic_ids"]
        #create a boolean array that represents where the intersection values are available in the first table
        r_bo1 = np.in1d(self._table1.row_ids, r_inter)
        #create a boolean array for where the intersection is in the second table (rows)
        r_bo2 = np.in1d(self._table2.row_ids, r_inter)
        #the same for columns
        #create a boolean array that represents where the intersection values are available in the first table
        c_bo1 = np.in1d(self._table1.col_ids, c_inter)
        #create a boolean array for where the intersection is in the second table (cols)
        c_bo2 = np.in1d(self._table2.col_ids, c_inter)
        #####
        #ru_bo = np.in1d(self.union["ur_ids"], r_inter)
        rids1 = self._table1.row_ids[r_bo1]
        rids2 = self._table2.row_ids[r_bo2]
        rdis = rids1[rids1 != rids2]
        #ruids = self.union["ur_ids"][ru_bo]
        # diff_order = np.where(rids2 != rids1)
        # ri = np.argsort(r_inter)
        # condition = diff_order[0].shape[0] > 0
        #####
        #slicing work to get the intersection tables
        inter1 = np.asmatrix(self._table1.content)[:, c_bo1][r_bo1, :]
        inter2 = np.asmatrix(self._table2.content)[:, c_bo2][r_bo2, :]
        if (rdis.shape[0]>0):
            #todo do this in one step
            r_indices = self._find_reorder(rids1, rids2, rdis)
            inter2 = inter2[r_indices,:]
        #for columns
        cids1 = self._table1.col_ids[c_bo1]
        cids2 = self._table2.col_ids[c_bo2]
        cdis = cids1[cids1 != cids2]
        #if there's a disorder in the columns
        if (cdis.shape[0]>0):
            c_indices = self._find_reorder(cids1, cids2, cdis)
            inter2 = inter2[:,c_indices]
        #at this point inter2 should look good hopefully!
        #diff work
        diff = inter1 - inter2
        #done :)
        #normalization
        normalized_diff = normalize_float_11(diff)
        #create a serialized thing for the log
        before = timeit.default_timer()
        self._content_to_json(normalized_diff)
        after = timeit.default_timer()
        print("logging", after - before)

    def _content_to_json(self, diff):
        #check if the diff is None (the case of all 0s diff)
        if diff is None:
            return
        #find the position of the intersection things in union ids
        #assuming that we have the same order of the intersection!
        r_bo_inter_u = np.in1d(self.union["ur_ids"], self.intersection["ir_ids"])
        c_bo_inter_u = np.in1d(self.union["uc_ids"], self.intersection["ic_ids"])
        r_indices = np.arange(self.union["ur_ids"].shape[0])[r_bo_inter_u]
        c_indices = np.arange(self.union["uc_ids"].shape[0])[c_bo_inter_u]
        ru = self.union["ur_ids"][r_indices]
        cu = self.union["uc_ids"][c_indices]
        for (i,j), value in np.ndenumerate(diff):
            #todo if the normalization gives results between [0,1] this should change as it considers values between [-1,1]
            if value != 0:
                self.diff.content += [{"row": ru[i], "col": cu[j],
                                       #todo to get the original change value we can pass the original diff matrix then get the element m.item((i,j))
                                       "diff_data": float(value),
                                       "rpos": r_indices[i], "cpos": c_indices[j]}]
        ## other idea could be
        # doing something like res = np.where(m!=0) //not in the case of normalization
        # the res is 2 matrices
        # res[0] is the indices of the rows (where the values are != 0)
        # res[1] is the indices of the cols
        # res[1].item(0,0)
        # to access the value it would be m[res[0].item(0,0), res[1].item(0,0)] (the 0,0 would be i,j)
        # np.apply_along_axis(myfunc, 0, res)
        # array([['x is [0 2]', 'x is [1 1]', 'x is [2 5]']], dtype='|S10') --> these are the i,j of where i have changes, i can just wrap them and send them


#todo might be an idea to find the merged things first then handle the rest separately
