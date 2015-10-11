from flask import Flask, request
import hashlib, uuid
import sqlite3 as lite
import sys




app = Flask(__name__)

DEBUG = True
app.config.from_object(__name__)

salt = 'b63f705cdf42417fa92d3d797cfea761'

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route("/", methods=['POST'])
def hello(): 
	return "Hello World"


#registers an account given the name, username, password and account id
@app.route("/register", methods=['POST'])
def register():
	name = request.form.get('name')
	username = request.form.get('username')
	password = request.form.get('password')
	hPass = hashlib.sha512(salt + password).hexdigest()
	account = request.form.get('account')
	con = None
	try:
		con = lite.connect("users.db")
		cur = con.cursor()
		# cur.execute("CREATE TABLE Users(Id INTEGER PRIMARY KEY, Name TEXT, Username TEXT, Password TEXT, Account TEXT)")
		tuple = (name, username, hPass, account);
		cur.execute("INSERT INTO Users(Name, Username, Password, Account) VALUES('%s', '%s', '%s', '%s');" % tuple)
		con.commit()
		return 'success'

	except lite.Error, e:
		print "Error %s" % e.args[0]
		sys.exit(1)

	finally:
		if con:
			con.close()


#logs into an account
#returns the customer id if successful
#if unsuccessful, returns the word fail followed by either True or False which indicates whether an account with that username even exists
@app.route("/login", methods=['POST'])
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
		if(o[3] == hPass):
			return o[4]
		else:
			return 'fail ' + str(o is not None)

	except lite.Error, e:
		print "Error %s" % e.args[0]
		sys.exit(1)

	finally:
		if con:
			con.close()


@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
	app.run()