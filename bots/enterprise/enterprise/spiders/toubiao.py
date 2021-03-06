import scrapy, json
from utils.webpage import log_empty_fields, get_url_host, get_url_param
from utils.exporter import read_cache, parse_cookies
from enterprise.items import JiekuanItem, ToubiaoItem

#################################################################################################
#                                                                                               #
# USAGE: nohup scrapy crawl toubiao -a plat_id=1 -a plat_name=ymd -a need_token=1               #
#        -a formated_url='http://www.xxx.com/api/invests?token={token}&page_index={page_index}' #
#        -a time_from=yyyy/mm/dd -a time_to=yyyy/mm/dd --loglevel=INFO --logfile=log &          #
#                                                                                               #
#################################################################################################

class ToubiaoSpider(scrapy.Spider):
    name = 'toubiao'
    allowed_domains = []
    start_formated_url = None
    pipeline = ['UniqueItemPersistencePipeline']

    def __init__(self, plat_id=None, plat_name=None, need_token='0', formated_url=None, time_from=None, \
                 time_to=None, *args, **kwargs):
        self.plat_id = plat_id
        self.plat_name = plat_name
        self.need_token = bool(int(need_token))
        self.start_formated_url = formated_url
        self.time_from = time_from
        self.time_to = time_to
        super(ToubiaoSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        if not (self.plat_id and self.time_from and self.time_to): return

        try:
            loans = JiekuanItem.django_model.objects.filter(plat_id=self.plat_id, status='1', \
                                                            success_time__gte=self.time_from, \
                                                            success_time__lte=self.time_to)
        except Exception as e:
            self.logger.info('Error From Filtering Loan Objects <%s>.' % e)
            return

        for jk in loans:
            if not jk.bid_id: continue
            token = ''
            lines = read_cache('tokens', (self.plat_id or 'test')+'.tk')

            if self.need_token and lines: token = lines[0]
            url = self.start_formated_url.format(id=jk.bid_id, token=token)

            from scrapy.http import Request
            cookies = parse_cookies(lines[1])
            yield Request(url, cookies=cookies, dont_filter=True)

    def parse(self, response):
        symbol = (get_url_param(response.url, 'page_index'), get_url_host(response.url), \
                  get_url_param(response.url, 'id'), response.url)
        self.logger.info('Parsing No.%s Page %s Invest Info About %s BidId From <%s>.' % symbol)

        try:
            content = json.loads(response.body_as_unicode())
            if int(content.get('result_code', 0)) != 1:
                raise ValueError
        except Exception:
            self.logger.info('Response Error In No.%s Page %s Invest Info About %s BidId From <%s>.' % symbol)
            return None

        item_list = []
        for dt in content.get('data', []):
            item = ToubiaoItem()
            item['invest_id'] = dt.get('invest_id')
            item['bid_id'] = dt.get('id')
            item['plat_id'] = self.plat_id
            item['plat_name'] = self.plat_name
            item['user_id'] = dt.get('user_id')
            item['username'] = dt.get('username')
            item['amount'] = dt.get('amount')
            item['valid_amount'] = dt.get('valid_amount')
            item['add_date'] = dt.get('add_date')
            item['status'] = dt.get('status')
            item['type'] = dt.get('type')
            item['url'] = dt.get('url')

            log_empty_fields(item, self.logger)
            item_list.append(item)

        return item_list
