import scrapy
import re
from bs4 import BeautifulSoup
import pymongo
# from pymongo import MongoClient
from pymongo import MongoClient
import os
import sys
from urllib.parse import urlparse

mongo_url = os.getenv('PYTHON_LAB2_MONGO_URL', None)
if (mongo_url == None):
    print("Can't connect mongo")
    sys.exit(0)

connection = pymongo.MongoClient(mongo_url)
db = connection["python_lab2"]

class Comment():
    def __init__(self, author, text, date, topic):
        self.author = author
        self.text = text
        self.date = date
        self.topic = topic

    def to_string(self):
        return 'author : ' + self.author + '\n' + \
            'text : ' + self.text + '\n' + \
            'date : ' + self.date + '\n' + \
            'topic : ' + self.topic

class ForumSpider(scrapy.Spider):

    name = "forum_spider"
    url_counter = 0
    current_page = 1
    COMMENTS_PER_PAGE = 20
    urls = [
        'https://forums.drom.ru/altai/t1152288384.html'
    ]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        try:
            posts = response.xpath('//li[@class="postbitlegacy postbitim postcontainer"]').extract()
        except:
            print('posts scrap failed')
            return None
        try:
            topic = response.xpath('//div[@class="pagetitle"]/h1/text()').extract_first()
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
                print('next page')
                link = self.get_next_page_link_by_response(response)
                print('link :', link)
                return scrapy.Request(url=link, callback=self.parse)
            

    def parse_post(self, post, topic):
        print('self.url_counter : ', self.url_counter)
        soup = BeautifulSoup(post, 'html.parser')

        text = soup.findAll("div", {"class": "content"})
        answer = soup.findAll("div", {"class": "bbcode_container"})
        author = soup.findAll("div", {"class": "username_container"})
        date = soup.findAll("span", {"class": "date"})

        author = author[0].text
        text = text[0].text
        date = date[0].text
        try:
            to_delete = answer[0].text
            text = text[len(to_delete):]
        except:
            # del(to_delete)
            print()
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

        print('domain : ', domain)
        href = response.xpath('//span[@class="prev_next"]/a[@rel="next"]/@href').extract_first()
        print('href : ', href)
        next_page_link = domain + href
        # try:
        #     href = href[0]
        # except:
        #     href = None
        return next_page_link

    def save_comment_in_database(self, comment):
        return db.comments.save({ 
            'author' : comment.author, 
            'text' : comment.text, 
            'date' : comment.date, 
            'topic' : comment.topic
        })