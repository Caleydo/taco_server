#!/usr/bin/python
__author__ = 'Reem'

import numpy as np
import logger as log
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

#compares two lists and logs the diff
#todo consider sorting or merge
def compare_ids(ids1, ids2, type):
    for i in get_deleted_ids(ids1, ids2):
        log.message("delete", type, i, np.where(ids1 == i)[0][0])
    for j in get_added_ids(ids1, ids2):
        log.message("add", type, j, np.where(ids2 == j)[0][0])
    return None

#testing

full_table1 = get_full_table(data_directory+in_file_name)
#print(full_table1['table'])
full_table2 = get_full_table(data_directory+out_file_name)
#print(full_table2['table'])

log.init_log(log_file)
compare_ids(full_table1['col_ids'], full_table2['col_ids'], "column")
compare_ids(full_table1['row_ids'], full_table2['row_ids'], "row")

#todo should the result be the log or the union array with notation of difference (which is added or removed)?