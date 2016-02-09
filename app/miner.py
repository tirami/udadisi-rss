from BeautifulSoup import BeautifulSoup
from collections import defaultdict
import re
import hashlib
import json
import nltk
import sys
from datetime import datetime
import urllib
import urllib2
from threading import Thread
import extract
import operator
import feedparser
import time

from BeautifulSoup import BeautifulSoup


def get_summary(entry):
    summary = entry['summary']
    return summary


def get_link(entry):
    uri = entry['links'][0]['href']
    return uri


def get_time(entry):
    if 'published_parsed' in entry:
        t = entry['published_parsed']
    elif 'updated_parsed' in entry:
        t = entry['updated_parsed']
    dt = datetime.fromtimestamp(time.mktime(t))
    return dt


class RssMiner(Thread):
    def __init__(self, category):
        super(RssMiner, self).__init__()
        self.category = category
        self.mined_posts_hashes = []

    def run(self):
        self.log("Starting mining.")
        urls = [url.strip() for url in self.category.urls.split(',')]
        for url in urls:
            self.log("Reading feed at: " + url)
            try:
                feed = feedparser.parse(url)
                for entry in feed['entries']:
                    time = get_time(entry)
                    text = get_summary(entry)  # not currently being mined
                    url = get_link(entry)
                    self.mine_url(url, time)

            except Exception as e:
                print e.message, e.args
        self.log("Mining Complete")

    def stop(self):
        self.log("Stopping mining.")

    def log(self, text):
        print "Miner:{} - {}".format(self.category.id, text)

    def mine_url(self, url, time_created):
        try:
            visible_text, last_modified = self.download_page(url)
            text_hash = hashlib.sha1(url.encode('utf-8'))
            self.log("Mining link at " + url)
            if text_hash not in self.mined_posts_hashes:
                terms_dict = extract.extract_terms(visible_text)
                now = datetime.now().strftime('%Y%m%d%H%M')
                t = time_created.strftime('%Y%m%d%H%M')
                post = RssMiner.dict_of_post(url, terms_dict, t, now)
                batch = RssMiner.package_batch_to_json(self.category.id, [post])
                self.send_to_parent(self.category.parent_id, batch)
                self.mined_posts_hashes.append(hash)
            else:
                print("Post already mined.")

        except Exception as e:
            print e.message, e.args

    # website specific static methods
    def download_page(self, uri):
        try:
            res = urllib.urlopen(uri)
            info = dict(res.info())
            time = datetime.now()
            if 'last-modified' in info:
                time_str = info['last-modified']
                time = datetime.strptime(time_str, '%a, %d %b %Y %H:%M:%S %Z')

            html = res.read()
            soup = BeautifulSoup(html)
            text = self.find(soup, 'p') \
                    + self.find(soup, 'h1') \
                    + self.find(soup, 'h2') \
                    + self.find(soup, 'h3')

            return text, time
        except:
            print "Error loading " + uri, sys.exc_info()
            return ""

    def find(self, soup, tag):
        elements = soup.findAll(tag)
        lines = [e.text for e in elements if len(e.text) > 0]
        return ' '.join(lines)

    # standard engine communication static methods
    @staticmethod
    def send_to_parent(url, data):
        url += "/v1/minerpost"
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        try:
            urllib2.urlopen(req)
        except Exception as e:
            print "Exception while sending data to engine at the uri: {}".format(url)
            print e

    @staticmethod
    def dict_of_post(post_url, terms_dict, last_modified, mined_at):
        post = {
           "terms": terms_dict,
           "url": post_url,
           "datetime": last_modified,
           "mined_at": mined_at
        }
        return post

    @staticmethod
    def package_batch_to_json(id_of_miner, posts):
        values = {
           "posts": posts,
           "miner_id": id_of_miner
        }
        data = json.dumps(values)
        return data
