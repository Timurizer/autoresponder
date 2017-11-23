# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.utils.encoding import python_2_unicode_compatible

from django.db import models


# Create your models here.

@python_2_unicode_compatible
class Question(models.Model):
    '''
    Модель содержит пары вопрос-ответ
    '''
    question = models.CharField(max_length=500)
    answer = models.CharField(max_length=500)

    def __str__(self):
        return self.question



@python_2_unicode_compatible

class QuestionPreprocessed(models.Model):
    '''
    Модель содержит препроцесснутые пары вопрос-ответ
    '''
    original = models.ForeignKey(Question, on_delete=models.CASCADE)
    question = models.CharField(max_length=1200)
    answer = models.CharField(max_length=1200)

    def __str__(self):
        return self.question
