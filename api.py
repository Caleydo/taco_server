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

def diff_filename(path1, path2):
    #old naming using the file name
    join_path = os.path.splitext(os.path.basename(path1))[0] + "_" + os.path.splitext(os.path.basename(path2))[0] + "_diff.log"
    return join_path


@app.route('/diff_log/<id1>/<id2>')
def diff_log(id1, id2):
    ds1 = dataset.get(id1)
    ds2 = dataset.get(id2)
    if os.path.exists(ds1._path) and os.path.exists(ds2._path):
        #difff = diff_filename(ds1._path, ds2._path)
        difff = "diff_" + id1 + "_" + id2 + ".log"
        if not os.path.exists( os.path.join("data",difff)):
            #create the table object
            table1 = {'table': ds1.asnumpy(), 'col_ids': ds1.cols(), 'row_ids': ds1.rows()}
            table2 = {'table': ds2.asnumpy(), 'col_ids': ds2.cols(), 'row_ids': ds2.rows()}
            if diff_finder.generate_diff(table1, table2, difff):
                print('generated new diff file', os.path.join("data",difff))
                return flask.send_file("data/" + difff, mimetype='text/tab-separated-values')
            else:
                print('could not generate a new file, theres nothing in common between these tables')
        else:
            print("it already exists")
            return flask.send_file("data/" + difff, mimetype='text/tab-separated-values')
            #ds1.asnumpy()
            #ds1.rows()
            #ds1.cols()
            #print(ds1.asjson())
    else:
        print("one of the files is missing!!")
    #return flask.jsonify(ds1.asjson())
    #todo return a value that could be handled to show an error in the client side
    return ""
  #return flask.send_file('data/'+ diff_name +'_diff.log', mimetype='text/tab-separated-values')
  #return flask.make_response()

def create():
  """
  by convention contain a factory called create returning the extension implementation
  :return:
  """
  return app

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=9000)