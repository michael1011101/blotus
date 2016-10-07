import scrapy, json
from utils.webpage import log_empty_fields, get_url_param
from utils.exporter import read_cache
from utils.hmacsha1 import get_unix_time, get_access_signature
from aif.items import JibenItem

#################################################################################################
#                                                                                               #
# USAGE: nohup scrapy crawl jiben -a plat_id=1 -a need_token=1                                  #
#        -a formated_url='http://api.xxx.com/interface-basicdata?token={token}&date=yyyy-mm-dd' #
#        --loglevel=INFO --logfile=log &                                                        #
#                                                                                               #
#################################################################################################

class JibenSpider(scrapy.Spider):
    name = 'jiben'
    allowed_domains = ['zwgt.com', 'order.ddsoucai.com']
    start_formated_url = None
    pipeline = ['UniqueItemPersistencePipeline']

    def __init__(self, plat_id=None, need_token='0', formated_url='', password=None, date=None, *args, **kwargs):
        self.plat_id = plat_id
        self.need_token = bool(int(need_token))
        self.start_formated_url = formated_url
        self.password = password
        self.date = date

        super(JibenSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        if self.need_token:
            token = ''
            lines = read_cache('tokens', (self.plat_id or 'token')+'.tk')

            if self.need_token and lines: token = lines[0]

            timestamp = get_unix_time()
            signature = get_access_signature(token, timestamp, self.password)

            body = {'token': token, 'timestamp': timestamp, 'signature': signature, 'date': self.date}

            yield scrapy.FormRequest(self.start_formated_url, formdata=body)
        else:
            body = {'date': self.date}

            yield scrapy.FormRequest(self.start_formated_url, formdata=body)
        #url = self.start_formated_url.format(token=token)

        #yield self.make_requests_from_url(url)

    def parse(self, response):
        symbol = (self.plat_id, response.url)
        self.logger.info('Parsing No.%s Plat Basic Data From <%s>.' % symbol)

        try:
            content = json.loads(response.body_as_unicode())
            internal_content = content.get('data', {})[0]
            if int(content.get('result_code', -1)) != 1 or not internal_content:
                raise ValueError
        except Exception:
            self.logger.warning('Fail To Receive No.%s Plat Basic Data From <%s>.' % symbol)
            return None

        item = JibenItem()
        item['plat_id'] = self.plat_id
        item['date'] = get_url_param(response.request.body, 'date')
        item['turnover_amount'] = internal_content.get('turnover_amount')
        item['unconventional_turnover_amount'] = internal_content.get('unconventional_turnover_amount')
        item['trade_amount'] = internal_content.get('trade_amount')
        item['borrower_amount'] = internal_content.get('borrower_amount')
        item['investor_amount'] = internal_content.get('investor_amount')
        item['different_borrower_amount'] = internal_content.get('different_borrower_amount')
        item['different_investor_amount'] = internal_content.get('different_investor_amount')
        item['loan_balance'] = internal_content.get('loan_balance')
        item['avg_full_time'] = internal_content.get('avg_full_time')
        item['product_overdue_rate'] = internal_content.get('product_overdue_rate')
        item['overdue_loan_amount'] = internal_content.get('overdue_loan_amount')
        item['compensatory_amount'] = internal_content.get('compensatory_amount')
        item['loan_overdue_rate'] = internal_content.get('loan_overdue_rate')

        log_empty_fields(item, self.logger)
        return item
