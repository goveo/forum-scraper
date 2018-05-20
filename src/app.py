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

		commnets_count = get_comments_count_by_username(username)
		print("commnets_count : ", commnets_count)
		if (commnets_count == 0):
			return render_template("error.html", error = 'Wrong username') 
		else:
			total_comments = get_comments_total_count()
			
			topics = get_topics_by_username(username)
			print('topics : ', topics)
			messages_in_topics = []
			for topic in topics:
				messages_in_topics.append(get_comments_count_by_username_and_topic(username, topic))

		total_topics = len(topics)

		return render_template(
			"chart.html",
			coments_count = commnets_count,
			total_comments = total_comments,
			total_topics = total_topics,
			username = username,
			topics = topics,
			messages_in_topics = messages_in_topics)


def get_topics_by_username(username):
	topics = db.comments.distinct( "topic", { "author": username} )
	return topics


def get_comments_count_by_username_and_topic(username, topic):
	comments = db.comments.find( {"author": username, "topic" : topic}).count()
	return comments


def get_comments_count_by_username(username):
	comments_count = db.comments.find( {"author": username }).count()
	return comments_count


def get_comments_count_by_topic(topic):
	topics_count = db.comments.find({"topic": topic}).count()
	return topics_count

def get_comments_total_count():
	comments_count = db.comments.find().count()
	return comments_count



if __name__ == "__main__":
	app.run(debug=True)