import scrapy, json
from utils.webpage import log_empty_fields, get_url_param
from utils.exporter import read_cache
from utils.hmacsha1 import get_unix_time, get_access_signature
from aif.items import MeiyueItem

class MeiyueSpider(scrapy.Spider):
    name = 'meiyue'
    allowed_domains = ['zwgt.com', 'order.ddsoucai.com']
    start_formated_url = None
    pipeline = ['UniqueItemPersistencePipeline']

    def __init__(self, plat_id=None, need_token='0', formated_url='', password=None, month=None, *args, **kwargs):
        self.plat_id = plat_id
        self.need_token = bool(int(need_token))
        self.start_formated_url = formated_url
        self.password = password
        self.month = month

        super(MeiyueSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        if self.need_token:
            token = ''
            lines = read_cache('tokens', (self.plat_id or 'token')+'.tk')
            if self.need_token and lines:
                token = lines[0]

            timestamp = get_unix_time()
            signature = get_access_signature(token, timestamp, self.password)
            body = {'token': token, 'timestamp': timestamp, 'signature': signature, 'month': self.month}

            yield scrapy.FormRequest(self.start_formated_url, formdata=body)
        else:
            body = {'month':self.month}
            yield scrapy.FormRequest(self.start_formated_url, formdata=body)

        #url = self.start_formated_url.format(token=token)
        #yield self.make_requests_from_url(url)

    def parse(self, response):
        #symbol = (self.plat_id, get_url_param(response.url, 'from_month'), get_url_param(response.url, 'to_month'), response.url)
        #self.logger.info('Parsing No.%s Plat [%s, %s] Monthly Data From <%s>.' % symbol)
        symbol = (self.plat_id, get_url_param(response.request.body, 'month'), response.url)
        self.logger.info('Parsing No.%s Plat %s Monthly Data From <%s>.' % symbol)

        try:
            content = json.loads(response.body_as_unicode())
            internal_content = content.get('data', {})[0]
            if int(content.get('result_code', -1)) != 1 or not internal_content:
                raise ValueError
        except Exception:
            self.logger.warning('Fail To Receive No.%s Plat Basic Data From <%s>' % symbol)

        item = MeiyueItem()
        item['plat_id'] = self.plat_id
        item['date'] = get_url_param(response.request.body, 'month')
        item['loan_amount_per_capita'] = internal_content.get('loan_amount_per_capita')
        item['avg_loan_per_trade'] = internal_content.get('avg_loan_per_trade')
        item['invest_amount_per_capita'] = internal_content.get('invest_amount_per_capita')
        item['avg_invest_per_trade'] = internal_content.get('avg_invest_per_trade')
        item['max_borrower_ratio'] = internal_content.get('max_borrower_ratio')
        item['topten_borrowers_ratio'] = internal_content.get('topten_borrowers_ratio')
        item['overdue_project_amount'] = internal_content.get('overdue_project_amount')
        item['avg_interest_rate'] = internal_content.get('avg_interest_rate')
        item['avg_borrow_period'] = internal_content.get('avg_borrow_period')

        log_empty_fields(item, self.logger)
        return item