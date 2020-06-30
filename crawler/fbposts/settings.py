# -*- coding: utf-8 -*-

# Scrapy settings for fbcrawl project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "fbposts"

SPIDER_MODULES = ["fbposts.spiders"]
NEWSPIDER_MODULE = "fbposts.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept-Language": "pt_BR",
}

DUPEFILTER_CLASS = "scrapy.dupefilters.BaseDupeFilter"

# specifies the order of the column to export as CSV
FEED_EXPORT_FIELDS = ["post_id", "source", "date", "text", "image", "url"]
URLLENGTH_LIMIT = 99999
FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"
