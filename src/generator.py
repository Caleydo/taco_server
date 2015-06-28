__author__ = 'Reem'
import numpy as np
import random


# creates an array with random float values within a range with size
def random_floats_array(low, high, size):
    return [random.uniform(low, high) for _ in xrange(size)]


# creates an array with random int values within a range with size
def random_int_array(low, high, size):
    return [random.randint(low, high) for _ in xrange(size)]


# creates a homogeneous table
def create_table(rows, cols, min_data, max_data, data_type=int):
    table = []
    #generate the header
    header_row = ['row_ids']
    header_row += ['col' + str(x+1) for x in range(cols)]
    first_col = ['row' + str(x+1) for x in range(rows)]
    #table.append(header_row) #no need to append the header because we send it as a result
    for i in range(rows):
        new_row = []
        if data_type == int:
            # or can use insert function instead, but + is also working
            new_row += random_int_array(min_data, max_data, cols)
        else:
            new_row += random_floats_array(min_data, max_data, cols)
        table.append(new_row)
    return {'table': np.array(table), 'col_ids': header_row, 'row_ids': first_col}


# save a table to a file
def save_table(table, row_ids, col_ids, file_name):
    #fmt = '%.6f'
    fmt = '%s'
    #fmt = '%r'
    with_first_col = np.c_[row_ids, table]
    with_headers = np.r_[[col_ids],with_first_col]
    print ("i'm with headers", with_headers)
    np.savetxt(file_name, with_headers, delimiter=',', fmt=fmt)


# todo make it as a class or a script
# todo notice that the row identifiers are floats
# todo add identifier for each column (could be the header?)
# todo add a header to the log file? (operation, row/column/cell, id, position, data)