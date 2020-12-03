import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import json
import requests
from urllib.parse import parse_qsl, urlencode
import re
from ..pipelines import Pipeline


class SephoraSpider(scrapy.Spider):
    name = 'sephora'
    allowed_domains = ['sephora.fr']
    # start_urls = ['https://www.sephora.fr/marques-de-a-a-z/']
    start_urls = ['https://www.sephora.fr/marques/de-a-a-z/burberry-burb/']

    def __init__(self):
        self.base_url = 'https://www.sephora.fr'
        self.url_api = "https://api.bazaarvoice.com/data/batch.json?"
        self.payload = "passkey=iohrnzjadededr160osgfvimy&apiversion=5.5&displaycode=3232-fr_fr&resource.q0=products" \
                       "&filter.q0=id%3Aeq%3AP618001&stats.q0=questions%2Creviews" \
                       "&filteredstats.q0=questions%2Creviews" \
                       "&filter_questions.q0=contentlocale%3Aeq%3Afr_FR&filter_answers.q0=contentlocale%3Aeq%3Afr_FR" \
                       "&filter_reviews.q0=contentlocale%3Aeq%3Afr_FR" \
                       "&filter_reviewcomments.q0=contentlocale%3Aeq%3Afr_FR&resource.q1=questions" \
                       "&filter.q1=productid%3Aeq%3AP618001&filter.q1=contentlocale%3Aeq%3Afr_FR" \
                       "&sort.q1=lastapprovedanswersubmissiontime%3Adesc&stats.q1=questions" \
                       "&filteredstats.q1=questions&include.q1=authors%2Cproducts%2Canswers" \
                       "&filter_questions.q1=contentlocale%3Aeq%3Afr_FR&filter_answers.q1=contentlocale%3Aeq%3Afr_FR" \
                       "&limit.q1=20&offset.q1=0&limit_answers.q1=20&resource.q2=reviews" \
                       "&filter.q2=isratingsonly%3Aeq%3Afalse&filter.q2=productid%3Aeq%3AP618001" \
                       "&filter.q2=contentlocale%3Aeq%3Afr_FR&sort.q2=submissiontime%3Adesc" \
                       "&stats.q2=reviews&filteredstats.q2=reviews&include.q2=authors%2Cproducts%2Ccomments" \
                       "&filter_reviews.q2=contentlocale%3Aeq%3Afr_FR" \
                       "&filter_reviewcomments.q2=contentlocale%3Aeq%3Afr_FR" \
                       "&filter_comments.q2=contentlocale%3Aeq%3Afr_FR&limit.q2=5&offset.q2=0&limit_comments.q2=20" \
                       "&callback=BV._internal.dataHandler0"
        self.db_url = "mongodb+srv://test:MongoDB.2020@cluster0.n2hnd.mongodb.net/fragrance_db?retryWrites=true" \
                      "&w=majority"

    def parse(self, response):
        if response.url == "https://www.sephora.fr/marques/de-a-a-z/burberry-burb/":
            yield scrapy.Request(url=response.url, callback=self.parse_brand)
        else:
            self.log("parse: I just visited: " + response.url)
            urls = response.css('a.sub-category-link::attr(href)').extract()
            if urls:
                for url in urls:
                    yield scrapy.Request(url=self.base_url + url, callback=self.parse_brand)

    def parse_brand(self, response):
        # self.log("parse_brand: I just visited: "+ response.url)
        for d in response.css('div.search-result-content div.product-tile::attr(data-tcproduct)').extract():
            d = json.loads(d)
            yield scrapy.Request(url=d['product_url_page'].replace("p", "P"), callback=self.parse_item)

    def parse_item(self, response):
        self.log("parse: I just visited: " + response.url)
        links = response.css('link').extract()
        product_id = re.findall(r'P[0-9]*', [x for x in links if 'sephora.fr' in x][0])[0]
        decoded = parse_qsl(self.payload)
        decoded.pop(4)
        decoded.pop(12)
        decoded.pop(25)
        decoded.insert(4, ('filter.q0', 'id:eq:' + product_id))
        decoded.insert(12, ('filter.q0', 'id:eq:' + product_id))
        decoded.insert(25, ('filter.q0', 'id:eq:' + product_id))
        response = requests.get(f"{self.url_api}{urlencode(decoded)}").text

        data = json.loads(re.search(r"\((.*)\)", response).group(1))
        if data["BatchedResults"]["q0"]["Results"][0]["Brand"]['Name'] == 'BURBERRY':
            print("we are going to save: ", data["BatchedResults"]["q0"]["Results"][0]["Brand"]['Name'])
            pipeline = Pipeline()
            # perfume = pipeline.process_response(response)
            pipeline.save_in_mongo(self.db_url, 'ifresearch', 'sephora', data["BatchedResults"])

            # return data["BatchedResults"]
            return data["BatchedResults"]["q0"]["Results"][0]["Brand"]
        else:
            print("we are not going to save: ", data["BatchedResults"]["q0"]["Results"][0]["Brand"])
            return None