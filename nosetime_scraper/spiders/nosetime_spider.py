import scrapy
from ..pipelines import NosetimeScraperPipeline
import time

headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; TencentTraveler 4.0; Trident/4.0; SLCC1; Media Center PC 5.0; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30618)'}
base_url = 'https://www.nosetime.com'

class NosetimeScraper(scrapy.Spider):
    name = "nosetime"

    # urls = ['/pinpai/4-c.html']
    # urls = ['/pinpai/2-a.html', '/pinpai/3-b.html','/pinpai/4-c.html',
    #        '/pinpai/5-d.html','/pinpai/6-e.html','/pinpai/7-f.html',
    #        '/pinpai/8-g.html','/pinpai/9-h.html','/pinpai/10-i.html',
    #        '/pinpai/11-j.html','/pinpai/12-k.html','/pinpai/13-i.html',
    #        '/pinpai/14-m.html','/pinpai/15-n.html','/pinpai/16-o.html',
    #        '/pinpai/17-p.html','/pinpai/18-q.html','/pinpai/19-r.html',
    #        '/pinpai/20-s.html','/pinpai/21-t.html','/pinpai/22-u.html',
    #        '/pinpai/23-v.html','/pinpai/24-w.html','/pinpai/25-x.html',
    #        '/pinpai/26-y.html','/pinpai/27-z.html']
    # urls = ['/pinpai/10036120-yuguoboshi-hugo-boss.html',
    #         '/pinpai/10094164-kedi-coty.html',
    #         '/pinpai/10021965-gaotiye-jean-paul-gaultier.html',
    #         '/pinpai/10088596-laerfu-laolun-ralph-lauren.html']

    def __init__(self, urls=None, database=None, *args, **kwargs):
        super(NosetimeScraper, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.nosetime.com' + url for url in urls]

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