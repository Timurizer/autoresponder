# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from rest_framework.decorators import api_view

from .autoresponder.answerer import answer


@api_view()
def ask_question(request, question, count=5):
    """
        Responces the question.

    """
    question = question.replace("_", " ")
    triple = answer(question, int(count))
    result = ""
    for i in triple:
        result += "Question: " + i[0] + "</br>\nAnswer: " + i[1] + "</br>\nConfidence: " + str(i[2]) + "</br>\n"
        result += "-" * 15 + "</br>\n"

    return HttpResponse(result)
