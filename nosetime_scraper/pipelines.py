# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from bs4 import BeautifulSoup
import re
import pymongo


class NosetimeScraperPipeline:

    def __init__(self):
        pass

    def process_item(self, item, spider):
        return item

    def process_response(self, response):
        perfume = {}
        response_body = response.body.decode('utf-8')
        soup = BeautifulSoup(response_body, "html.parser")

        # photo
        try:
            perfume['img'] = soup.find('img', {'class': "noxx"})['src']
        except:
            pass
        # id
        try:
            perfume['id'] = perfume['img'].split("/")[-1].split("-")[0].split(".")[0]
        except:
            pass
        # names
        try:
            names = soup.find('h1').text
            names = re.split(r'\s*((?!\s)[\W\d_]*[A-Za-z].*?[A-Za-z][\W\d_]*?)\s*(?=(?![a-zA-Z])[^\W\d_]|$)', names)
            perfume['enname'] = names[1]
            perfume['cnname'] = names[0]
            if perfume['enname'].startswith('('):
                return None
        except:
            pass
        # item_info
        try:
            item_info = soup.find('ul', {'class': "item_info"})
            item_soup = BeautifulSoup(str(item_info), "html.parser")
            items = item_soup.text.split('  ')
            for e in items:
                e = e.replace('[', '')
                e = e.replace(']', '')
                e = e.replace(' ', '')
                e = e.split('：')
                perfume[e[0]] = e[1]

            translated_keys = {"品牌":"brand", "香调": "fragrance", "前调":"top",
                    "中调":"middle", "后调":"base", "属性":"attribut",
                    "标签": "tag"}
            perfume_copy = perfume.copy()
            for k,v in perfume.items():
                try:
                    perfume_copy[translated_keys[k]]= v
                except KeyError:
                    pass

            for k in translated_keys.keys():
                try:
                    perfume_copy.pop(k)
                except KeyError:
                    pass
            perfume = perfume_copy.copy()
        except:
            pass

        try:
            perfume['isscore'] = soup.find('div', {'class': "score"}).text
            perfume['istotal'] = soup.find('span', {'class': "people"}).text
        except:
            pass

        try:
            stars = soup.find_all('span', {'class': 'starnum'})
            d = {}
            for star in stars:
                d[star.text] = star.find_next("div").text
            perfume['stars'] = d

            perfume['intro'] = soup.find('div', {'class': 'showmore'}).text
        except:
            pass

        try:
            # short comments
            perfume["short_comments"] = []
            for pseudo_rate, comment in zip(soup.find_all('div', {'class': "author"}),
                                            soup.find_all('div', {'class': "hfshow1"})):
                d = {"name": pseudo_rate.text, "comment": comment.text}
                perfume["short_comments"].append(d)
        except:
            pass

        #long_comments
        perfume["long_comments"] = []
        long_comment_html = soup.find('li', {'id': 'itemdiscuss'})
        try:
            for pseudo_rate, comment, time, fav_cnt in zip(long_comment_html.find_all('div', {'class': "comment"}),
                                                           long_comment_html.find_all('div', {'class': "hfshow"}),
                                                           long_comment_html.find_all('span',
                                                                                      {'class': "publish-time"}),
                                                           long_comment_html.find_all('span', {'class': "fav_cnt"})):
                d = {}
                d["name"] = pseudo_rate.text
                d["comment"] = comment.text
                d["publish-time"] = time.text
                try:
                    d["fav_cnt"] = fav_cnt.text
                except:
                    pass
                try:
                    d["rating"] = pseudo_rate.span["class"][1]
                except:
                    pass
                perfume["long_comments"].append(d)
        except:
            pass

        try:
            l = []
            likebys = soup.find_all('div', {'class': "title"})
            for likeby in likebys:
                l.append(likeby.find('a')['href'].split("/")[-1].split("-")[0])
            perfume["likebys_id"] = l
        except:
            pass
        return perfume

    def datsave_in_mongo(self, perfume):
        client = pymongo.MongoClient(
            "mongodb+srv://USER:PASSWORD@cluster0.n2hnd.mongodb.net/fragrance_db?retryWrites=true&w=majority")
        db = client.test
        fragrance = db.fragrance_db2
        fragrance.insert_one(perfume)