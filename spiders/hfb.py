import scrapy
import re


class HockeysFuturePositionsSpider(scrapy.Spider):
    name = 'hockeysfuturepositions'
    allowed_domains = ['hfboards.hockeysfuture.com']
    start_urls = ['http://hfboards.hockeysfuture.com/showpost.php?p=118067873&postcount=1']

    def parse(self, response):
        for cell in response.css('table.stg_table td::text'):
            m = re.match("(?P<player>[A-z' -]+) \(\d+, (?P<position>LW|C|RW|RD|LD|G)\)", cell.extract())
            if m:
                yield {key: value.upper() for key, value in m.groupdict().items()}
