import scrapy
import re
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
import os
import sys
from urllib.parse import urlparse
from comment import Comment

import json
from pprint import pprint

mongo_url = os.getenv('PYTHON_LAB2_MONGO_URL', None)
if (mongo_url == None):
    print("Can't connect mongo")
    sys.exit(0)

connection = pymongo.MongoClient(mongo_url)
db = connection["python_lab2"]

INPUT_FILENAME = 'data.json'

class ForumSpider(scrapy.Spider):
    
    with open(INPUT_FILENAME) as f:
        data = json.load(f)
    
    try:
        name = data['spider_name']
        COMMENTS_PER_PAGE = data['comments_per_page']
        urls = data['concrete_urls']
        posts_key = data['keys']['posts']
        topic_key = data['keys']['topic']
        next_page_key = data['keys']['next_page_link']

        post_text_element = data['post_keys']['text']['element']
        post_text_class = data['post_keys']['text']['class']
        post_answer_element = data['post_keys']['answer']['element']
        post_answer_class = data['post_keys']['answer']['class']
        post_author_element = data['post_keys']['author']['element']
        post_author_class = data['post_keys']['author']['class']
        post_date_element = data['post_keys']['date']['element']
        post_date_class = data['post_keys']['date']['class']

    except: 
        print("\tERROR: data.json is wrong. Please fill all default fields")
        sys.exit(0)

    try: 
        forum_urls = data['forum_urls']
    except: 
        forum_urls = None

    url_counter = 0
    current_page = 1

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        try:
            posts = response.xpath(self.posts_key).extract()
        except:
            print('posts scrap failed')
            return None
        try:
            topic = response.xpath(self.topic_key).extract_first()
        except:
            topic = 'unknown'

        for post in posts:
            self.url_counter = self.url_counter + 1

            comment = self.parse_post(post, topic)

            print()
            print(comment.to_string())
            self.save_comment_in_database(comment)

            if (self.url_counter >= self.COMMENTS_PER_PAGE): 
                self.url_counter = 0
                link = self.get_next_page_link_by_response(response)
                return scrapy.Request(url=link, callback=self.parse)
            

    def parse_post(self, post, topic):
        print('self.url_counter : ', self.url_counter)
        soup = BeautifulSoup(post, 'html.parser')

        text = soup.findAll(self.post_text_element, {"class": self.post_text_class})
        answer = soup.findAll(self.post_answer_element, {"class": self.post_answer_class})
        author = soup.findAll(self.post_author_element, {"class": self.post_author_class})
        date = soup.findAll(self.post_date_element, {"class": self.post_date_class})

        author = author[0].text
        text = text[0].text
        date = date[0].text
        try:
            to_delete = answer[0].text
            text = text[len(to_delete):]
        except:
            print(None)
        author = author.strip()
        text = text.strip()

        return Comment(author, text, date, topic)


    def get_next_page_link_by_response(self, response):
        href = str(response)
        href = href[4:]
        href = href[:-1]
        href = href.strip()
        parsed_uri = urlparse(href)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

        href = response.xpath(self.next_page_key).extract_first()
        if href == None:
            return None

        next_page_link = domain + href
        return next_page_link

    def save_comment_in_database(self, comment):
        data = {
            'author' : comment.author, 
            'text' : comment.text, 
            'date' : comment.date, 
            'topic' : comment.topic
        }
        return db.comments.update(data, data, upsert=True)