import scrapy
from ..pipelines import NosetimeScraperPipeline
import time

headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; TencentTraveler 4.0; Trident/4.0; SLCC1; Media Center PC 5.0; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30618)'}
base_url = 'https://www.nosetime.com'

class NosetimeScraper(scrapy.Spider):
    name = "nosetime"

    # urls = ['/pinpai/4-c.html']


    def __init__(self, url=None, database=None, *args, **kwargs):
        super(NosetimeScraper, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.nosetime.com' + url]

    def parse(self, response):
        # proceed to other pages of the listings
        urls = response.css('a.imgborder::attr(href)').getall()
        for url in urls:
            print("url: ", url)
            yield scrapy.Request(url=base_url + url, callback=self.parse)

        # now that we have the urls we need to know if the dire are the things we can scrape
        pipeline = NosetimeScraperPipeline()
        perfume = pipeline.process_response(response)
        try:
            if perfume['enname']:
                print("Finally are going to store: ", perfume['enname'])
                pipeline.save_in_mongo(perfume)
        except KeyError:
            pass