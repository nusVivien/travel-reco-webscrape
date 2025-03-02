# mec-5.5.4-webscraping-project

## Project to scrape websites using Scrapy 
As instructed, I had followed the tutorial and created 2 spider files:
(located in mec-5.5.4-webscraping-project/scrapy_mini_project/scrapy_mini_project/spiders/)
- toscrape-css.py
- toscrape-xpath.py

the 2 output files were created by calling the following commands:
- scrapy crawl toscrape-css -o css-scraper-results.json 
- scrapy crawl toscrape-xpath -o xpath-scraper-results.json

the output files created are:
(located in mec-5.5.4-webscraping-project/scrapy_mini_project/ )

## BONUS SECTION: Converting JSON file to  SQLITE DB
For the bonus section, I created the file:
- json2sqlite.py
It converts the file xpath-scraper-results.json to quotes.sqlite

now we can use sqlite3 in python to explore the quotes data