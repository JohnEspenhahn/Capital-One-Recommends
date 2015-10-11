import flask
from flask import Flask, request
import hashlib, uuid
import sqlite3 as lite
import sys
from flask.ext.cors import CORS, cross_origin
from flask.ext import restful
from flask.ext.restful import Api
import json


app = Flask(__name__)
cors = CORS(app, resources={r"/": {"origins": "localhost"}})
app.config['CORS_HEADERS'] = 'Content-Type'


DEBUG = True
app.config.from_object(__name__)

salt = 'b63f705cdf42417fa92d3d797cfea761'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route("/", methods=['POST'])
@cross_origin()
def hello(): 
	return "Hello World"


#registers an account given the name, username, password and account id
@app.route("/register", methods=['POST'])
@cross_origin()
def register():
	name = request.form.get('name')
	username = request.form.get('username')
	password = request.form.get('password')
	hPass = hashlib.sha512(salt + password).hexdigest()
	account = request.form.get('account')
	con = None
	data = {}
	try:
		con = lite.connect("users.db")
		cur = con.cursor()
		# cur.execute("CREATE TABLE Users(Id INTEGER PRIMARY KEY, Name TEXT, Username TEXT, Password TEXT, Account TEXT)")
		tuple = (name, username, hPass, account);
		cur.execute("INSERT INTO Users(Name, Username, Password, Account) VALUES('%s', '%s', '%s', '%s');" % tuple)
		con.commit()
		data['success'] = True

	except lite.Error, e:
		print "Error %s" % e.args[0]
		data['success'] = False

	finally:
		if con:
			con.close()
	return json.dumps(data)

#logs into an account
#returns the customer id if successful
#if unsuccessful, returns the word fail followed by either True or False which indicates whether an account with that username even exists
@app.route("/login", methods=['POST'])
@cross_origin()
def login(): 
	username = request.form.get('username')
	password = request.form.get('password')
	hPass = hashlib.sha512(salt + password).hexdigest()

	con = None
	try:
		con = lite.connect("users.db")
		cur = con.cursor()
		# cur.execute("CREATE TABLE Users(Id INTEGER PRIMARY KEY, Name TEXT, Username TEXT, Password TEXT, Account TEXT)")
		tuple = (username);
		cur.execute("SELECT * FROM Users WHERE Username='%s';" % username)
		o = cur.fetchone()
		data = {}
		if(o is None or o[3] != hPass): #unsucessful login
			data['success'] = False
			if o is not None:
				data['message'] = 'Username/password is incorrect. Please try again.'
			else:
				data['message'] = 'Account does not exist. Please register first.'
		else: #successful login
			data['success'] = True
			data['name'] = o[2]
			data['id'] = o[4]
			data['message'] = 'Login successful.'

		return json.dumps(data)

	except lite.Error, e:
		print "Error %s" % e.args[0]
		sys.exit(1)

	finally:
		if con:
			con.close()


@app.route('/shutdown')
@cross_origin()
def shutdown():
    shutdown_server()
    return 'Server shutting down...'



@app.after_request
def add_cors(resp):
    """ Ensure all responses have the CORS headers. This ensures any failures are also accessible
        by the client. """
    resp.headers['Access-Control-Allow-Origin'] = flask.request.headers.get('Origin','*')
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
    resp.headers['Access-Control-Allow-Headers'] = flask.request.headers.get( 
        'Access-Control-Request-Headers', 'Authorization' )
    # set low for debugging
    if app.debug:
        resp.headers['Access-Control-Max-Age'] = '1'
    return resp


if __name__ == '__main__':
	app.run(	)