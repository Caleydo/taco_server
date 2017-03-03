from phovea_server import ns
import timeit
from src import diff_cache
import logging


__author__ = 'Reem'

_log = logging.getLogger(__name__)

# create an Namespace app for hosting my namespace
app = ns.Namespace(__name__)


# request my configuration
# import phovea_server.config
# config = phovea_server.config.view('taco_server')

@app.route('/hello/<whom>')
def hello_world(whom):
  return 'hello world' + whom + ' ' + ns.request.args.get('to')


@app.route('/jsontest')
def jsontest():
  return ns.jsonify({'x': 'where are you', 'y': "too"})


@app.route('/diff_log/<id1>/<id2>/<bins_row>/<bins_col>/<direction>/<operations>')
def diff_log(id1, id2, bins_row, bins_col, direction, operations):
  """
  @see: https://github.com/Reemh/taco_server/wiki/Diff-Aggregation
  @deprecated: Use the more specific routes instead

  :param id1: id of the first table
  :param id2: id of the second table
  :param bins_row: number of bins in row direction
  :param bins_col: number of bins in column direction
  :param direction: 0 = rows, 1 = cols, 2 = rows and cols
  :param changes:
  :return:
  """
  t1 = timeit.default_timer()
  b = int(bins_row)
  if b == 0:
    # no bins which is the diff heatmap (detail)
    json_result = diff_cache.get_diff_table(id1, id2, direction, operations, True)
  else:
    # the overview view and
    # the middle view based on the number of bins or lines i.e. rows/columns (middle)
    b_c = int(bins_col)
    json_result = diff_cache.get_ratios(id1, id2, direction, operations, b, b_c)
  t6 = timeit.default_timer()
  _log.debug("TIMER: time for everything ", t6 - t1)
  # creating flask response
  return make_json_response(json_result)


def make_json_response(json_string):
  response = ns.make_response(json_string)
  response.headers["content-type"] = 'application/json'
  return response


@app.route('/compare/<id1>/<id2>/<operations>/bar_chart')
def bar_chart(id1, id2, operations):
  bins_row = 1
  bins_col = 1
  direction = 2
  return diff_log(id1, id2, bins_row, bins_col, direction, operations)


@app.route('/compare/<id1>/<id2>/<operations>/ratio_2d')
def ratio_2d(id1, id2, operations):
  bins_row = -1  # -1 = aggregate the whole table
  bins_col = -1  # -1 = aggregate the whole table
  direction = 2
  return diff_log(id1, id2, bins_row, bins_col, direction, operations)


@app.route('/compare/<id1>/<id2>/<bins_row>/<bins_col>/<operations>/histogram')
def histogram(id1, id2, bins_row, bins_col, operations):
  direction = 2
  return diff_log(id1, id2, bins_row, bins_col, direction, operations)


@app.route('/compare/<id1>/<id2>/<operations>/diff_heat_map')
def diff_heatmap(id1, id2, operations):
  bins_row = 0
  bins_col = 0
  direction = 2
  return diff_log(id1, id2, bins_row, bins_col, direction, operations)


def create():
  """
  by convention contain a factory called create returning the extension implementation
  :return:
  """
  return app

if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0', port=9000)
