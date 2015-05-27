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
    header_row = [0]
    header_row += [x for x in range(cols)]
    table.append(header_row)
    for i in range(rows+1):
        new_row = [i+1]
        if data_type == int:
            # or can use insert function instead, but + is also working
            new_row += random_int_array(min_data, max_data, cols)
        else:
            new_row += random_floats_array(min_data, max_data, cols)
        table.append(new_row)
    return np.array(table)


# save a table to a file
def save_table(table, file_name, header=None):
    fmt = '%.6f'
    if header is not None:
        # if there's a header
        # NOTE that header only works as a string
        np.savetxt(file_name, table, delimiter=',', fmt=fmt, header=header, comments='')
    else:
        # if there's no header
        #fmt = '%r'
        np.savetxt(file_name, table, delimiter=',', fmt=fmt)


# todo make it as a class or a script
# todo notice that the row identifiers are floats
# todo add identifier for each column (could be the header?)