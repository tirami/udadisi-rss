from BeautifulSoup import BeautifulSoup
from collections import defaultdict
import base64
import feedparser
import json
import nltk
import sys
import time
from time import mktime
import urllib
import urllib2

mined_posts_hashes = []

def get_summary(entry):
    summary = entry['summary']
    return summary


def get_link(entry):
    uri = entry['links'][0]['href']
    return uri


def get_timestamp(entry):
    time_struct = entry['published_parsed']
    time_stamp = int(mktime(time_struct))
    return time_stamp


def download_page(uri):
    try:
        html = urllib.urlopen(uri).read()
        soup = BeautifulSoup(html)
        visible_text = soup.getText()
        return visible_text
    except:
        print "Error loading " + uri, sys.exc_info()
        return ""


def extract_terms(text):
    tokens = text.split(' ')
    tagged = nltk.pos_tag(tokens)
    nouns = [word for (word, type) in tagged if type == 'NN']
    terms = defaultdict(int)
    for noun in nouns:
        terms[noun] += 1
    return terms


def construct_post(terms, uri, time, mined_at, miner_name):
    post = {
        "post" : {
           "terms": terms,
           "url": uri,
           "datetime": time,
           "mined_at": mined_at
        },
        "miner_id" : miner_name
    }
    data = json.dumps(post)
    return data


def sent_to_engine(post, uri):
    req = urllib2.Request(uri, post, {'Content-Type': 'application/json'})
    try:
        urllib2.urlopen(req)
    except:
        print "Error posting to aggrigation server."


# main mining function
def run_miner(miner_name, uris, engine_uri):
    for uri in uris:
        try:
            feed = feedparser.parse(uri)
            for entry in feed['entries']:
                timestamp = get_timestamp(entry)
                text = get_summary(entry)
                uri = get_link(entry)
                hash_str = str(timestamp) + text + uri
                hash = base64.encodestring(hash_str)
                if hash not in mined_posts_hashes:
                    mined_at = int(time.time()) # now
                    if len(text) == 0:
                        # if there is no summary, try and follow the link to the site
                        text = download_page(uri)
                    terms = extract_terms(text)
                    post = construct_post(terms, uri, timestamp, mined_at, miner_name)
                    sent_to_engine(post, engine_uri)
                    mined_posts_hashes.append(hash)
                else:
                    print("Post already mined")
        except Exception as e:
            print e.message, e.args
