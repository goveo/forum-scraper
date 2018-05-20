import scrapy
import re
from bs4 import BeautifulSoup
import pymongo
# from pymongo import MongoClient
from pymongo import MongoClient

connection = pymongo.MongoClient('mongodb://goveo:goveo@ds129540.mlab.com:29540/python_lab2')
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


    def start_requests(self):
        urls = [
            'https://forums.drom.ru/altai/t1152288384.html'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        posts = response.xpath('//li[@class="postbitlegacy postbitim postcontainer"]').extract()
        topic = ''
        try:
            topic = response.xpath('//div[@class="pagetitle"]/h1/text()').extract_first()
            
        except:
            topic = 'unknown'
        for post in posts:
            comment = self.parse_post(post, topic)
            print()
            print(comment.to_string())
            db.comments.save({ 
                'author' : comment.author, 
                'text' : comment.text, 
                'date' : comment.date, 
                'topic' : comment.topic
            }) 
            

    def parse_post(self, post, topic):
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