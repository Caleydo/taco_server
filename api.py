__author__ = 'Reem'

import flask
import timeit
from src import diff_cache, graph, diff_finder
import ujson

#create an Flask app for hosting my namespace
app = flask.Flask(__name__)
#request my configuration
#import caleydo_server.config
#config = caleydo_server.config.view('taco_server')

@app.route('/hello/<whom>')
def hello_world(whom):
  return 'hello world' +  whom+ ' ' + flask.request.args.get('to')

@app.route('/jsontest')
def jsontest():
  return flask.jsonify({'x': 'where are you', 'y': "too"})


#@direction: 0 rows, 1 cols, 2 both rows and cols
@app.route('/diff_log/<id1>/<id2>/<lod>/<direction>/<ops>/<bins>')
def diff_log(id1, id2, lod, direction, ops, bins):
    t1 = timeit.default_timer()
    if lod == str(diff_finder.Levels.overview):
        json_result = diff_cache.get_ratios(id1, id2, direction, ops)
    elif lod == str(diff_finder.Levels.middle):
        json_result = diff_cache.get_aggregated(id1, id2, direction, ops)
    else:
        json_result = diff_cache.get_diff(id1, id2, direction, ops)
    # creating flask response
    response = flask.make_response(json_result)
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


@app.route('/aggregate/<id1>/<id2>/<direction>/<ops>/<bins>')
def aggregate(id1, id2, direction, ops, bins):

    json_result = diff_cache.get_diff(id1, id2, direction, ops)
    # creating flask response
    response = flask.make_response(json_result)
    response.headers["content-type"] = 'application/json'
    return response


def create():
  """
  by convention contain a factory called create returning the extension implementation
  :return:
  """
  return app

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
