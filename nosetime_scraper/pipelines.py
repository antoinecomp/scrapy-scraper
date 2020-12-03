# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
from bs4 import BeautifulSoup
import re
import pymongo
import requests

base_url = 'https://www.nosetime.com'


class Pipeline:

    def __init__(self):
        pass

    def process_item(self, item, spider):
        return item

    def process_url(self, url, headers):
        product_id = url.split("/")[-1].split("-")[0]
        json_doc = requests.get(
            f"https://www.nosetime.com/app/item.php?id={product_id}",
            headers=headers,
        ).json()

        perfume = {}
        try:
            perfume["id"] = json_doc["id"]
        except KeyError:
            return None
        try:
            perfume["item_name_en"] = json_doc["enname"]
        except KeyError:
            pass
        try:
            perfume["item_name_cn"] = json_doc["cnname"]
        except KeyError:
            pass
        try:
            perfume["item_info"] = json_doc["intro"]
        except KeyError:
            pass
        try:
            perfume["item_score"] = json_doc["isscore"]
        except KeyError:
            pass
        try:
            perfume["number_reviews"] = json_doc["istotal"]
        except KeyError:
            pass
        try:
            perfume["brand"] = json_doc["brand"]
        except KeyError:
            pass
        try:
            perfume["attrib"] = json_doc["attrib"]
        except KeyError:
            pass
        try:
            perfume["top"] = json_doc["top"]
        except KeyError:
            pass
        try:
            perfume["middle"] = json_doc["middle"]
        except KeyError:
            pass
        try:
            perfume['base'] = json_doc["base"]
        except KeyError:
            pass
        try:
            perfume["mainodor"] = json_doc["mainodor"]
        except KeyError:
            pass
        try:
            perfume["perfumer"] = json_doc["perfumer"]
        except KeyError:
            pass

        response_unicode = requests.get(base_url + url, headers=headers)
        soup = BeautifulSoup(response_unicode.text, 'html.parser')

        try:
            perfume["number_five"] = soup.find_all('div', {'class': 'nows'})[0].text
        except IndexError:
            pass
        try:
            perfume["number_four"] = soup.find_all('div', {'class': 'nows'})[1].text
        except IndexError:
            pass
        try:
            perfume["number_three"] = soup.find_all('div', {'class': 'nows'})[2].text
        except IndexError:
            pass
        try:
            perfume["number_two"] = soup.find_all('div', {'class': 'nows'})[3].text
        except IndexError:
            pass
        try:
            perfume["number_one"] = soup.find_all('div', {'class': 'nows'})[4].text
        except IndexError:
            pass

        perfume["short_comment"] = []
        for pseudo_rate, comment in zip(soup.find_all('div', {'class': "author"}),
                                        soup.find_all('div', {'class': "hfshow1"})):
            d = {}
            d["name"] = pseudo_rate.text
            d["comment"] = comment.text
            try:
                d["rating"] = pseudo_rate.span["class"][1]
            except:
                pass
            perfume["short_comment"].append(d)

        perfume["long_comment"] = []
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
                perfume["long_comment"].append(d)
        except:
            pass

        try:
            perfume["img_src"] = soup.find('img', {'class': 'noxx'})["src"]
        except:
            pass
            # perfume["url_image"]=soup.find('img',{'class':'noxx'})

        return perfume

    def process_response_respectfully(self, response):
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

    def save_in_mongo(self, url, db, collection, perfume):
        client = pymongo.MongoClient(url)
        db = client[db]
        collection = db[collection]
        collection.insert_one(perfume)