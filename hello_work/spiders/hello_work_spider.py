import pdb
import scrapy

from hello_work.items import HelloWorkItem

"""
ターミナル内で「scrapy crawl hello_work_spider」で実行できます。
時間の関係でおおよそ420ページ、92アイテムのクロールで止めていますが、取れたデータは「information.csv」をご覧ください。
"""


class HelloWorkSpiderSpider(scrapy.Spider):
    name = 'hello_work_spider'
    allowed_domains = ['hellowork.careers']
    start_urls = ['https://www.hellowork.careers/category']

    def parse(self, response):
        for pref in response.css('table#states td'):
            pref_href = pref.css('a ::attr("href")').get()
            pref_url = response.urljoin(pref_href)
            yield scrapy.Request(pref_url, callback=self.parse_city)

    def parse_city(self, response):
        for city in response.css('p.city'):
            city_href = city.css('a ::attr("href")').get()
            city_url = response.urljoin(city_href)
            yield scrapy.Request(city_url, callback=self.only_hello_work)

    def only_hello_work(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            formcss='div#only-helloworktxt > form > input:nth-of-type(4)',
            dont_click=True,
            callback=self.parse_job_offer
        )

    def parse_job_offer(self, response):
        for job_offer in response.css('div.row'):
            job_offer_href = job_offer.css('h2.jobtitle > a ::attr("href")').get()
            job_offer_url = response.urljoin(job_offer_href)
            yield scrapy.Request(job_offer_url, callback=self.parse_detail)

        next_page_url = response.css('div.pagination > span.link:nth-last-of-type(1) > a ::attr("href")').get()
        if next_page_url is not None:
            yield scrapy.Request(next_page_url, callback=self.parse_job_offer)

    def parse_detail(self, response):
        item = HelloWorkItem()
        table_selectors = response.css('table.mytable-new > tr')

        # 会社名や雇用形態、事業者番号は非公開の場合があり、それらのデータがない item もあります。
        for table_selector in table_selectors:
            th_content = table_selector.css('th ::text').get()
            td_content = table_selector.css('td ::text').get()
            company_name_content = table_selector.css('td > div.ruby-pt > ruby > rb ::text').get()
            if "会社名" in th_content:
                company_name = company_name_content.replace('\u3000', '')
                item['company_name'] = company_name
            if "雇用形態" in th_content:
                employment_status = td_content.replace(' ', '')
                item['employment_status'] = employment_status
            if "事業所番号" in th_content:
                business_number = td_content
                item['business_number'] = business_number
        yield item