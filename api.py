__author__ = 'Reem'

import flask
from src import diff_finder
from src.diff_finder import Table, DiffFinder
import caleydo_server.dataset as dataset

import os

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
    print(lod)
    ds1 = dataset.get(id1)
    ds2 = dataset.get(id2)

    #todo find a way cash this
    #create the table object
    table1 = Table(list(ds1.rows()), list(ds1.cols()), ds1.asnumpy())
    table2 = Table(list(ds2.rows()), list(ds2.cols()), ds2.asnumpy())
    dfinder = DiffFinder(table1, table2, ds1.rowtype, ds2.coltype, lod, direction)
    return flask.jsonify(dfinder.generate_diff(ops).serialize())
    #todo make sure that both dataset have same rowtype and coltype before calling this api function
    #return flask.jsonify(diff_finder.generate_diff(table1, table2, ds1.rowtype, ds1.coltype, direction))
    #else:
        #print("one of the files is missing!!")
    #return flask.jsonify(ds1.asjson())
    #todo return a value that could be handled to show an error in the client side
    #return "{}"

def create():
  """
  by convention contain a factory called create returning the extension implementation
  :return:
  """
  return app

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9000)
