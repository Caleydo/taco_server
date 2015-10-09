__author__ = 'Reem'

import flask
import timeit
from src import diff_cache
import hashlib

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
@app.route('/diff_log/<id1>/<id2>/<lod>/<direction>/<ops>')
def diff_log(id1, id2, lod, direction, ops):
    t1 = timeit.default_timer()
    name = str(id1) + '_' + str(id2) + '_' + str(lod) + '_' + str(direction) + '_' + str(ops)
    hash_name = hashlib.md5(name).hexdigest()
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


def create():
  """
  by convention contain a factory called create returning the extension implementation
  :return:
  """
  return app

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
