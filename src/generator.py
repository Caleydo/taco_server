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
    for i in range(rows):
        new_row = [i]
        if data_type == int:
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
        np.savetxt(file_name, table, delimiter=',', fmt=fmt)


data_directory = '../data/'
a = create_table(10,2,0,99 , data_type=float)
save_table(a, data_directory + 'big_table_in.csv')

print(a, a.shape)

# todo make it as a class or a script
# todo notice that the row and column identifiers are floats
# todo add identifier for each column