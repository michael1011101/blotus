import scrapy, json
from utils.webpage import log_empty_fields, get_url_param
from utils.exporter import read_cache
from utils.hmacsha1 import get_unix_time, get_access_signature
from aif.items import MeiriItem

############################################################################################################################
#                                                                                                                          #
# USAGE: nohup scrapy crawl meiri -a plat_id=1 -a need_token=1 -a formated_url='http://api.xxx.com/interface-dailydata?    #
#        token={token}&from_date=yyyy-mm-dd&to_date=yyyy-mm-dd&page_size=100&page_index=1' --loglevel=INFO --logfile=log & #
#                                                                                                                          #
############################################################################################################################

class MeiriSpider(scrapy.Spider):
    name = 'meiri'
    allowed_domains = ['zwgt.com', 'order.ddsoucai.com']
    start_formated_url = None
    pipeline = ['UniqueItemPersistencePipeline']

    def __init__(self, plat_id=None, method='0', need_token='0', formated_url='', password=None, from_date='2016-09-27', to_date='2016-09-28', page_size=20, page_index=1, *args, **kwargs):
        self.plat_id = plat_id
        self.method = bool(int(method))
        self.need_token = bool(int(need_token))
        self.start_formated_url = formated_url
        self.password = password
        self.from_date = from_date
        self.to_date = to_date
        self.page_size = str(page_size)
        self.page_index = str(page_index)

        super(MeiriSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        if self.need_token:
            token = ''
            lines = read_cache('tokens', (self.plat_id or 'token')+'.tk')

            if self.need_token and lines: token = lines[0]

            timestamp = get_unix_time()
            signature = get_access_signature(token, timestamp, self.password)

            body = {'token': token, 'timestamp': timestamp, 'signature': signature, 'from_date': self.from_date, 'to_date': self.to_date, 'page_size': self.page_size, 'page_index': self.page_index}

            yield scrapy.FormRequest(self.start_formated_url, formdata=body)
        else:
            if self.method:
                yield scrapy.FormRequest(self.start_formated_url.format(page_size=self.page_size, page_index=self.page_index, from_date=self.from_date, to_date=self.to_date), method='GET')
            else:
                body = {'from_date': self.from_date,'to_date': self.to_date, 'page_size': self.page_size, 'page_index': self.page_index}
                yield scrapy.FormRequest(self.start_formated_url, formdata=body)

    def parse(self, response):
        symbol = (self.plat_id, get_url_param(response.request.body, 'from_date'), get_url_param(response.request.body, 'to_date'), response.url)
        self.logger.info('Parsing No.%s Plat [%s, %s] Daily Data From <%s>.' % symbol)

        try:
            content = json.loads(response.body_as_unicode())
            internal_content = content.get('data', {})
            if int(content.get('result_code', -1)) != 1 or not internal_content:
                raise ValueError
        except Exception:
            self.logger.warning('Fail To Receive No.%s Plat Basic Data From <%s>.' % symbol)
            return None

        item_list = []
        for dd in internal_content:
            item = MeiriItem()
            item['plat_id'] = self.plat_id
            item['date'] = dd.get('current_date')
            item['daily_turnover'] = dd.get('daily_turnover')
            item['daily_trade_cnt'] = dd.get('daily_trade_cnt')
            item['daily_invest_cnt'] = dd.get('daily_invest_cnt')
            item['thityday_income'] = dd.get('thityday_income')
            item['service_time'] = dd.get('service_time')

            log_empty_fields(item, self.logger)
            item_list.append(item)

        return item_list
