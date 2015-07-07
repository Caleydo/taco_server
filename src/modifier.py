__author__ = 'Reem'
import numpy as np
import random
import generator as gen
import logger as log


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


# adds a new_col to the array in the specified index
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
    #consider that we don't change the IDs
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
        print("Error: list is empty, can't delete a col", index)
        return my_array
    else:
        row_length = len(my_array[0])
        if index < row_length:
            my_array = np.delete(my_array, index, axis=1)
        else:
            print("Error: out of range deletion")
    return my_array

#to get the last id from the row_ids or the col_ids
#assuming that the id starts with 3 letters ('col' or 'row')
def get_last_id(id_list):
    num_ids = []
    for full_id in id_list:
        num_ids.append(int(full_id[3:]))
    #interesting because in numpy it's list_name.max()!
    return max(num_ids)

def randomly_change_table(full_table, min_data, max_data):
    table = full_table['table']
    row_ids = full_table['row_ids']
    col_ids =full_table['col_ids']
    change_type = random.randint(1, 5)
    ADD_ROW = 1
    ADD_COL = 2
    CH_CELL = 3
    DEL_ROW = 4
    DEL_COL = 5
    largest_row = 10
    largest_col = 3
    #shape of the table without ids
    table_height = table.shape[0]
    table_width = table.shape[1]
    #latest ids for insertion
    latest_row_id = get_last_id(row_ids)
    latest_col_id = get_last_id(col_ids)
    new_row_id = latest_row_id + 1
    new_col_id = latest_col_id + 1
    if change_type == ADD_ROW:
        index = random.randint(0, table_height)
        if table_height > 0:
            latest_row_id += 1
            if table_width > 0:
                new_row = gen.random_floats_array(min_data, max_data, table_width)
            else:
                #i don't know if this is possible in anyway!!
                new_row = gen.random_floats_array(min_data, max_data, 1)
        else:
            # table is empty
            # recheck
            latest_row_id = 1 #or?
            new_row = gen.random_floats_array(min_data, max_data, random.randint(1, largest_row))
        log.message("add", "row", "row"+str(new_row_id), index, new_row)
        row_ids.insert(index, "row"+str(new_row_id))
        table = add_row(table, index, new_row)
    elif change_type == ADD_COL:
        if table_height > 0:
            index = random.randint(0, table_width)
            new_col = gen.random_floats_array(min_data, max_data, table_height)
            latest_col_id += 1
        else:
            #this is the first column or what?
            index = 0
            latest_col_id = 1 #?
            new_col = gen.random_floats_array(min_data, max_data, random.randint(1, largest_col))
        log.message("add", "column", "col"+str(new_col_id), index, new_col)
        col_ids.insert(index, "col"+str(new_col_id))
        table = add_col(table, index, new_col)
    elif change_type == CH_CELL:
        if table_height > 0:
            i = random.randint(0, table_height - 1)
            j = random.randint(0, table_width - 1)
            new_value = random.uniform(min_data, max_data)
            log.message("change", "cell", row_ids[i]+','+col_ids[j], str(i)+','+str(j), new_value)
            table = change_cell(table, i, j, new_value)
        else:
            print("log: there's nothing to change")
    elif change_type == DEL_ROW:
        index = random.randint(0, table_height - 1)
        log.message("delete","row", row_ids[index] ,index, table[index])
        row_ids.pop(index)
        table = del_row(table, index)
    elif change_type == DEL_COL:
        if table_width > 0:
            index = random.randint(0, table_width - 1)
            log.message("delete","column", col_ids[index] ,index, table[:,index])
            col_ids.pop(index)
            table = del_col(table, index)
        else:
            print("Error: no columns to delete")
    return {'table': np.array(table), 'col_ids': col_ids, 'row_ids': row_ids}


# testing
data_directory = '../data/'
file_name = 'tiny_table1'
in_file_name = file_name + '_in.csv'
out_file_name = file_name + '_out.csv'
log_file = data_directory + file_name + '.log'

rows = 6
cols = 5
min_data = 0
max_data = 10

log.init_log(log_file)

result = gen.create_table(rows, cols, min_data, max_data, data_type=float)
result_table = result['table']
print (result['col_ids'], result['row_ids'])

size = result_table.shape
#save the input file
gen.save_table(result_table, result['row_ids'], result['col_ids'], data_directory + in_file_name)

#add the header to the table
# (should be read from the file as a whole table but for now I add it manually)
#big_table = np.insert(big_table, 0, header, axis=0)
#print(big_table)
output_table = None
# the old testing
random.seed(10)
num_of_changes = random.randint(2, 15)
print("num of changes is ", num_of_changes - 1)
for i in xrange(1, num_of_changes):
    result = randomly_change_table(result, min_data, max_data)
    #print(big_table)

#todo to activate this
gen.save_table(result['table'], result['row_ids'], result['col_ids'], data_directory + out_file_name)

print(result, result['table'].shape)

#todo delete operations first then add or ch operations
#todo make sure that the log file is complete and ordered somehow
#todo choose the operations that you want to apply on tables
#todo make the logging in a separate file