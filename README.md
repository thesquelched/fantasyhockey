fantasyhockey
=============

Tools and data for Yahoo Fantasy Hockey 2016-17 Season

Data
----

- `data/corsica' - Corsica data
    - `skater_3yr_all.csv' - 3-year skater data, all situations
    - `skater_3yr_5v4.csv' - 3-year skater data, 5 on 4
    - `skater_3yr_5v3.csv' - 3-year skater data, 5 on 3
- `data/yahoo.csv' - Yahoo draft analysis for 2016-17 season, including position eligibility

Scripts
-------

Scripts require python 3.5 or higher.  To install requirements:

```bash
$ pyvenv-3.5 .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Included scripts:

- `spiders` - Scrapy spiders
