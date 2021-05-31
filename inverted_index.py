import os
import xml.etree.ElementTree as parser
from collections import defaultdict
from flask import Flask, render_template, request
import json
from datetime import datetime
from sys import getsizeof
from collections import deque

app = Flask(__name__)


def removeCh(word):
    remove = " .(,)!?=\<>1\"2345;+[]%:'67890/"
    for i in remove:
        word = word.replace(i, '')
    return word


def tokenize(content):
    if not content:
        return []
    stop_words = readwords('stoplist.txt')
    tokens = deque(content.strip().split())
    result = []
    while tokens:
        token = removeCh(tokens.popleft().strip().lower())
        if '-' in token:
            tokens += token.split('-')
        elif '\n' in token:
            tokens += token.split('\n')
        else:
            if token not in stop_words and len(token) > 2:
                result += token,
    return result


app.config['UPLOAD_FOLDER'] = './'


@app.route('/SearchEngine', methods=['GET', 'POST'])
def inverted_index_gen():
    a = datetime.now()
    if request.method != 'POST':
        return
    file = request.files['file']
    e = parser.parse(file).getroot()
    inverted_index = defaultdict(set)
    for i in e.findall('./RECORD'):
        for j in i.findall('./RECORDNUM'):
            for k in i.findall('./AUTHORS/AUTHOR'):
                author = tokenize(k.text)
                for l in author:
                    inverted_index[l].add(int(j.text))
            for k in i.findall('./MAJORSUBJ/TOPIC'):
                major = tokenize(k.text)
                for l in major:
                    inverted_index[l].add(int(j.text))
            for k in i.findall('./MINORSUBJ/TOPIC'):
                minor = tokenize(k.text)
                for l in minor:
                    inverted_index[l].add(int(j.text))
            for k in i.findall('./ABSTRACT'):
                abstract = tokenize(k.text)
                for l in abstract:
                    inverted_index[l].add(int(j.text))
            for k in i.findall('./TITLE'):
                title = tokenize(k.text)
                for l in title:
                    inverted_index[l].add(int(j.text))
            for k in i.findall('REFERENCES/CITE'):
                publication = tokenize(k.get('publication'))
                author = tokenize(k.get('author'))
                for l in publication:
                    inverted_index[l].add(int(j.text))
                for l in author:
                    inverted_index[l].add(int(j.text))
            for k in i.findall('CITATIONS/CITE'):
                publication = tokenize(k.get('publication'))
                author = tokenize(k.get('author'))
                for l in publication:
                    inverted_index[l].add(int(j.text))
                for l in author:
                    inverted_index[l].add(int(j.text))
    result = {key: sorted(inverted_index[key]) for key in sorted(inverted_index)}
    time = datetime.now() - a
    size = getsizeof(json.dumps(result, default=serialize_sets))
    return render_template('inverted_index.html', segment_details=result, time_taken=time, file_size=size)


def serialize_sets(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


def readwords(filename):
    filename = os.path.join(filename)
    f = open(filename)
    words = [line.rstrip() for line in f.readlines()]
    return set(words)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('welcome.html')


if __name__ == '__main__':
    app.run()
