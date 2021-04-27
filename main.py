import xml.etree.ElementTree as parser
import pysolr
from flask import Flask, render_template, request
from collections import deque
import glob
import os
import pandas as pd

app = Flask(__name__)


def readwords(filename):
    filename = os.path.join(filename)
    f = open(filename)
    words = [line.rstrip() for line in f.readlines()]
    return set(words)

def removeCh(word):
    remove = " .(,)!?=\<>1\"2345;+[]%:'67890/"
    for i in remove:
        word = word.replace(i, '')
    return word


def tokenize(content):
    if not content:
        return []
    stop_words = readwords('static/stoplist.txt')
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


@app.route('/result', methods=['POST'])
def top_results():
    if request.method != 'POST':
        return
    text = request.form['text'].lower()


    solr = pysolr.Solr('http://localhost:8983/solr/LyricsData', always_commit=True)

    # li = ["SONG_NAME: " + word for word in query]
    # qur = " OR ".join(li)

    results = solr.search(text,rows=10)

    return render_template('result.html', result=results)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('lyrics_search.html')


if __name__ == '__main__':
    app.run()