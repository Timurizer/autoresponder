#! /usr/bin/env python
# -*- coding:cp1251  -*-
from tools import *

dtv_load_path = '/Users/Timmy/Desktop/test_task/telegram_bot/doc2vec_model_tagged.dtv'


def answer(question):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    annoy_index = AnnoyIndexer()
    model = models.Doc2Vec.load(model_path)
    annoy_index.load(annoy_path)
    annoy_index.model = model

    question = preprocess_text(question)

    inferred_vector = model.infer_vector(question)
    sims = model.most_similar([inferred_vector], topn=5, indexer=annoy_index)

    triples = list()
    for i in range(0, len(sims)):
        for row in c.execute('SELECT * FROM answerer_question where id = ' + str(tag_to_id(sims[i][0]))):
            triples.append((row[1], row[2], sims[i][1]))

    return triples
