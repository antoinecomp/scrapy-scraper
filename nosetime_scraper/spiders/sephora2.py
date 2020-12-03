import scrapy


class Sephora2Spider(scrapy.Spider):
    name = 'sephora2'
    allowed_domains = ['sephora.com']
    start_urls = ['https://www.sephora.fr/marques-de-a-a-z/']

    def parse(self, response):
        self.log("parse: I just visited: " + response.url)
        urls = response.css('a.sub-category-link::attr(href)').extract()
        if urls:
            for url in urls:
                print(url)
                yield scrapy.Request(url=self.base_url + url, callback=self.parse_brand)
