__author__ = 'Reem'

from diff_finder import Table, DiffFinder, Diff
import caleydo_server.dataset as dataset
import timeit
import json
import ujson
import io

data_directory = '../cache/'

def get_diff_cache(name):
    return None


def set_diff_cache(name, data):
    file_name = data_directory + name + '.json'
    with io.open(file_name, 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))


def calc_diff(id1, id2, lod, direction, ops):
    ds1 = dataset.get(id1)
    ds2 = dataset.get(id2)
    # create the table object
    table1 = Table(ds1.rows(), ds1.cols(), ds1.asnumpy())
    table2 = Table(ds2.rows(), ds2.cols(), ds2.asnumpy())
    dfinder = DiffFinder(table1, table2, ds1.rowtype, ds2.coltype, lod, direction)
    t2 = timeit.default_timer()
    d = dfinder.generate_diff(ops)
    t3 = timeit.default_timer()
    print("time to generate diff", t3 - t2)
    if isinstance(d, Diff):
        d.add_union(dfinder.union)
        t4 = timeit.default_timer()
        # json_result = flask.jsonify(d.serialize())
        # json_result = json.dumps(d.serialize())
        json_result = ujson.dumps(d.serialize())
    else:
        # todo later find a way to send the error
        # e.g. there's no matching column in this case
        t4 = timeit.default_timer()
        json_result = ujson.dumps(d)  # which is {} for now!
    t5 = timeit.default_timer()
    print("time for jsonify", t5 - t4)
    return json_result


  # todo make sure that both dataset have same rowtype and coltype before calling this api function
  # todo return a value that could be handled to show an error in the client side
