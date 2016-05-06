import scrapy
from utils.webpage import get_content, get_thread_from_exposure_url
from utils.get_thread import get_max_thread_from_exposure
from exporterHelper.items import ExporterItem

######################################################################################################
#                                                                                                    #
# USAGE: nohup scrapy crawl wangjia_exposure -a from_id=1 -a to_id=1 --loglevel=INFO --logfile=log & #
#                                                                                                    #
######################################################################################################

class WangjiaExposureJsonSpider(scrapy.Spider):
    name = 'wangjia_exposure'
    allowed_domains = ['wdzj.com']
    #NOTE: (zacky, 2015.JUN.9th) URL PREFIX FOR WANGJIA EXPOSURE.
    start_formated_url = 'http://bbs.wdzj.com/forum-110-{page_id}.html'
    pipeline = ['CacheFileExporterPersistencePipeline']
    max_thread = get_max_thread_from_exposure()

    def __init__(self, from_id=1, to_id=1, *args, **kwargs):
        to_id = max(int(from_id), int(to_id))
        self.shortlist = xrange(int(from_id), int(to_id)+1)
        super(WangjiaExposureJsonSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        for i in self.shortlist:
            url = self.start_formated_url.format(page_id=i)
            yield self.make_requests_from_url(url)

    def parse(self, response):
        self.logger.info('Parsing Wangjia Exporsure URLs From <%s>.' % response.url)

        item = ExporterItem()
        elements = response.xpath('//table[starts-with(@summary, "forum")]/tbody')
        #elements = response.xpath('//div[@class="comeing_channel_tab_area"]/table/tbody')
        for ele in elements:
            content = ele.xpath('tr/th[@class="new"]')
            #content = ele.xpath('tr/td[@class="comeing_channel_threadlist_sub"]')
            if not content: continue

            url = get_content(content.xpath('a[contains(@class, "xst")]/@href').extract())
            thread = get_thread_from_exposure_url(url)
            if int(self.max_thread) < int(thread):
                item.set_record(url)

        return item
