# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import json
import scrapy
from scrapy.loader.processors import TakeFirst, Join, MapCompose
from datetime import datetime, timedelta


def url_strip(url):
    fullurl = url[0]
    # catchin '&id=' is enough to identify the post
    i = fullurl.find("&id=")
    if i != -1:
        return fullurl[: i + 4] + fullurl[i + 4 :].split("&")[0]
    else:  # catch photos
        i = fullurl.find("/photos/")
        if i != -1:
            return fullurl[: i + 8] + fullurl[i + 8 :].split("/?")[0]
        else:  # catch albums
            i = fullurl.find("/albums/")
            if i != -1:
                return fullurl[: i + 8] + fullurl[i + 8 :].split("/?")[0]
            else:
                return fullurl


def parse_date(date, loader_context):
    d = json.loads(date[0])  # nested dict of features
    flat_d = dict()  # only retain 'leaves' of d tree

    def recursive_items(dictionary):
        """
        Get most nested key:value pair of nested dict
        """
        for key, value in dictionary.items():
            if type(value) is dict:
                yield from recursive_items(value)
            else:
                yield (key, value)

    for key, value in recursive_items(d):
        flat_d[key] = value

    # returns timestamp in localtime conversion from linux timestamp UTC
    ret = (
        str(datetime.fromtimestamp(flat_d["publish_time"]))
        if "publish_time" in flat_d
        else None
    )
    return ret


def id_strip(post_id):
    d = json.loads(post_id[::-1][0])  # nested dict of features
    return str(d["top_level_post_id"])


def image_strip(images):
    return [image for image in images if not "https://static.xx.fbcdn.net" in image]


class FbPostItem(scrapy.Item):
    source = scrapy.Field()
    date = scrapy.Field()
    text = scrapy.Field(output_processor=Join(separator=u""))  # full text of the post
    image = scrapy.Field(output_processor=image_strip)

    url = scrapy.Field(output_processor=url_strip)
    post_id = scrapy.Field(output_processor=id_strip)
