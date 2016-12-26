# -*- coding: utf-8 -*-
import scrapy
from utils.webpage import get_content, get_trunk
from p2peye.items import FeatureItem

##############################################################################################
#                                                                                            #
# USAGE: nohup scrapy crawl biaoqian -a from_id=1 -a to_id=1 --loglevel=INFO --logfile=log & #
#                                                                                            #
##############################################################################################


class BiaoqianSpider(scrapy.Spider):
    name = "biaoqian"
    allowed_domains = ["p2peye.com"]
    start_formated_url = "http://licai.p2peye.com/search/z0b0r0c0x0y0t0m0q0s0p{page_id}.html"
    pipeline = ['UniqueItemPersistencePipeline']

    def __init__(self, from_id=1, to_id=1, *args, **kwargs):
        self.shortlist = xrange(int(from_id), int(to_id)+1)
        super(BiaoqianSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for page in self.shortlist:
            url = self.start_formated_url.format(page_id=page)
            yield self.make_requests_from_url(url)

    def get_pin_from_url(self, url):
        purl = url.split('/')
        while not purl[-1]: purl.pop()

        return purl.pop().split('.')[0]

    def parse(self, response):
        self.logger.info('Parsing p2peye Tag From <%s>.' % response.url)

        features = []
        platforms = response.xpath('//ul[@class="mod-result"]/li')
        for platform in platforms:
            item = FeatureItem()
            item['link'] = get_content(platform.xpath('div/div/a/@href').extract())
            item['pin'] = self.get_pin_from_url(item['link'])
            item['name'] = get_content(platform.xpath('div/div/a/@title').extract())
            item['feature'] = '#'.join([get_trunk(tag) for tag in platform.xpath('div/span[@class="addinterest_blue"]/text()').extract()])
            features.append(item)
        return features
