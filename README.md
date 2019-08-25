fantasyhockey
=============

Tools and data for Yahoo Fantasy Hockey.

Yahoo draft scraper
-------------------

[scrapy](LINK) scraper for Yahoo draft data, including player position, average
draft position, etc.

Install requirements with [pipenv](https://docs.pipenv.org/en/latest/).

```bash
$ pipenv install
$ pipenv shell
$ scrapy runspider spiders/yahoo.py -o yahoo.csv
```
