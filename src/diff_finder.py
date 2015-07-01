#!/usr/bin/python
__author__ = 'Reem'

import numpy as np
# import sys
#
# print 'Number of arguments:', len(sys.argv), 'arguments.'
# print 'Argument List:', str(sys.argv)

data_directory = '../data/'
file_name = 'tiny_table1'
in_file_name = file_name + '_in.csv'
out_file_name = file_name + '_out.csv'

#todo think if you want to use this method for the col_ids or copy it manually
#data = np.genfromtxt(data_directory+in_file_name, dtype=None, delimiter=',', names=True)
data = np.genfromtxt(data_directory+in_file_name, dtype=None, delimiter=',')
row_ids = data[1:][:,0]
col_ids = data[0,:][1:]
table = data[1:,1:]
print(table)
#todo find a way to read the row id : maybe check the tutorials