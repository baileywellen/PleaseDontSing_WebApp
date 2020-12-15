
from flask import Flask

#make a Flask instance with the current module rendered passed to flask
app = Flask(__name__)

#the line below is a little strange because it is calling itself.... but it is importing the routes
#this keeps all of the routes in a separate file to keep it clean
from application import routes