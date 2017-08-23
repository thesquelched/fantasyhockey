import scrapy
import re


base_url = 'https://hockey.fantasysports.yahoo.com'


class YahooFantasyHockeySpider(scrapy.Spider):
    name = 'yahoofantasyhockey'
    allowed_domains = ['hockey.fantasysports.yahoo.com']
    start_urls = ['https://hockey.fantasysports.yahoo.com/hockey/draftanalysis?pos=ALL']

    def parse(self, response):
        for row in response.css('table#draftanalysistable tr')[1:]:
            yield dict(zip(
                ('name', 'positions', 'avg_pick', 'avg_round', 'pct_drafted'),
                self.parse_player(row)
            ))

        url = response.xpath('//a[contains(., "Next 50")]/@href').extract_first()
        if url:
            yield scrapy.Request(base_url + url, callback=self.parse)

    def parse_player(self, row):
        td_name, *rest = row.css('td')
        name = td_name.css('a.name::text').extract_first()

        pos_raw = td_name.css('span.Fz-xxs::text').extract_first()
        positions = re.split('\s*-\s*', pos_raw, maxsplit=1)[-1]

        dpick, dround, dpct = [td.css('::text').extract_first() for td in rest]

        return name, positions, dpick, dround, dpct
