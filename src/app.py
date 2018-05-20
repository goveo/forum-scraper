from flask import Flask, render_template, request

import numpy as np
import pystache

import pymongo
from pymongo import MongoClient
import os
import sys

app = Flask(__name__, static_folder='static', static_url_path='')

mongo_url = os.getenv('PYTHON_LAB2_MONGO_URL', None)
if (mongo_url == None):
    print("Can't connect mongo")
    sys.exit(0)

connection = pymongo.MongoClient(mongo_url)
db = connection["python_lab2"]

@app.route("/")
def index():
	users = db.comments.distinct("author")
	return render_template('index.html', result = users)

@app.route('/search', methods = ['POST', 'GET'])
def result():
	if request.method == 'POST':
		result = request.form
		username = result.get('username', type=str)
		print("username : ", username)

		commnets_count = db.comments.find( {"author": username }).count()
		print("commnets_count : ", commnets_count)
		if (commnets_count == 0):
			return render_template("result.html", error = 'Wrong username') 
		else:
			total_comments = db.comments.find().count()

		return render_template(
			"result.html",
			count = commnets_count,
			total_comments = total_comments,
			username = username)

if __name__ == "__main__":
	app.run(debug=True)