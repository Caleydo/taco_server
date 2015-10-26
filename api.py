__author__ = 'Reem'

import flask
import timeit
from src import diff_cache, fd_graph
import os
import json
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
# /4/2/structure,content
@app.route('/diff_log/<id1>/<id2>/<lod>/<direction>/<ops>')
def diff_log(id1, id2, lod, direction, ops):
    t1 = timeit.default_timer()
    hash_name = diff_cache.create_hashname(id1, id2, lod, direction, ops)
    json_result = diff_cache.get_diff_cache(hash_name)
    if json_result is None:
        json_result = diff_cache.calc_diff(id1, id2, lod, direction, ops)
        diff_cache.set_diff_cache(hash_name, json_result)
    # creating flask response
    response = flask.make_response(json_result)
    response.headers["content-type"] = 'application/json'
    t6 = timeit.default_timer()
    print("time for everything ", t6 - t1)
    return response

@app.route('/mds')
def mds():
    id_list = ["tacoServerTacoMultiple5Output", "tacoServerTacoMultiple4Output", "tacoServerTacoMultiple3Output"]
    fd_res = fd_graph.calc_fd_graph(id_list, 4, 2, "structure,content")
    mds_directory = 'plugins/taco_server/mds_data/'
    #file_name = mds_directory + 'mdsdata.json'
    file_name = mds_directory + 'fddata.json'
    if os.path.isfile(file_name):
        with open(file_name) as data_file:
          data = json.load(data_file)
        return ujson.dumps(data)
    #if the file doesn't exist
    return None


def create():
  """
  by convention contain a factory called create returning the extension implementation
  :return:
  """
  return app

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
