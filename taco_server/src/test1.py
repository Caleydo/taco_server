import numpy as np
import random

__author__ = 'Reem'


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
    #     print("Error: size of new column")
  else:
    print("Error: out of range column insertion")
  return my_array


def change_cell(my_array, row, col, new_value):
  if (row < len(my_array) and col < len(my_array[row])):
    # print(row,col)
    my_array[row][col] = new_value
  else:
    print("Error: out of range changes")
  return my_array


def del_row(my_array, index):
  array_length = len(my_array)
  # check if the table is empty
  if array_length == 0:
    print(("Error: list is empty, can't delete a row", index))
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
    print(("Error: list is empty, can't delete a row", index))
    return my_array
  else:
    row_length = len(my_array[0])
    if index < row_length:
      my_array = np.delete(my_array, index, axis=1)
    else:
      print("Error: out of range deletion")
  return my_array


ADD_ROW = 1
ADD_COL = 2
CH_CELL = 3
DEL_ROW = 4
DEL_COL = 5


def randomly_change_table(table):
  change_type = random.randint(1, 5)
  largest_row = 10
  min_data = 0
  max_data = 30
  largest_col = 3
  if change_type == ADD_ROW:
    index = random.randint(0, len(table))
    if len(table) > 0:
      new_row = random.sample(list(range(min_data, max_data)), len(table[0]))
    else:
      # table is empty
      new_row = random.sample(list(range(min_data, max_data)), random.randint(1, largest_row))
    print(("log: add a row in ", index, new_row))
    table = add_row(table, index, new_row)
  elif change_type == ADD_COL:
    if len(table) > 0:
      index = random.randint(0, len(table[0]))
      new_col = random.sample(list(range(min_data, max_data)), len(table))
    else:
      index = 0
      new_col = random.sample(list(range(min_data, max_data)), random.randint(1, largest_col))
    print(("log: add a col in ", index, new_col))
    table = add_col(table, index, new_col)
  elif change_type == CH_CELL:
    if len(table) > 0:
      i = random.randint(0, len(table) - 1)
      j = random.randint(0, len(table[0]) - 1)
      new_value = random.uniform(min_data, max_data)
      print(("log: change something somewhere ", i, j, new_value))
      table = change_cell(table, i, j, new_value)
    else:
      print("log: there's nothing to change")
  elif change_type == DEL_ROW:
    index = random.randint(0, len(table) - 1)
    print(("log: delete row ", index))
    table = del_row(table, index)
  elif change_type == DEL_COL:
    index = random.randint(0, len(table[0]) - 1)
    print(("log: delete col ", index))
    table = del_col(table, index)
  return table


file_name = "../../data/small_table.csv"

my_array = np.array([[7.1, 3], [1, 4], [2, 3], [3, 3]])
# this generates text all are strings
# my_array = np.array([["col1","col2"],[1,4],[2,3],[3,3]])
# np.savetxt(file_name,my_array, delimiter=',',fmt='%s')

# this generates a table where I write the header alone with comments nothing
# more reasonable if the data is int or float
# np.savetxt(file_name, my_array, delimiter=',', fmt='%.5f', header='col1,col2', comments='')
np.savetxt(file_name, my_array, delimiter=',', fmt='%.5f')

b = np.loadtxt(file_name, dtype=float, delimiter=',')

# print(b)
c = []

my_array = change_cell(my_array, 3, 3, 88)
my_array = add_col(my_array, 1, [2, 3, 4, 5])
my_array = add_col(my_array, 1, [2.3, 3.3, 15, 55])
my_array = add_row(my_array, 0, [15, 22.2, 7, 6])
# print(my_array)

random.seed(10)
# rand = random.randint(0,100)
# rand = random.randrange(0,100)
rand = random.uniform(-1, 100)
# print(rand)

# 1- create 3 initial tables
# 2- modify these tables randomly
# 3- save each of the new table in a file with a similar name
table_1 = [[1]]
table_2 = np.array([[13, 0.1], [7.1, 3], [1, 4], [2, 3], [3, 3]])
# table_3 might be from a file as it has to be big
input_file = '../../data/small_table_in.csv'
my_date = np.genfromtxt(input_file, delimiter=',')
print(("this is my data", my_date))
output_file = "../../data/small_table_out.csv"

random.seed(100)
num_of_changes = random.randint(2, 20)
print(("num of changes is ", num_of_changes - 1))
for i in range(1, num_of_changes):
  my_date = randomly_change_table(my_date)
  print(my_date)
# print(table_2)

# save the result in a file
np.savetxt(output_file, my_date, delimiter=',', fmt='%.6f')

# TODO recheck the case of empty list
# todo when the table is one column then adding anything doesn't work
# todo changing a value gets an integer instead of a float!
# todo error out of range changes?
