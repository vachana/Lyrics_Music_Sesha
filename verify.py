import os
import xml.etree.ElementTree as parser
from collections import deque
from collections import defaultdict
from math import log, sqrt, pow
import copy
import glob
from matplotlib import pyplot as plt


def removeCh(word):
    remove = " .(,)!?=\<>1\"2345;+[]%:'67890/"
    for i in remove:
        word = word.replace(i, '')
    return word


def readwords(filename):
    filename = os.path.join(filename)
    f = open(filename)
    words = [line.rstrip() for line in f.readlines()]
    return set(words)


def idf(inv_index, total_docs):
    idf = {}
    for key in inv_index:
        temp = len(inv_index[key]) + 1
        if temp > 0:
            idf[key] = 1 + log(total_docs / temp)
        else:
            idf[key] = 1
    return idf


def normalize_tf_cal(tf, count_doc):
    norm_tf = copy.deepcopy(tf)
    for key in tf:
        for docid in tf[key]:
            if docid in count_doc:
                norm_tf[key][docid] = tf[key][docid] / count_doc[docid]
    return norm_tf


def calc_tfidf_docs(idf_terms, tf_terms, query):
    tf_idf = copy.deepcopy(tf_terms)
    for key in tf_terms:
        for docid in tf_terms[key]:
            if key in query:
                tf_idf[key][docid] = tf_terms[key][docid] * idf_terms[key]
                # TF-IDF score for all query terms within each document
    return tf_idf


def tokenize(content):
    if not content:
        return []
    tokens = deque(content.strip().split())
    stop_words = readwords('stoplist.txt')
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


def top_results(text):
    query = tokenize(text)
    inverted_index = defaultdict(set)
    tf = {}
    total_docs = 0
    docids = set()
    for i in glob.glob('cfc-xml/*7*.xml'):
        e = parser.parse(i).getroot()
        count_docs_norml = {}
        for i in e.findall('./RECORD'):
            total_docs += 1
            c = 0
            for j in i.findall('./RECORDNUM'):
                docids.add(j.text)
                for k in i.findall('./AUTHORS/AUTHOR'):
                    author = tokenize(k.text)
                    for l in author:
                        c += 1
                        inverted_index[l].add(int(j.text))
                        if l not in tf:
                            tf[l] = defaultdict(float)
                        else:
                            tf[l][int(j.text)] += 1
                for k in i.findall('./MAJORSUBJ/TOPIC'):
                    major = tokenize(k.text)
                    for l in major:
                        c += 1
                        inverted_index[l].add(int(j.text))
                        if l not in tf:
                            tf[l] = defaultdict(float)
                        else:
                            tf[l][int(j.text)] += 1
                for k in i.findall('./MINORSUBJ/TOPIC'):
                    minor = tokenize(k.text)
                    for l in minor:
                        c += 1
                        inverted_index[l].add(int(j.text))
                        if l not in tf:
                            tf[l] = defaultdict(float)
                        else:
                            tf[l][int(j.text)] += 1
                for k in i.findall('./ABSTRACT'):
                    abstract_a = tokenize(k.text)
                    for l in abstract_a:
                        c += 1
                        inverted_index[l].add(int(j.text))
                        if l not in tf:
                            tf[l] = defaultdict(float)
                        else:
                            tf[l][int(j.text)] += 1
                for k in i.findall('./EXTRACT'):
                    abstract = tokenize(k.text)
                    for l in abstract:
                        c += 1
                        inverted_index[l].add(int(j.text))
                        if l not in tf:
                            tf[l] = defaultdict(float)
                        else:
                            tf[l][int(j.text)] += 1
                for k in i.findall('./TITLE'):
                    title = tokenize(k.text)
                    for l in title:
                        c += 1
                        inverted_index[l].add(int(j.text))
                        if l not in tf:
                            tf[l] = defaultdict(float)
                        else:
                            tf[l][int(j.text)] += 1
                count_docs_norml[int(j.text)] = c
    inv_index = {key: sorted(inverted_index[key]) for key in sorted(inverted_index)}
    idf_terms_docs = idf(inv_index, total_docs)
    norml_tf_term_docs = normalize_tf_cal(tf, count_docs_norml)
    tf_idf_term_docs = calc_tfidf_docs(idf_terms_docs, norml_tf_term_docs, query)

    tf_query = dict()
    tf_idf_query = dict()
    tf_query_normalized = copy.deepcopy(tf_query)
    for term in query:
        if term not in tf_query:
            tf_query[term] = 1
        else:
            tf_query[term] += 1
    for term in query:
        if term in tf_query:
            tf_query_normalized[term] = tf_query[term] / len(query)

    for term in query:
        if term in idf_terms_docs and term in tf_query_normalized:
            tf_idf_query[term] = idf_terms_docs[term] * tf_query_normalized[term]
    query_Val = 0

    for term in tf_idf_query:
        query_Val += (pow(tf_idf_query[term], 2))

    query_Val = sqrt(query_Val)

    tf_idf_per_doc = defaultdict(lambda: defaultdict(set))
    #
    for term in tf_idf_term_docs:
        for doc_id in tf_idf_term_docs[term]:
            tf_idf_per_doc[doc_id][term].add(tf_idf_term_docs[term][doc_id])

    doc_vals = dict()
    for doc_id in tf_idf_per_doc:
        val = 0
        for term in tf_idf_per_doc[doc_id]:
            if tf_idf_per_doc[doc_id][term] and term in query:
                a = tf_idf_per_doc[doc_id][term].copy()
                val += (pow(a.pop(), 2))
        doc_vals[doc_id] = sqrt(val)
    dot_prd = dict()

    for doc_id in tf_idf_per_doc:
        val = 0
        for term in tf_idf_per_doc[doc_id]:
            if tf_idf_per_doc[doc_id][term] and term in query:
                a = tf_idf_per_doc[doc_id][term].copy()
                val += tf_idf_query[term] * a.pop()
        dot_prd[doc_id] = sqrt(val)

    cosine_val = {}
    for doc_id in dot_prd:
        if (query_Val * doc_vals[doc_id]):
            cosine_val[doc_id] = (dot_prd[doc_id]) / (query_Val * doc_vals[doc_id])
    sorted_cos = {k: v for k, v in sorted(cosine_val.items(), key=lambda item: item[1])}
    top_10 = []
    for i in range(10):
        top_10.append(list(sorted_cos.keys())[-i])
    return top_10


def main():
    precision,recall,map_10 = [],[],[]
    queries = list(range(1, 100))
    e = parser.parse('cfc-xml\cfquery.xml').getroot()
    for i in e.findall('./QUERY'):
        for j in i.findall('./QueryText'):
            count_10, doc_id = {}, {}
            top_10 = top_results(j.text)
        for j in i.findall('./Results'):
            results = int(j.text)
        for j in i.findall('./Records/Item'):
            doc_id[j] = int(j.text)
        count = 0
        for j in top_10:
            if j in doc_id.values():
                count += 1
        k=1
        ap_10 = []
        while k < 11:
            for j in range(0, k):
                if top_10[j] in doc_id.values():
                    count += 1
            k +=1
        ap_10.append((count / k))


        precision.append(count / 10)
        recall.append(count/results)
        avg_val = sum(ap_10) / len(ap_10)
        print("AP@10", avg_val)
        map_10.append(sum(ap_10) / len(ap_10))
    print("MAP@10", sum(map_10) / 100)
    print(precision)
    print(recall)
    plt.plot(queries, precision)
    plt.plot(queries, recall)
    plt.show()


if __name__ == '__main__':
    main()
