__author__ = 'Reem'

import flask
#from src import diff_finder

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

@app.route('/diff_log')
def diff_log():
  return flask.send_file('data/tiny_table1_diff.log', mimetype='text/tab-separated-values')
  #return "i hate this work it's shit"
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