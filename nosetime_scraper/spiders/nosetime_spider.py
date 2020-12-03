# import scrapy
# from ..pipelines import Pipeline
# import time
#
# headers = {'User-Agent':'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; TencentTraveler 4.0; Trident/4.0; SLCC1; Media Center PC 5.0; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30618)'}
# base_url = 'https://www.nosetime.com'
#
# class NosetimeScraper(scrapy.Spider):
#     name = "nosetime"
#
#     # urls = ['/pinpai/4-c.html']
#
#     def __init__(self, url=None, urls=None, database=None, *args, **kwargs):
#         urls = ['/pinpai/10036120-yuguoboshi-hugo-boss.html',
#                 '/pinpai/10094164-kedi-coty.html',
#                 '/pinpai/10021965-gaotiye-jean-paul-gaultier.html',
#                 '/pinpai/10088596-laerfu-laolun-ralph-lauren.html']
#         super(NosetimeScraper, self).__init__(*args, **kwargs)
#         if url:
#             self.start_urls = ['https://www.nosetime.com' + url for url in urls]
#         elif urls:
#             self.start_urls = ['https://www.nosetime.com' + url for url in urls]
#         self.db_url = "mongodb+srv://test:MongoDB.2020@cluster0.n2hnd.mongodb.net/fragrance_db?retryWrites=true" \
#                       "&w=majority"
#
#     def parse(self, response):
#         # proceed to other pages of the listings
#         urls = response.css('a.imgborder::attr(href)').getall()
#         for url in urls:
#             print("url: ", url)
#             # now that we have the urls we need to know if the dire are the things we can scrape
#             pipeline = Pipeline()
#             # perfume = pipeline.process_response(response)
#             perfume = pipeline.process_url(url, headers)
#             print(perfume['item_name_en'])
#             try:
#                 if perfume['item_name_en']:
#                     print("Finally are going to store: ", perfume['item_name_en'])
#                     pipeline.save_in_mongo(perfume, self.db_url, 'if_reasearch', 'fragrance')
#             except KeyError:
#                 pass
#             yield scrapy.Request(url=base_url + url, callback=self.parse)
#
