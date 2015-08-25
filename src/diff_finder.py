#!/usr/bin/python
__author__ = 'Reem'

import numpy as np
import logger as log
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

#reads a csv file (using full file path) and returns the data table with the IDs
#todo to make more general (to read other data samples)
def get_full_table(file):
    #data = np.genfromtxt(file, dtype=None, delimiter=',', names=True)
    data = np.genfromtxt(file, dtype=np.string_, delimiter=',')
    row_ids = data[1:][:,0]
    col_ids = data[0,:][1:]
    table = data[1:,1:]
    return {'table': table , 'col_ids': col_ids, 'row_ids': row_ids}

def get_deleted_ids(ids1, ids2):
    return list(set(ids1) - set(ids2))

def get_added_ids(ids1, ids2):
    return list(set(ids2) - set(ids1))

def get_intersection(ids1, ids2):
    return set(ids1).intersection(ids2)

#compares two lists and logs the diff
#todo consider sorting or merge
def compare_ids(ids1, ids2, u_ids, type):
    merge_delimiter = "+"
    merge_found = False
    deleted = get_deleted_ids(ids1, ids2)
    to_log = []
    to_not_log = []
    #todo is to check for the split here
    for i in deleted:
        if i in u_ids:
            pos = np.where(u_ids == i)[0][0] #todo fix the bug here! index out of bound
        else:
            print("This should not happen!", u_ids, i)
            pos = 20
        to_log += [{"op": "delete", "id": i, "pos": pos}]
    for j in get_added_ids(ids1, ids2):
        #check for a + for merge operations!
        if str(j).find(merge_delimiter) == -1:
            apos = np.where(u_ids == j)[0][0]
            to_log += [{"op": "add", "id": j, "pos": apos}]
        else:
            merged_ids = str(j).split(merge_delimiter)
            pos = str(np.where(u_ids == j)[0][0])
            all_ids = str(j)
            for s in merged_ids:
                pos += "," + str(np.where(u_ids == s)[0][0])
                all_ids += "," + s
                # #todo find a better way to delete this!!!
                # to_not_log = [whatever for whatever, val in enumerate(to_log) if whatever["id"] == s]
                # for index in reversed(to_not_log): # start at the end to avoid recomputing offsets
                #     del to_log[index]
            to_log += [{"op": "merge", "id": all_ids, "pos": pos}]
            #todo delete the others from the deleted to_log
    for m in to_log:
        log.message(m["op"], type, m["id"], m["pos"])


def compare_values(full_table1, full_table2, ru_ids, cu_ids):
    rows = get_intersection(full_table1['row_ids'], full_table2['row_ids'])
    cols = get_intersection(full_table1['col_ids'], full_table2['col_ids'])
    for i in rows:
        r1 = np.where(full_table1['row_ids'] == i)[0][0]
        r2 = np.where(full_table2['row_ids'] == i)[0][0]
        for j in cols:
            c1 = np.where(full_table1['col_ids'] == j)[0][0]
            c2 = np.where(full_table2['col_ids'] == j)[0][0]
            # cell_diff = full_table1['table'][r1,c1] - full_table2['table'][r2,c2]
            # doesn't work like this because it's a string
            if full_table1['table'][r1,c1] != full_table2['table'][r2,c2]:
                #todo find a diff for different datatypes!
                cell_diff = float(full_table1['table'][r1,c1]) - float(full_table2['table'][r2,c2])
                rpos = np.where(ru_ids == i)[0][0]
                cpos = np.where(cu_ids == j)[0][0]
                log.message("change", "cell", str(i)+','+str(j), str(rpos)+','+str(cpos), cell_diff)
                #print('no match ', full_table1['table'][r1,c1], full_table2['table'][r2,c2], r1 ,c1 ,  i, j)


def union_ids(ids1, ids2):
    if len(ids1) < len(ids2):
        first = ids1
        second = ids2
    else:
        first = ids2
        second = ids1
    u = second
    print(first, second)
    #to solve expected problems when the length of the ids in one array is more than the others (strings)
    #todo solve the error here ValueError: new type not compatible with array.
    if(u.dtype.itemsize < first.dtype.itemsize):
        u.astype(first.dtype)
    else:
        print("there's nothingn to change")

    print("u is ", u)
    deleted = get_deleted_ids(first, second)
    for i in deleted:
        index1 = np.where(first == i)[0][0]
        if index1 == 0:
            #it's deleted from the first position
            #add it at position index1
            u[index1:0] = i
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


def generate_diff_from_files(file1, file2, diff_log):
    full_table1 = get_full_table(file1)
    #print(full_table1['table'])
    full_table2 = get_full_table(file2)
    #print(full_table2['table'])
    return generate_diff(full_table1, full_table2, diff_log)


# testing
def generate_diff(full_table1, full_table2, diff_log):

    if len(get_intersection(full_table1['col_ids'], full_table2['col_ids'])) == 0:
        #there's no ids in common within the two compared tables
        return False

    #todo move this to the api
    log_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), data_directory + diff_log))
    log.init_log(log_filename)
    print("log filename ", log_filename)

    uc_ids = union_ids(full_table1['col_ids'], full_table2['col_ids'])
    ur_ids = union_ids(full_table1['row_ids'], full_table2['row_ids'])

    compare_ids(full_table1['col_ids'], full_table2['col_ids'], uc_ids, "column")
    compare_ids(full_table1['row_ids'], full_table2['row_ids'], ur_ids, "row")

    compare_values(full_table1, full_table2, ur_ids, uc_ids)

    log.close()
    return True

#print(generate_diff_from_files(in_file_name, out_file_name, log_file))
#file1= "C:\\Users\\Reem\\Repository\\caleydo_web_container\\plugins\\demo_app\\data\\test_10x100.csv"
#file2= "C:\\Users\\Reem\\Repository\\caleydo_web_container\\plugins\\demo_app\\data\\test_100x10.csv"
#print(generate_diff_from_files(file2, file1, log_file + "gene"))

#todo should the result be the log or the union array with notation of difference (which is added or removed)?
#todo might be an idea to find the merged things first then handle the rest separately
#todo think of the split