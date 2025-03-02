import json
import sqlite3

connection = sqlite3.connect('quotes.sqlite')
cursor = connection.cursor()
cursor.execute('Create Table if not exists Quotes (quote_text Text, author Text)')

quotes = json.load(open('xpath-scraper-results.json'))
print(quotes)

columns = ['text', 'author']

for row in quotes:
    print(row)
    keys = tuple(row[c] for c in columns)
    print(keys)

    # exit()
    cursor.execute('insert into Quotes values(?,?)', keys)
    print(f'{row["text"]} data inserted successfully')


connection.commit()
connection.close()