__author__ = 'YOU'

import flask

#create an Flask app for hosting my namespace
app = flask.Flask(__name__)

#request my configuration
#import caleydo_server.config
#config = caleydo_server.config.view('taco_server')

@app.route('/hello/<whom>')
def hello_world(whom):
  return 'asdfasf' +  whom+ ' ' + flask.request.args.get('to')

def create():
  """
  by convention contain a factory called create returning the extension implementation
  :return:
  """
  return app