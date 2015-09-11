__author__ = 'Reem'

import flask
from src import diff_finder
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


@app.route('/diff_log/<id1>/<id2>')
def diff_log(id1, id2):
    ds1 = dataset.get(id1)
    print('ds1', ds1)
    ds2 = dataset.get(id2)
    print('ds2', ds2)
    #if os.path.exists(ds1._path) and os.path.exists(ds2._path):
        #todo find a way cash this
        #create the table object
    table1 = {'table': ds1.asnumpy(), 'col_ids': list(ds1.cols()), 'row_ids': list(ds1.rows())}
    table2 = {'table': ds2.asnumpy(), 'col_ids': list(ds2.cols()), 'row_ids': list(ds2.rows())}
        #todo make sure that both dataset have same rowtype and coltype before calling this api function
    return flask.jsonify(diff_finder.generate_diff(table1, table2, ds1.rowtype, ds1.coltype))
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
