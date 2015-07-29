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
    join_path = os.path.splitext(os.path.basename(path1))[0] + "_" + os.path.splitext(os.path.basename(path2))[0] + "_diff.log"
    print os.path.abspath(path1)
    return join_path


@app.route('/diff_log/<id1>/<id2>')
def diff_log(id1, id2):
    ds1 = dataset.get(int(id1))
    ds2 = dataset.get(int(id2))
    if os.path.exists(ds1._path) and os.path.exists(ds2._path):
        difff = diff_filename(ds1._path, ds2._path)
        if not os.path.exists("data/" + difff):
            #print(ds1._path, ds2._path)
            #print("difff is ", difff)
            if diff_finder.generate_diff(ds1._path, ds2._path, difff):
                print('generated new diff file')
                return flask.send_file("data/" + difff, mimetype='text/tab-separated-values')
            else:
                print('could not generate a new file')
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
    return str(ds1.asjson()) #todo change this!
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