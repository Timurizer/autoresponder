# autoresponder  
автор: Тимур Якупов

## Для запуска django:  
$ python3 questions/manage.py runserver  

### urls:  
'/' - swagger  
'/answerer/autoresponder/(?P\<question\>[\w\-]+)/' - получить 5 самых похожих вопросов  
'/answerer/autoresponder/(?P\<question\>[\w\-]+)/(?P\<count\>[0-9]+)' - получить \<count\> самых похожих вопросов
  
## Для запуска тестов:  
$ python3 questions/manage.py test answerer.tests  

## Для запуска Telegram Bot:
$ python3 telegram_bot/bot.py  
Написать боту @autoresponder_yakupov_bot

## Для запуска Vk bot:
$ python3  vk_bot/vk_bot.py   
Написать сюда https://vk.com/public157344380

## Heroku:
https://still-garden-90905.herokuapp.com  
К сожалению, не удалось подружить swagger с heroku до конца  
'try it out' не работает
