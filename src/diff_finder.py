#!/usr/bin/python
__author__ = 'Reem'

import numpy as np
import json
import os
# import sys
#
# print 'Number of arguments:', len(sys.argv), 'arguments.'
# print 'Argument List:', str(sys.argv)

data_directory = '../data/'
file_name = 'tiny_table1'
in_file_name = data_directory + file_name + '_in.csv'
out_file_name = data_directory + file_name + '_out.csv'
log_file = data_directory + file_name + '_diff.log'

# reads a csv file (using full file path) and returns the data table with the IDs
#todo to make more general (to read other data samples)
def get_full_table(file):
    #data = np.genfromtxt(file, dtype=None, delimiter=',', names=True)
    data = np.genfromtxt(file, dtype=np.string_, delimiter=',')
    row_ids = data[1:][:, 0]
    col_ids = data[0, :][1:]
    table = data[1:, 1:]
    return {'table': table, 'col_ids': col_ids, 'row_ids': row_ids}


# get the IDs available only in the first one
def get_deleted_ids(ids1, ids2):
    return list(set(ids1) - set(ids2))


# get the IDs available only in the second one
def get_added_ids(ids1, ids2):
    return list(set(ids2) - set(ids1))


def get_intersection(ids1, ids2):
    return set(ids1).intersection(ids2)


def get_union_ids(ids1, ids2):
    if len(ids1) < len(ids2):
        first = ids1
        second = ids2
    else:
        first = ids2
        second = ids1
    u = list(second)
    deleted = get_deleted_ids(first, second)
    for i in deleted:
        index1 = first.index(i)
        if index1 == 0:
            #it's deleted from the first position
            #add it at position index1
            u.insert(0, i)
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
                    u.insert(0, i)
                    return u
            pre_index = u.index(pre_element)
            #insert the new element after the pre_element
            u.insert(pre_index + 1, i)
            #todo if the index is not available
    return u


#compares two lists and logs the diff
#todo consider sorting
def compare_ids(ids1, ids2, u_ids, e_type, diff_arrays):
    merge_delimiter = "+"
    deleted = get_deleted_ids(ids1, ids2)
    to_filter = []
    deleted_log = []
    added_log = []
    merged_log = []
    split_log = []
    merge_id = 0
    #todo is to check for the split here
    for i in deleted:
        #check for a + for a split operation
        if str(i).find(merge_delimiter) == -1:
            if i in u_ids:
                pos = u_ids.index(i)
            else:
                print("This should not happen!", u_ids, i)
                pos = 20
            deleted_log += [{"id": i, "pos": pos}]
        else:
            #split found
            split_log += [{"id": str(i), "pos": u_ids.index(i), "split_id": merge_id, "is_added": False}]
            split_ids = str(i).split(merge_delimiter)
            to_filter += split_ids  #will be filtered in next step
            for s in split_ids:
                split_log += [{"id": s, "pos": u_ids.index(s), "split_id": merge_id, "is_added": True}]
            merge_id += 1 #increment it
    for j in get_added_ids(ids1, ids2):
        #check for a + for merge operations!
        if str(j).find(merge_delimiter) == -1:
            if j not in to_filter:
                apos = u_ids.index(j)
                added_log += [{"id": j, "pos": apos}]
                #else:
                #   print("this should not be logged because it's part of a split", j)
        else:
            #merge found
            merged_log += [{"id": str(j), "pos": u_ids.index(j), "merge_id": merge_id, "is_added": True}]
            merged_ids = str(j).split(merge_delimiter)
            for s in merged_ids:
                #delete the delete operations related to those IDs
                deleted_log = filter(lambda obj: obj['id'] != s, deleted_log)
                merged_log += [{"id": s, "pos": u_ids.index(s), "merge_id": merge_id, "is_added": False}]
            merge_id += 1 #increment it
    #log
    diff_arrays["merged_" + e_type + "s"] = merged_log
    diff_arrays["split_" + e_type + "s"] = split_log
    diff_arrays["added_" + e_type + "s"] = added_log
    diff_arrays["deleted_" + e_type + "s"] = deleted_log
    return diff_arrays


def compare_values(full_table1, full_table2, ru_ids, cu_ids, diff_arrays):
    rows = get_intersection(full_table1['row_ids'], full_table2['row_ids'])
    cols = get_intersection(full_table1['col_ids'], full_table2['col_ids'])
    for i in rows:
        r1 = full_table1['row_ids'].index(i)
        r2 = full_table2['row_ids'].index(i)
        for j in cols:
            c1 = full_table1['col_ids'].index(j)
            c2 = full_table2['col_ids'].index(j)
            # cell_diff = full_table1['table'][r1,c1] - full_table2['table'][r2,c2]
            # doesn't work like this because it's a string
            if full_table1['table'][r1, c1] != full_table2['table'][r2, c2]:
                #todo find a diff for different datatypes!
                cell_diff = float(full_table1['table'][r1, c1]) - float(full_table2['table'][r2, c2])
                rpos = ru_ids.index(i)
                cpos = cu_ids.index(j)
                diff_arrays["ch_cells"] += [{"row": str(i), "col": str(j), "diff_data": cell_diff, "rpos": rpos, "cpos": cpos}]
    return diff_arrays


def generate_diff_from_files(file1, file2):
    full_table1 = get_full_table(file1)
    #print(full_table1['table'])
    full_table2 = get_full_table(file2)
    #print(full_table2['table'])
    return generate_diff(full_table1, full_table2, None, None)


# testing
def generate_diff(full_table1, full_table2, rowtype, coltype):
    print("sizes", len(full_table1['col_ids']), len(full_table2['col_ids']), len(full_table1['row_ids']), len(full_table2['row_ids']), full_table1['table'].shape, full_table2['table'].shape)

    if len(get_intersection(full_table1['col_ids'], full_table2['col_ids'])) == 0:
        #there's no ids in common within the two compared tables
        #todo handle this
        return {}

    diff_arrays = {
        "added_rows": [],
        "deleted_rows": [],
        "added_cols": [],
        "deleted_cols": [],
        "merged_rows": [],
        "split_rows": [],
        "merged_cols": [],
        "split_cols": [],
        "ch_cells": [],
        "union": {}
    }

    uc_ids = get_union_ids(full_table1['col_ids'], full_table2['col_ids'])
    ur_ids = get_union_ids(full_table1['row_ids'], full_table2['row_ids'])

    diff_arrays = compare_ids(full_table1['col_ids'], full_table2['col_ids'], uc_ids, "col", diff_arrays)
    diff_arrays = compare_ids(full_table1['row_ids'], full_table2['row_ids'], ur_ids, "row", diff_arrays)

    diff_arrays = compare_values(full_table1, full_table2, ur_ids, uc_ids, diff_arrays)
    c_ids = assign_ids(uc_ids, coltype)
    r_ids = assign_ids(ur_ids, rowtype)
    #use tolist() to solve the json serializable problem
    diff_arrays["union"] = {"uc_ids": uc_ids, "ur_ids": ur_ids, "c_ids": c_ids.tolist(), "r_ids": r_ids.tolist()}

    return diff_arrays


#helping functions
def assign_ids(ids, idtype):
    import caleydo_server.plugin

    manager = caleydo_server.plugin.lookup('idmanager')
    return np.array(manager(ids, idtype))
#print(json.dumps(generate_diff_from_files(in_file_name, out_file_name)))
#print(generate_diff_from_files(data_directory + 'test_table_in.csv', data_directory + 'test_table_out.csv'))
#file1= "C:\\Users\\Reem\\Repository\\caleydo_web_container\\plugins\\demo_app\\data\\test_10x100.csv"
#file2= "C:\\Users\\Reem\\Repository\\caleydo_web_container\\plugins\\demo_app\\data\\test_100x10.csv"
#print(generate_diff_from_files(file2, file1))

#todo should the result be the log or the union array with notation of difference (which is added or removed)?
#todo might be an idea to find the merged things first then handle the rest separately