# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test import Client
from .models import *
from .autoresponder.answerer import *
import sqlite3

'''
Так как я не пользуюсь всеми возможностями моделей django,
тесты моделей проводятся только на корректное представление данных
'''


class QuestionModelTests(TestCase):
    def test_string_representation(self):
        entry = Question(question="my question", answer="my answer")
        self.assertEqual(str(entry), entry.question)


class QuestionPreprocessedModelTests(TestCase):
    def test_string_representation(self):
        entry = QuestionPreprocessed(question="My preprocessed question", answer="my preprocessed answer")
        self.assertEqual(str(entry), entry.question)


class ViewsTest(TestCase):
    '''
    Тесты вьюшек
    '''

    my_string = "строка"
    count = 3

    def test_root(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_ask_question(self):
        client = Client()
        response = client.get('/answerer/autoresponder/' + self.my_string + '/')
        self.assertEqual(response.status_code, 200)

        response = client.get('/answerer/autoresponder/' + self.my_string + '/' + str(self.count) + '/')
        self.assertEqual(response.status_code, 200)


class TestPreprocess(TestCase):
    '''
    Тесты всего, связанного с препроцессингом
    '''

    my_string = "Это моя тестовая строка"

    def test_tokenize(self):
        tokenized = tokenize(self.my_string)
        self.assertTrue(type(tokenized) is list)
        self.assertTrue(len(tokenized) > 0)
        self.assertTrue(type(tokenized[0]) is str)

    def test_lemmatize_text(self):
        tokenized_string = tokenize(self.my_string)
        lemmatized_string = lemmatize_text(tokenized_string)
        self.assertEqual(len(tokenized_string), len(lemmatized_string))

    def test_tag_to_id(self):
        model = models.Doc2Vec.load(model_path)
        preprocessed = preprocess_text(self.my_string)
        vector = model.infer_vector(preprocessed)
        sims = model.docvecs.most_similar([vector], topn=1)
        id = tag_to_id(sims[0][0])
        self.assertTrue(type(id) is int)

    def test_preprocess_text(self):
        result = preprocess_text(self.my_string)
        self.assertTrue(type(result) is list)
        for word in result:
            self.assertTrue(type(word is str))


class TestAnswerer(TestCase):
    '''
    Тест основного метода поиска самых похожих
    '''
    my_string = "Это моя тестовая строка"
    count = 3

    def test_answer(self):
        result = answer(self.my_string, self.count)
        self.assertTrue(len(result) == self.count)
        self.assertTrue(type(result[0][0]) is str)
        self.assertTrue(type(result[0][1]) is str)
        self.assertTrue(type(result[0][2]) is float)


class SQLiteTests(TestCase):
    '''
    Тесты работы с базой данных через sqlite3
    '''

    dbpath = os.path.abspath(os.path.join(basepath, "..", "..", "test_database.db"))

    def setUp(self):
        """
        Создание тестовой базы данных и ее заполнение
        """

        conn = sqlite3.connect(self.dbpath)
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE answerer_question
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, question text, answer text)
                   """)

        quas = [('вопрос1', 'ответ1'),
                ('вопрос2', 'ответ2'),
                ('вопрос3', 'ответ3'),
                ('вопрос4', 'ответ4'),
                ('вопрос5', 'ответ5'),
                ('вопрос6', 'ответ6'),
                ]
        cursor.executemany("INSERT INTO answerer_question (question, answer) VALUES (?,?)",
                           quas)
        conn.commit()

    def test_select(self):
        conn = sqlite3.connect(self.dbpath)
        data = select_from_db(conn, 1)
        self.assertEqual(data[0], 'вопрос1')
        data = select_from_db(conn, 4)
        self.assertEqual(data[1], 'ответ4')

    def test_search(self):
        conn = sqlite3.connect(self.dbpath)
        data = search_in_db(conn, 'вопрос1')
        self.assertEqual(data[1], 'ответ1')
        data = search_in_db(conn, 'вопрос4')
        self.assertEqual(data[1], 'ответ4')

    def test_insert(self):
        conn = sqlite3.connect(self.dbpath)
        insert_to_db(conn, 'новый вопрос', 'новый ответ')
        data = search_in_db(conn, 'новый вопрос')
        self.assertEqual(data[1], 'новый ответ')

    def tearDown(self):
        """
        Удаление базы данных
        """

        os.remove(self.dbpath)


class ModelCreationTest(TestCase):
    '''
    Тест создания модели doc2vec
    '''

    quas = [('вопрос1', 'ответ1', 1),
            ('вопрос2', 'ответ2', 2),
            ('вопрос3', 'ответ3', 3),
            ('вопрос4', 'ответ4', 4),
            ('вопрос5', 'ответ5', 5),
            ('вопрос6', 'ответ6', 6),
            ]

    dbpath = os.path.abspath(os.path.join(basepath, "..", "..", "test_model_database.db"))
    model_name = os.path.abspath(os.path.join(basepath, "..", "..", "test_model"))

    def setUp(self):
        """
        Создание тестовой базы данных и ее заполнение
        Создание модели d2v с параметром iters=1 для скорости
        """
        conn = sqlite3.connect(self.dbpath)
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE answerer_questionpreprocessed
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, question text, answer text, original INTEGER)
                   """)

        cursor.executemany("INSERT INTO answerer_questionpreprocessed (question, answer, original) VALUES (?,?,?)",
                           self.quas)
        conn.commit()

        train_d2v(self.dbpath, model_name=self.model_name, iters=1)

    def test_model_creation(self):
        model = models.Doc2Vec.load(self.model_name)
        self.assertEqual(len(self.quas) * 2, len(model.docvecs))

    def tearDown(self):
        """
        Удаление модели
        Удаление базы данных
        """

        os.remove(self.dbpath)
        os.remove(self.model_name)
