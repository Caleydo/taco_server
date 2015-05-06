__author__ = 'Reem'
import numpy as np
import random
import generator as gen
import logging


# adds a new_row to the my_array in the specified index
def add_row(my_array, index, new_row):
    # no out of range index
    # the size of the new row should match the existing rows
    # unless it's an empty array anyway
    if index <= len(my_array) and (len(my_array) == 0 or len(new_row) == len(my_array[0])):
        my_array = np.insert(my_array, index, new_row, axis=0)
    else:
        print("Error: out of range insertion")
    return my_array


def add_col(my_array, index, new_col):
    if (len(my_array) == 0 and index == 0) or (len(new_col) == len(my_array) and index <= len(my_array[0])):
        my_array = np.insert(my_array, index, new_col, axis=1)
        # my_array = np.insert(my_array, index, new_col)
        # else:
        # print("Error: size of new column")
    else:
        print("Error: out of range column insertion")
    return my_array


def change_cell(my_array, row, col, new_value):
    if row < len(my_array) and col < len(my_array[row]):
        # print(row,col)
        my_array[row][col] = new_value
    else:
        print("Error: out of range changes")
    return my_array


def del_row(my_array, index):
    array_length = len(my_array)
    # check if the table is empty
    if array_length == 0:
        print("Error: list is empty, can't delete a row", index)
        return my_array
    else:
        if index < array_length:
            my_array = np.delete(my_array, index, axis=0)
        else:
            print("Error: out of range deletion")
    return my_array


def del_col(my_array, index):
    array_length = len(my_array)
    # check if the table is empty
    if array_length == 0:
        print("Error: list is empty, can't delete a row", index)
        return my_array
    else:
        row_length = len(my_array[0])
        if index < row_length:
            my_array = np.delete(my_array, index, axis=1)
        else:
            print("Error: out of range deletion")
    return my_array


def randomly_change_table(table, min_data, max_data):
    change_type = random.randint(1, 5)
    ADD_ROW = 1
    ADD_COL = 2
    CH_CELL = 3
    DEL_ROW = 4
    DEL_COL = 5
    largest_row = 10
    largest_col = 3
    length_table = table.shape[0]
    width_table = table.shape[1]
    if change_type == ADD_ROW:
        # todo change to consider that the first column is a header
        index = random.randint(0, length_table)
        if length_table > 0:
            # todo consider that the first element is an id
            new_row = gen.random_floats_array(min_data, max_data, width_table)
        else:
            # table is empty
            new_row = gen.random_floats_array(min_data, max_data, random.randint(1, largest_row))
        #print("log: add a row in ", index, new_row)
        # todo get the id instead of index for the log
        log_message("add", "column", index, index, new_row)
        table = add_row(table, index, new_row)
    elif change_type == ADD_COL:
        if length_table > 0:
            index = random.randint(0, width_table)
            new_col = gen.random_floats_array(min_data, max_data, length_table)
        else:
            index = 0
            new_col = gen.random_floats_array(min_data, max_data, random.randint(1, largest_col))
        # todo get the id instead of index for the log
        #print("log: add a col in ", index, new_col)
        log_message("add", "column", index, index, new_col)
        table = add_col(table, index, new_col)
    elif change_type == CH_CELL:
        if length_table > 0:
            i = random.randint(0, length_table - 1)
            j = random.randint(0, width_table - 1)
            new_value = random.uniform(min_data, max_data)
            #print("log: change something somewhere ", i, j, new_value)
            # todo get the id instead of index for the log
            log_message("change", "cell", i, (i,j), new_value)
            table = change_cell(table, i, j, new_value)
        else:
            print("log: there's nothing to change")
    elif change_type == DEL_ROW:
        index = random.randint(0, length_table - 1)
        #print("log: delete row ", index)
        # todo get the id instead of index for the log
        log_message("delete","row", index ,index, table[index])
        table = del_row(table, index)
    elif change_type == DEL_COL:
        if width_table > 0:
            index = random.randint(0, width_table - 1)
            #print("log: delete col ", index)
            # todo get the id instead of index for the log
            log_message("delete","column", index ,index, table[:,index])
            table = del_col(table, index)
        else:
            print("Error: no columns to delete")
    return table


def log_message(operation, type, id, position, data, new_id=None):
    logging.info('\t%s\t%s\t%s\t%s\t%s', operation, type, id, position, data)
    return

# testing
data_directory = '../data/'
in_file_name = 'big_table_in.csv'
out_file_name = 'big_table_out.csv'
log_file = data_directory + 'test.log'

rows = 20
cols = 10
min_data = 0
max_data = 100


# the logging
logging.basicConfig(level=logging.INFO,
                    #format='%(message)s',
                    format='%(asctime)s\t%(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    filename=log_file,
                    filemode='w')

big_table = gen.create_table(rows, cols, min_data, max_data, data_type=float)
gen.save_table(big_table, data_directory + in_file_name )


# the old testing
random.seed(101)
num_of_changes = random.randint(2, 20)
print("num of changes is ", num_of_changes - 1)
for i in xrange(1, num_of_changes):
    big_table = randomly_change_table(big_table, min_data, max_data)
    #print(big_table)

gen.save_table(big_table, data_directory + out_file_name)

print(big_table, big_table.shape)