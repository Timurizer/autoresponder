#! /usr/bin/env python
# -*- coding:cp1251  -*-

# Note: use this for django
from .tools import *


# Note: and this to work with pycahrm
# from tools import *


def answer_input():
    '''
    ���������� 5 ��������� ����� question, answer, confidence
    ���� ������� � ����������
    '''

    conn = sqlite3.connect(dbname)
    annoy_index = AnnoyIndexer()
    model = models.Doc2Vec.load(model_path)
    annoy_index.load(annoy_path)
    annoy_index.model = model

    print("������� ������: ")
    question = str(input())
    question = preprocess_text(question)

    inferred_vector = model.infer_vector(question)
    sims = model.most_similar([inferred_vector], topn=5, indexer=annoy_index)

    triples = list()
    for i in range(0, len(sims)):
        result = select_from_db(conn, tag_to_id(sims[i][0]))
        result.append(sims[i][1])
        triples.append(result)

    return triples


def answer(question, top_n=5):
    '''
    ��������� ������ question � ���������� top_n
    ��������� ����� question, answer, confidence
    '''
    conn = sqlite3.connect(dbname)
    annoy_index = AnnoyIndexer()
    model = models.Doc2Vec.load(model_path)
    annoy_index.load(annoy_path)
    annoy_index.model = model

    question = preprocess_text(question)

    inferred_vector = model.infer_vector(question)
    sims = model.most_similar([inferred_vector], topn=top_n, indexer=annoy_index)

    triples = list()
    for i in range(0, len(sims)):
        result = select_from_db(conn, tag_to_id(sims[i][0]))
        result.append(sims[i][1])
        triples.append(result)

    return triples
