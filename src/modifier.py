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

def randomly_change_table(full_table, min_data, max_data, change_type, new_id = None):
    table = full_table['table']
    row_ids = full_table['row_ids']
    col_ids =full_table['col_ids']
    #just in case of an empty table
    largest_row = 10
    largest_col = 3
    #shape of the table without ids
    table_height = table.shape[0]
    table_width = table.shape[1]

    if change_type == ADD_ROW:
        index = random.randint(0, table_height)
        if table_height > 0:
            if table_width > 0:
                new_row = gen.random_floats_array(min_data, max_data, table_width)
            else:
                #i don't know if this is possible in anyway!!
                new_row = gen.random_floats_array(min_data, max_data, 1)
        else:
            # table is empty
            # todo recheck
            new_id = 1 #or?
            new_row = gen.random_floats_array(min_data, max_data, random.randint(1, largest_row))
        log.message("add", "row", "row"+str(new_id), index, new_row)
        row_ids.insert(index, "row"+str(new_id))
        new_id += 1
        table = add_row(table, index, new_row)
    elif change_type == ADD_COL:
        if table_height > 0:
            index = random.randint(0, table_width)
            new_col = gen.random_floats_array(min_data, max_data, table_height)
        else:
            #this is the first column or what?
            index = 0
            new_id = 1 #?
            new_col = gen.random_floats_array(min_data, max_data, random.randint(1, largest_col))
        log.message("add", "column", "col"+str(new_id), index, new_col)
        col_ids.insert(index, "col"+str(new_id))
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

def merge_columns(full_table, merge_array):
    #assuming that the merge function is "MEAN"
    table = full_table['table']
    col_ids = full_table['col_ids']
    row_ids = full_table['row_ids']
    cols = table[:, merge_array]
    merged_col = cols.mean(axis=1)
    #change the cols IDs
    ids = [col_ids[i] for i in merge_array]
    merged_id = "+".join(ids)
    #todo now we are assuming that we merge the columns to the place of the first col
    #remove the cols
    for dc in sorted(merge_array, reverse=True):
        table = del_col(table, dc)
        col_ids.pop(dc)
    #add the new col
    table = add_col(table, merge_array[0], merged_col)
    #update the IDs
    col_ids.insert(merge_array[0], merged_id)
    log.message("merge","column", merged_id ,merge_array)
    print(merged_id, cols, merged_col, table)
    return {"table": table, "col_ids": col_ids, "row_ids": row_ids}

def merge_rows(full_table, merge_array):
    #assuming that the merge function is "MEAN"
    table = full_table['table']
    col_ids = full_table['col_ids']
    row_ids = full_table['row_ids']
    rows = table[merge_array, :]
    merged_row = rows.mean(axis=0)
    #change the rows IDs
    ids = [row_ids[i] for i in merge_array]
    merged_id = "+".join(ids)
    #todo now we are assuming that we merge the rows to the place of the first row
    #remove the rows
    for dr in sorted(merge_array, reverse=True):
        table = del_row(table, dr)
        row_ids.pop(dr)
    #add the new row
    table = add_row(table, merge_array[0], merged_row)
    #update the IDs
    row_ids.insert(merge_array[0], merged_id)
    log.message("merge","row", merged_id, merge_array)
    print(merged_id, rows, merged_row, table)
    return {"table": table, "col_ids": col_ids, "row_ids": row_ids}

# operations is an array with the desired operations ordered
def change_table(full_table, min_data, max_data, operations):
    #latest ids for insertion
    #todo put it somewhere else :|
    latest_row_id = get_last_id(full_table['row_ids'])
    latest_col_id = get_last_id(full_table['col_ids'])
    new_row_id = latest_row_id + 1
    new_col_id = latest_col_id + 1
    # first delete the rows
    for r in xrange(operations['del_row']):
        full_table = randomly_change_table(full_table, min_data, max_data, DEL_ROW)
    # then delete the cols
    for c in xrange(operations['del_col']):
        full_table = randomly_change_table(full_table, min_data, max_data, DEL_COL)
    # then add rows
    for r in xrange(operations['add_row']):
        full_table = randomly_change_table(full_table, min_data, max_data, ADD_ROW, new_row_id)
        new_row_id +=1
    # then add cols
    for c in xrange(operations['add_col']):
        full_table = randomly_change_table(full_table, min_data, max_data, ADD_COL, new_col_id)
        new_col_id +=1
    #finally change the cells
    for c in xrange(operations['ch_cell']):
        full_table = randomly_change_table(full_table, min_data, max_data, CH_CELL)
    #merge operation
    #the order of this operation might change later
    for mc in operations['me_col']:
        #full_table = merge_col(full_table)
        print ('merge col', mc)
        full_table = merge_columns(full_table, mc)
    for mr in operations['me_row']:
        full_table = merge_rows(full_table, mr)
    return full_table


# testing
ADD_ROW = 1
ADD_COL = 2
DEL_ROW = 3
DEL_COL = 4
CH_CELL = 5

data_directory = '../data/'
file_name = 'wide_table'
in_file_name = file_name + '_in.csv'
out_file_name = file_name + '_out.csv'
log_file = data_directory + file_name + '.log'

rows = 5
cols = 10
min_data = 0
max_data = 5 #don't forget to update this in the index.json and restart the server

# I know it's a bit crazy like this but I couldn't come up with a smarter way
# the problem that this has no order
#todo think of a structure where we can specify exactly the cells/cols/rows that could be modified
operations_count = {
    'del_row': 1,
    'del_col': 0,
    'add_row': 0,
    'add_col': 100,
    'ch_cell': 20, #todo changing in a new row is not considered
   # 'me_col': [[0,1,2]],
    'me_col': [],
    'sp_col': 0, #idk
 #   'me_row': [[0,2]],
    'me_row': [],
    'sp_row': 0 #i also dk
    }

log.init_log(log_file)

result = gen.create_table(rows, cols, min_data, max_data, data_type=int)

#save the input file
gen.save_table(result['table'], result['row_ids'], result['col_ids'], data_directory + in_file_name)

# change
result = change_table(result, min_data, max_data, operations_count)

# the old testing
# random.seed(10)
# num_of_changes = random.randint(2, 15)
# print("num of changes is ", num_of_changes - 1)
# for i in xrange(1, num_of_changes):
#     result = randomly_change_table(result, min_data, max_data, 1)

#save the output file
gen.save_table(result['table'], result['row_ids'], result['col_ids'], data_directory + out_file_name)

#print(result, result['table'].shape)

#todo make sure that the log file is complete and ordered somehow
#todo choose the percentage of change e.g. structural and content
#todo think of the split operation
#todo changing in an added row/col will be ignored as it is already a new thing
