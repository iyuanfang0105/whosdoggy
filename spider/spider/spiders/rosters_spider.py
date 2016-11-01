# coding:utf-8
import scrapy

from spider.items import RosterItem


class RostersSpider(scrapy.Spider):
    name = "rosters"

    def start_requests(self):
        urls = [
            'http://www.360doc.com/content/12/0630/22/178233_221426569.shtml',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        dog_blocks = response.css('td > div[align=center]')
        for block in dog_blocks:
            name = block.css('::text').extract_first()
            thumb = block.css('img::attr(src)').extract_first()

            if name is None or name.strip() == '' or thumb is None:
                continue

            item = RosterItem()
            item['thumb'] = thumb
            item['name'] = name.split()[0]
            item['alias'] = []
            yield item

            baidu_url = 'https://www.baidu.com/s?wd=' + item['name']
            yield scrapy.Request(baidu_url, callback=self.parse_baike_link)

    def parse_baike_link(self, response):
        links = response.css('div > h3 > a')
        for link in links:
            if len(link.css('::text').re(ur'_百度百科')) == 1:
                baike_url = link.css('::attr(href)').extract_first()
                yield scrapy.Request(baike_url, callback=self.parse_baike_alias)

    def parse_baike_alias(self, response):
        categories = response.css('div.basic-info').css('dl > dt')
        name = categories[0].xpath('string(following-sibling::dd[1])').extract_first().strip('\n')
        for category in categories:
            if len(category.css('::text').re(ur'别\s+称')) == 1:
                alias_desc = category.xpath('string(following-sibling::dd[1])').extract_first().strip('\n')
                if alias_desc.find(u'、') != -1:
                    alias_list = alias_desc.split(u'、')
                elif alias_desc.find(u'，') != -1:
                    alias_list = alias_desc.split(u'，')
                else:
                    alias_list = [alias_desc]

                item = RosterItem()
                item['thumb'] = ''
                item['name'] = name
                item['alias'] = alias_list
                yield item