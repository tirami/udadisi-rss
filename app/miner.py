# -*- coding: utf-8 -*-

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
    if 'description' in entry:
        return entry['description']
    if 'summary' in entry:
        return entry['summary']
    return ""


def get_link(entry):
    uri = entry['links'][0]['href']
    return uri

year_regex = re.compile(r'^\d{4}$')


def get_time(entry, is_science_direct):
    if is_science_direct:
        desc = entry['description']
        beg = desc.find('Publication date: ') + len('Publication date: ')
        end = desc.find('<br')
        pub_date_str = desc[beg:end].strip()
        if u'–' in pub_date_str:  # dates like June-August 2013
            date_start = pub_date_str.find(u'–') + 1
            date_str = pub_date_str[date_start:]
            # print date_str
            dt = datetime.strptime(date_str, '%B %Y')
        elif year_regex.match(pub_date_str):  # perhaps it's just a year, lie 1984
            # print pub_date_str
            dt = datetime.strptime(pub_date_str, '%Y')
        else:  # assume format like August 2013
            # print pub_date_str
            dt = datetime.strptime(pub_date_str, '%B %Y')
        return dt
    else:
        if 'published_parsed' in entry:
            t = entry['published_parsed']
        elif 'updated_parsed' in entry:
            t = entry['updated_parsed']
        dt = datetime.fromtimestamp(time.mktime(t))
        return dt


def is_science_direct(url):
    return 'rss.sciencedirect.com' in url


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
            is_sd = is_science_direct(url)
            try:
                feed = feedparser.parse(url)
                for entry in feed['entries']:
                    created_time = get_time(entry, is_sd)
                    text = get_summary(entry)  # not currently being mined
                    url = get_link(entry)
                    if text:
                        self.mine(text, created_time, url)
                    else:
                        self.mine_url(url, time)

            except Exception as e:
                print e.message, e.args
        self.log("Mining Complete")

    def stop(self):
        self.log("Stopping mining.")

    def log(self, text):
        print "Miner:{} - {}".format(self.category.id, text)

    def mine(self, text, time_created, link_url):
        try:
            terms_dict = extract.extract_terms(text)
            now = datetime.now().strftime('%Y%m%d%H%M')
            t = time_created.strftime('%Y%m%d%H%M')
            post = RssMiner.dict_of_post(link_url, terms_dict, t, now)
            batch = RssMiner.package_batch_to_json(self.category.id, [post])
            self.send_to_parent(self.category.parent_id, batch)
            self.mined_posts_hashes.append(hash)
        except Exception as e:
            print e.message, e.args

    def mine_url(self, url, time_created):
        try:
            visible_text, last_modified = self.download_page(url)
            text_hash = hashlib.sha1(url.encode('utf-8'))
            self.log("Mining link at " + url)
            if text_hash not in self.mined_posts_hashes:
                self.mine(visible_text, time_created, url)
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
