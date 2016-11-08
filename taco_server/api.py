__author__ = 'Reem'

from phovea_server import ns
import timeit
from src import diff_cache, graph, diff_finder
import ujson

#create an Namespace app for hosting my namespace
app = ns.Namespace(__name__)
#request my configuration
#import phovea_server.config
#config = phovea_server.config.view('taco_server')

@app.route('/hello/<whom>')
def hello_world(whom):
  return 'hello world' +  whom+ ' ' + ns.request.args.get('to')

@app.route('/jsontest')
def jsontest():
  return ns.jsonify({'x': 'where are you', 'y': "too"})


# @param direction: 0 rows, 1 cols, 2 both rows and cols
# @param: bins is the number of bins
# see https://github.com/Reemh/taco_server/wiki/Diff-Aggregation
@app.route('/diff_log/<id1>/<id2>/<bins>/<bins_col>/<direction>/<ops>')
def diff_log(id1, id2, bins, bins_col, direction, ops):
    t1 = timeit.default_timer()
    b = int(bins)
    if b == 0:
        # no bins which is the diff heatmap (detail)
        json_result = diff_cache.get_diff(id1, id2, direction, ops, True)
    else:
        # the overview view and
        # the middle view based on the number of bins or lines i.e. rows/columns (middle)
        b_c = int(bins_col)
        json_result = diff_cache.get_ratios(id1, id2, direction, ops, b, b_c)
    # creating flask response
    response = ns.make_response(json_result)
    response.headers["content-type"] = 'application/json'
    t6 = timeit.default_timer()
    print("time for everything ", t6 - t1)
    return response

@app.route('/fd/<ids>')
# /0/2/structure,content
def fd(ids):
    id_list = ids.split(',')
    fd_res = graph.calc_fd_graph(id_list, 2, "structure,content")
    return ujson.dumps(fd_res)


@app.route('/mds/<ids>')
def mds(ids):
    id_list = ids.split(',')
    mds_res = graph.calc_mds_graph(id_list,  2, "structure,content")
    return ujson.dumps(mds_res)


def create():
  """
  by convention contain a factory called create returning the extension implementation
  :return:
  """
  return app

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
