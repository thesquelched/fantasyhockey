fantasyhockey
=============

Tools and data for Yahoo Fantasy Hockey 2016-17 Season.

Data
----

- `data/corsica' - Corsica data
    - `skater_3yr_all.csv' - 3-year skater data, all situations
    - `skater_3yr_5v4.csv' - 3-year skater data, 5 on 4
    - `skater_3yr_5v3.csv' - 3-year skater data, 5 on 3
- `data/yahoo.csv' - Yahoo draft analysis for 2016-17 season, including position eligibility
- `data/skater.csv` - Joined Corsica/Yahoo data from 2013-14 through 2015-16
- `data/skater_projection.csv` - Player projections using a 4-2-1 weighted average of the previous three seasons

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

Acknowledgements
----------------

- [Corsica](http://www.corsica.hockey) for non-PIM stats
- [Yahoo](http://www.yahoo.com) for draft analysis
