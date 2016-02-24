from collections import defaultdict
import nltk
from nltk.corpus import stopwords
import HTMLParser
import re

stop = stopwords.words('english') + stopwords.words('spanish')
tags_to_remove = ['PRP', 'PRP$', 'RP', 'TO', 'IN']


def remove_rt(text):
    return text.replace('RT', '')


def unescape_html_chars(text):
    h = HTMLParser.HTMLParser()
    return h.unescape(text)


def remove_urls(text):
    url_re = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_re, '', text, flags=re.MULTILINE)


def remove_non_whitelisted_characters(text):
    # regex = re.compile('[^@a-zA-Z ]')
    # return regex.sub(' ', text)
    return text


def remove_twitter_usernames(text):
    regex = re.compile('@\w*')
    return regex.sub(' ', text)


def remove_stopwords(tagged):
    terms = [word for word in tagged if word.lower() not in stop and len(word) > 1]
    return terms


def extract_terms(text):
    text = remove_urls(text)
    text = unescape_html_chars(text)
    text = remove_twitter_usernames(text)
    text = remove_rt(text)
    text = remove_non_whitelisted_characters(text)
    tokens = text.split(' ')
    terms = remove_stopwords(tokens)
    rtn = defaultdict(int)
    for term in terms:
        rtn[term] += 1
    return rtn
