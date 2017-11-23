import pandas as pd
import sqlite3
import os

'''
Выполняет сохранение всех данных из файла vk.scv в базу данных
'''

basepath = os.path.dirname(__file__)
dbname = os.path.abspath(os.path.join(basepath, "..", "..", "db.sqlite3"))
dataset = model_path = os.path.abspath(os.path.join(basepath, "vk.scv"))

conn = sqlite3.connect(dbname)
c = conn.cursor()
count = 1
null_count = 0

data = pd.read_csv('vk.csv')
for i in range(len(data.index)):
    q = data.ix[i][1]
    a = data.ix[i][2]

    if not type(q) is float and not type(a) is float:
        c.execute('''INSERT INTO answerer_question (question, answer) VALUES (?, ?)''', (q, a))
    else:
        null_count += 1
    count += 1
    if count % 1000 == 0:
        print(count)

print("Null count = " + str(null_count))
print("qa count = " + str(count))

conn.commit()
conn.close()
