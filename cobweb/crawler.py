import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

class Spider:
    def __init__(self, url, config):
        #Spider initializes instance with an url and a config, the config for the spider will only tell if you want internal links, external links or both!

        self.__url = url
        self.__config = config

        #These are instance sets because every link will be unique, internal links link to another inside page, external links link to another different website!
        internal_urls = set()
        external_urls = set()

        isValid = self.__validateURL()
        if isValid is False:
            raise ValueError

    def __del__(self):
        print(f"Invalid URL {self.__url}")


    def __validateURL(self):
        parsed = urlparse(self.__url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def getLinks(self):
        pass

