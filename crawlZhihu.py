#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-05-27 22:38:18
# Project: zhihu

import MySQLdb
import random
import string
import sys
from pyspider.libs.base_handler import *

reload(sys)
sys.setdefaultencoding('utf8')

class Handler(BaseHandler):
    crawl_config = {
        'headers' : {
            'User-Agent' : 'GoogleBot',
            'Host' : 'www.zhihu.com'
        }
    }
    
    def __init__(self):
        self.db = MySQLdb.connect('localhost', 'root', 'root', 'wenda', charset='utf8')

        
    def add_question(self, title, content, comment_count):
        try:
            cursor = self.db.cursor()
            sql = 'insert into question(title, content, user_id, created_date, comment_count) values ("%s", "%s", %d, %s, %d)' % (title, content, random.randint(1, 10) , 'now()', comment_count);
            print sql
            cursor.execute(sql)
            qid = cursor.lastrowid
            self.db.commit()
            return qid
        except Exception, e:
            print e
            self.db.rollback()
        
    def add_comment(self, qid, comment):
        try:
            cursor = self.db.cursor()
            sql = 'insert into comment(content, entity_type, entity_id, user_id, created_date) values("%s", 1, %d, %d, %s)' % (comment, qid, random.randint(1, 10), 'now()')
            print sql
            cursor.execute(sql)
            self.db.commit()
        except Exception, e:
            print e
            self.db.rollback()
          
    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.zhihu.com/topic/19664655/top-answers', callback=self.index_page, validate_cert=False)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a.question_link').items():
            self.crawl(each.attr.href, callback=self.detail_page, validate_cert=False)
        for each in response.doc('div.zm-invite-pager span a').items():
            self.crawl(each.attr.href, callback=self.index_page, validate_cert=False)

    @config(priority=2)
    def detail_page(self, response):
        title = response.doc('h1.QuestionHeader-title').html()
        html = response.doc('div.QuestionHeader-detail span.RichText').html()
        if html == None:
            content = ''
        else:
            content = html.replace('"','\'"\'')
        comment_count = response.doc('h4.List-headerText>span').text()
        comment_count = string.atoi(comment_count[0:comment_count.find('¸ö')])
        qid = self.add_question(title, content, comment_count)
        items = response.doc('span.RichText.CopyrightRichText-richText').items()
        for each in response.doc('span.RichText.CopyrightRichText-richText').items():
            self.add_comment(qid, each.html().replace('"','\'"\''))
                             
        return {
            "url": response.url,
            "title": title,
            "content": content,
        }
