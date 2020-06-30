import scrapy
import logging

from scrapy.loader import ItemLoader
from scrapy.http import FormRequest
from scrapy.exceptions import CloseSpider
from datetime import datetime

from fbposts.items import FbPostItem, parse_date


class FacebookSpider(scrapy.Spider):
    """
    Parse FB pages (needs credentials)
    """

    name = "fb"

    def __init__(self, *args, **kwargs):
        # turn off annoying logging, set LOG_LEVEL=DEBUG in settings.py to see more logs
        logger = logging.getLogger("scrapy.middleware")
        logger.setLevel(logging.WARNING)

        super().__init__(*args, **kwargs)

        # email & pass need to be passed as attributes!
        if "email" not in kwargs or "password" not in kwargs:
            raise AttributeError(
                "You need to provide valid email and password:\n"
                'scrapy fb -a email="EMAIL" -a password="PASSWORD"'
            )
        else:
            self.logger.info("Email and password provided, will be used to log in")

        # page name parsing (added support for full urls)
        if "page" in kwargs:
            if self.page.find("/groups/") != -1:
                self.group = 1
            else:
                self.group = 0
            if self.page.find("https://www.facebook.com/") != -1:
                self.page = self.page[25:]
            elif self.page.find("https://mbasic.facebook.com/") != -1:
                self.page = self.page[28:]
            elif self.page.find("https://m.facebook.com/") != -1:
                self.page = self.page[23:]

        # parse date
        if "date" not in kwargs:
            self.date = datetime.today()
            self.logger.info(
                f"Date attribute not provided, scraping date set to {self.date.strftime('%Y-%M-%D')} (fb launch date)"
            )
        else:
            self.date = datetime.strptime(kwargs["date"], "%Y-%m-%d")
            self.logger.info(
                "Date attribute provided, fbcrawl will start crawling at {}".format(
                    kwargs["date"]
                )
            )
        self.year = self.date.year

        # parse lang, if not provided (but is supported) it will be guessed in parse_home
        self.lang = "pt"

        # max num of posts to crawl
        if "max" not in kwargs:
            self.max = int(10e5)
        else:
            self.max = int(kwargs["max"])

        # current year, this variable is needed for proper parse_page recursion
        self.k = datetime.now().year
        # count number of posts, used to enforce DFS and insert posts orderly in the csv
        self.count = 0

        self.start_urls = ["https://mbasic.facebook.com"]

    def parse(self, response):
        """
        Handle login with provided credentials
        """
        return FormRequest.from_response(
            response,
            formxpath='//form[contains(@action, "login")]',
            formdata={"email": self.email, "pass": self.password},
            callback=self.parse_home,
        )

    def parse_home(self, response):
        """
        This method has multiple purposes:
        1) Handle failed logins due to facebook 'save-device' redirection
        2) Set language interface, if not already provided
        3) Navigate to given page 
        """
        # handle 'save-device' redirection
        if response.xpath("//div/a[contains(@href,'save-device')]"):
            self.logger.info('Going through the "save-device" checkpoint')
            return FormRequest.from_response(
                response,
                formdata={"name_action_selected": "dont_save"},
                callback=self.parse_home,
            )

        # navigate to provided page
        href = response.urljoin(self.page)
        self.logger.info("Scraping facebook page {}".format(href))
        return scrapy.Request(url=href, callback=self.parse_page, meta={"index": 1})

    def parse_page(self, response):
        """
        Parse the given page selecting the posts.
        Then ask recursively for another page.
        """
        #open page in browser for debug
        # from scrapy.utils.response import open_in_browser
        # open_in_browser(response)

        # select all posts
        for post in response.xpath("//article[contains(@data-ft,'top_level_post_id')]"):

            many_features = post.xpath("./@data-ft").get()
            post_date = parse_date([many_features], {"lang": self.lang})
            post_date = (
                datetime.strptime(post_date, "%Y-%m-%d %H:%M:%S")
                if post_date is not None
                else post_date
            )

            if post_date is None:
                post_date = datetime(self.date.year, self.date.month, 1)

            # if 'date' argument is reached stop crawling
            if post_date < self.date:
                raise CloseSpider(
                    "Reached date: {} - post_date: {}".format(self.date, post_date)
                )

            new = ItemLoader(item=FbPostItem(), selector=post)
            if abs(self.count) + 1 > self.max:
                raise CloseSpider(
                    "Reached max num of post: {}. Crawling finished".format(
                        abs(self.count)
                    )
                )
            self.logger.info(
                "Parsing post n = {}, post_date = {}".format(
                    abs(self.count) + 1, post_date
                )
            )
            new.add_value("date", post_date)
            new.add_xpath('post_id','./@data-ft')
            new.add_xpath('url', ".//a[contains(@href,'footer')]/@href")

            # returns full post-link in a list
            post = post.xpath(".//a[contains(@href,'footer')]/@href").extract()
            temp_post = response.urljoin(post[0])
            self.count -= 1
            yield scrapy.Request(
                temp_post, self.parse_post, priority=self.count, meta={"item": new}
            )

        # load following page, try to click on "more"
        # after few pages have been scraped, the "more" link might disappears
        # if not present look for the highest year not parsed yet
        # click once on the year and go back to clicking "more"

        # new_page is different for groups
        if self.group == 1:
            new_page = response.xpath(
                "//div[contains(@id,'stories_container')]/div[2]/a/@href"
            ).extract()
        else:
            new_page = response.xpath(
                "//div[2]/a[contains(@href,'timestart=') and not(contains(text(),'ent')) and not(contains(text(),number()))]/@href"
            ).extract()
            # this is why lang is needed                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^

        if not new_page:
            self.logger.info('[!] "more" link not found, will look for a "year" link')
            # self.k is the year link that we look for
            if response.meta["flag"] == self.k and self.k >= self.year:
                xpath = (
                    "//div/a[contains(@href,'time') and contains(text(),'"
                    + str(self.k)
                    + "')]/@href"
                )
                new_page = response.xpath(xpath).extract()
                if new_page:
                    new_page = response.urljoin(new_page[0])
                    self.k -= 1
                    self.logger.info(
                        'Found a link for year "{}", new_page = {}'.format(
                            self.k, new_page
                        )
                    )
                    yield scrapy.Request(
                        new_page, callback=self.parse_page, meta={"flag": self.k}
                    )
                else:
                    while (
                        not new_page
                    ):  # sometimes the years are skipped this handles small year gaps
                        self.logger.info(
                            "Link not found for year {}, trying with previous year {}".format(
                                self.k, self.k - 1
                            )
                        )
                        self.k -= 1
                        if self.k < self.year:
                            raise CloseSpider(
                                "Reached date: {}. Crawling finished".format(self.date)
                            )
                        xpath = (
                            "//div/a[contains(@href,'time') and contains(text(),'"
                            + str(self.k)
                            + "')]/@href"
                        )
                        new_page = response.xpath(xpath).extract()
                    self.logger.info(
                        'Found a link for year "{}", new_page = {}'.format(
                            self.k, new_page
                        )
                    )
                    new_page = response.urljoin(new_page[0])
                    self.k -= 1
                    yield scrapy.Request(
                        new_page, callback=self.parse_page, meta={"flag": self.k}
                    )
            else:
                self.logger.info("Crawling has finished with no errors!")
        else:
            new_page = response.urljoin(new_page[0])
            if "flag" in response.meta:
                self.logger.info(
                    'Page scraped, clicking on "more"! new_page = {}'.format(new_page)
                )
                yield scrapy.Request(
                    new_page,
                    callback=self.parse_page,
                    meta={"flag": response.meta["flag"]},
                )
            else:
                self.logger.info(
                    'First page scraped, clicking on "more"! new_page = {}'.format(
                        new_page
                    )
                )
                yield scrapy.Request(
                    new_page, callback=self.parse_page, meta={"flag": self.k}
                )

    def parse_post(self, response):
        new = ItemLoader(
            item=FbPostItem(), response=response, parent=response.meta["item"]
        )
        new.context["lang"] = self.lang
        new.add_xpath(
            "source",
            "//td/div/h3/strong/a/text() | //span/strong/a/text() | //div/div/div/a[contains(@href,'post_id')]/strong/text()",
        )
        new.add_xpath("image", "//a/img[contains(@src,'content')]/@src")
        new.add_xpath(
            "text",
            "//div[@data-ft]//p//text() | //div[@data-ft]/div[@class]/div[@class]/text()",
        )
        yield new.load_item()
