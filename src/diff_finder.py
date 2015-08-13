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
    data = np.genfromtxt(file, dtype=None, delimiter=',')
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
def compare_ids(ids1, ids2, type):
    for i in get_deleted_ids(ids1, ids2):
        log.message("delete", type, i, np.where(ids1 == i)[0][0])
    for j in get_added_ids(ids1, ids2):
        #check for a + for merge operations!
        if str(j).find("+") == -1:
            log.message("add", type, j, np.where(ids2 == j)[0][0])
        else:
            #todo find the index for the merged thing!!
            log.message("merge", type, j, np.where(ids2 == j)[0][0])


def compare_values(full_table1, full_table2):
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
                log.message("change", "cell", str(i)+','+str(j), str(r1)+','+str(c1), cell_diff)
                #print('no match ', full_table1['table'][r1,c1], full_table2['table'][r2,c2], r1 ,c1 ,  i, j)

#testing
def generate_diff_from_files(file1, file2, diff_log):
    full_table1 = get_full_table(file1)
    #print(full_table1['table'])
    full_table2 = get_full_table(file2)
    #print(full_table2['table'])

    #todo move this to the api
    log_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), data_directory + diff_log))
    log.init_log(log_filename)
    print("log filename ", log_filename)

    compare_ids(full_table1['col_ids'], full_table2['col_ids'], "column")
    compare_ids(full_table1['row_ids'], full_table2['row_ids'], "row")

    compare_values(full_table1, full_table2)

    log.close()

    return True

#testing
def generate_diff(full_table1, full_table2, diff_log):

    #todo move this to the api
    log_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), data_directory + diff_log))
    log.init_log(log_filename)
    print("log filename ", log_filename)

    compare_ids(full_table1['col_ids'], full_table2['col_ids'], "column")
    compare_ids(full_table1['row_ids'], full_table2['row_ids'], "row")

    compare_values(full_table1, full_table2)

    log.close()
    return True
#generate_diff_from_files(out_file_name, in_file_name, log_file)

#todo should the result be the log or the union array with notation of difference (which is added or removed)?
#todo might be an idea to find the merged things first then handle the rest separately
#todo think of the split