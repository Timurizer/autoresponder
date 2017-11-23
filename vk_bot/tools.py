# -*- coding:cp1251  -*-


import nltk
import string
import pymorphy2
from nltk.corpus import stopwords
import sqlite3
from gensim.similarities.index import AnnoyIndexer
import gensim.models as models
import os

'''
Пути к базе данных, а так же путь
к выбранным мной модели d2v и файлу для подргузки annoy
'''

basepath = os.path.dirname(__file__)
dbname = os.path.abspath(os.path.join(basepath, "db.sqlite3"))
model_path = os.path.abspath(os.path.join(basepath, "dtv_model"))
annoy_path = os.path.abspath(os.path.join(basepath, "annoy_index"))

stop_words = set(stopwords.words('russian'))
stop_words.update(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на', '...', '``', "''", '..'])
stop_words.update(list('!"#$%&\'()*+,-./:;<=>? @[\]^_`{|}~£'))
morph = pymorphy2.MorphAnalyzer()


def tokenize(text):
    '''
    Разбивает текст на токены и исключает все стоп слова
    '''

    tokens = nltk.word_tokenize(text.lower())
    tokens = [i for i in tokens if (i not in string.punctuation)]
    tokens = [i for i in tokens if (i not in stop_words)]
    tokens = [i.replace("«", "").replace("»", "") for i in tokens]
    return tokens


def lemmatize(word):
    '''
    Лемматизирует слово
    '''
    p = morph.parse(word)[0]
    return p.normal_form


def lemmatize_text(text):
    '''
    Лемматизирует весь текст
    '''
    result = list()
    for i in text:
        result.append(lemmatize(i))
    return result


def split_by_sentence(text):
    '''
    Разбивает текст на предложения
    '''
    return nltk.tokenize.sent_tokenize(text)


def preprocess_sentences(sentences):
    '''
    Делает препроцессинг для всех предложений,
    возвращает лист препроцесснутых слов
    '''
    result = list()
    for sentence in sentences:
        result.append(lemmatize_text(tokenize(sentence)))
    return result


def preprocess_text(text):
    '''
    Препроцессинг данных для doc2vec
    '''
    result = list()
    temp = preprocess_sentences(split_by_sentence(text))
    for i in temp:
        result += i
    return result


def tag_to_id(tag):
    '''
    Преобразует тэг, полученный в результате
    поиска похожих текстов в целое число, которое
    является индексом в базе данных
    '''
    return int(tag[:-1])
