import scrapy

from hello_work.items import HelloWorkItem


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

        for table_selector in table_selectors:
            th_content = table_selector.css('th ::text').get()
            td_content = table_selector.css('td ::text').get()
            company_name_content = table_selector.css('td > div.ruby-pt > ruby > rb ::text').get()
            if "会社名" in th_content:
                company_name = company_name_content.replace('\u3000', '')
                item['company_name'] = company_name
            if "代表者名" in th_content:
                representative = td_content.replace('\u3000', '')
                item['representative'] = representative
            if "設立" in th_content:
                year_of_establishment = td_content
                item['year_of_establishment'] = year_of_establishment
            if "会社所在地" in th_content:
                location = td_content.replace('\u3000', '')
                item['location'] = location
            if "事業所番号" in th_content:
                business_number = td_content
                item['business_number'] = business_number
        yield item
