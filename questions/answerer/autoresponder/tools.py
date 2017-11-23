# -*- coding:cp1251  -*-

import sqlite3
import nltk
import string
import pymorphy2
from nltk.corpus import stopwords
import gensim.models as models
from gensim.models.doc2vec import TaggedDocument
from gensim.similarities.index import AnnoyIndexer
import os

'''
Пути к базе данных, а так же путь
к выбранным мной модели d2v и файлу для подргузки annoy
'''
basepath = os.path.dirname(__file__)
dbname = os.path.abspath(os.path.join(basepath, "..", "..", "db.sqlite3"))
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


def train_w2v(model_name='model'):
    '''
    Тренировка word2vec и сохранение модели в файл
    с именем model_name
    '''
    data = get_w2v_data()
    print("Vectorization started")
    model = models.Word2Vec(data, min_count=1)
    model.save(model_name)


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


def get_w2v_data():
    '''
    Препроцессинг данных для тренировки word2vec
    '''
    print("Preprocessing started")
    result = list()
    conn = sqlite3.connect(dbname)
    c = conn.cursor()

    count = 0
    for row in c.execute('''SELECT * FROM answerer_question'''):
        result += preprocess_sentences(split_by_sentence(row[1])) \
                  + preprocess_sentences(split_by_sentence(row[2]))
        count += 1

        if count % 1000 == 0:
            print(count)

    conn.close()
    return result


def save_preprocessed_to_db():
    '''
    Препроцессинг данных для doc2vec и их
    сохранение в базу данных для экономли времени в будущем
    '''
    print("Preprocessing started")

    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    d = conn.cursor()

    count = 0
    for row in c.execute('''SELECT * FROM answerer_question'''):
        id = int(row[0])
        preprocessed_q = ' '.join(preprocess_text(row[1]))
        preprocessed_a = ' '.join(preprocess_text(row[2]))
        d.execute('''INSERT INTO answerer_questionpreprocessed (question, answer, original_id) VALUES (?, ?, ?)'''
                  , (preprocessed_q, preprocessed_a, id))
        count += 1

        if count % 1000 == 0:
            print(count)
    print(count)
    conn.commit()
    conn.close()


def preprocess_text(text):
    '''
    Препроцессинг данных для doc2vec
    '''
    result = list()
    temp = preprocess_sentences(split_by_sentence(text))
    for i in temp:
        result += i
    return result


def train_d2v(db_path, model_name='doc2vec_model', iters=55, qonly=False):
    '''
    Обучает модель doc2veс на подготовленных данных из бд
    сохраняет полученную модель в файл
    Args:
        db_path - путь к базе данных

        model_name - название файла, в который модель будет сохранена

        qonly - true, когда тренировка doc2vec должна быть сделана
                только на вопросах

        iters - количество итераций (эпох)
    '''
    print('connecting to db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print('collecting data')
    data = list()
    count = 0
    tag = 0
    for row in c.execute('''SELECT * FROM answerer_questionpreprocessed'''):
        q = row[1].split(' ')
        data.append(TaggedDocument(q, [str(row[3]) + 'q']))

        if not qonly:
            a = row[2].split(' ')
            data.append(TaggedDocument(a, [str(row[3]) + 'a']))

        tag += 2
        count += 1
        if count % 2500 == 0:
            print(count)
    print('training doc2vec')

    model = models.doc2vec.Doc2Vec(data, size=50, min_count=1, iter=iters)
    model.save(model_name)


def tag_to_id(tag):
    '''
    Преобразует тэг, полученный в результате
    поиска похожих текстов в целое число, которое
    является индексом в базе данных
    '''
    return int(tag[:-1])


def make_annoy(model_name, num_trees=50):
    '''
    Создание индекс-файла
    '''
    model = models.Doc2Vec.load(model_name)
    annoy_index = AnnoyIndexer(model, num_trees)
    annoy_index.save('annoy_index')


def select_from_db(db_name, id):
    '''
    Выбор данных из базы данных по индексу
    '''
    c = db_name.cursor()
    result = list()
    for row in c.execute('SELECT * FROM answerer_question where id = ' + str(id)):
        result = [row[1], row[2]]
    return result


def search_in_db(db_name, question):
    '''
    Поиск в базе данных по вопросу
    '''
    c = db_name.cursor()
    result = list()
    for row in c.execute("SELECT * FROM answerer_question WHERE question like '%" + str(question) + "%'"):
        result = [row[1], row[2]]
    return result


def insert_to_db(db_name, question, answer):
    '''
    Добавление новой пары вопрос-ответ в базу данных
    '''
    c = db_name.cursor()
    c.execute('''INSERT INTO answerer_question (question, answer) VALUES (?, ?)''', (question, answer))
    db_name.commit()


def evaluate_model(model_name):
    '''
    Оценка модели doc2vec
    1 - для каждой пары вопрос-ответ преобразовать
    вопрос и ответ отдельно в векторы (для экономии времени
    используются препроцесснутые данные из БД)
    2 - найти для каждого вектора самый похожий
    3 - посмотреть по id самых похожих, совпадают ли они с оригинальными

    Выбор модели ведется на основе того, сколько пар вопрос-ответ не совпали
    совсем или совпали полностью

    returns:
        correct - совпали и вопрос, и ответ
        correct_q - совпал вопрос
        correct_a - совпал ответ
        wrong - не совпало ничего
    '''
    print('Preparing')
    model = models.Doc2Vec.load(model_name)
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    ids = list()
    most_similar_ids_q = list()
    most_similar_ids_a = list()
    correct = 0
    count = 0
    print('Executing')
    for row in c.execute('''SELECT * FROM answerer_questionpreprocessed'''):
        q = row[1].split(" ")
        a = row[2].split(" ")
        inferred_vector1 = model.infer_vector(q)
        inferred_vector2 = model.infer_vector(a)
        simsq = model.docvecs.most_similar([inferred_vector1], topn=1)
        simsa = model.docvecs.most_similar([inferred_vector2], topn=1)
        ids.append(row[3])

        most_similar_ids_q.append(tag_to_id(simsq[0][0]))
        most_similar_ids_a.append(tag_to_id(simsa[0][0]))

        count += 1
        if count % 1000 == 0:
            print(count)

    correct_q = 0
    correct_a = 0
    wrong = 0
    for i in range(len(ids)):
        if ids[i] == most_similar_ids_q[i] == most_similar_ids_a[i]:
            correct += 1
        if ids[i] == most_similar_ids_q[i]:
            correct_q += 1
        if ids[i] == most_similar_ids_a[i]:
            correct_a += 1
        if ids[i] != most_similar_ids_q[i] and ids[i] != most_similar_ids_a[i]:
            wrong += 1
    return correct, correct_a, correct_q, wrong
