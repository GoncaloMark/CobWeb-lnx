import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import pathlib
import yaml

#self.__config = self.__config_parser(config_file=config_file)
#, config_file

class Spider:
    def __init__(self, url, max_hops = 10):
        #Spider initializes instance with an url and a config, the config for the spider will only tell if you want internal links, external links or both!

        self.hops = int(max_hops)
        self._url = url
        
        #These are instance sets because every link will be unique, internal links link to another inside page, external links link to another different website!
        self._internal_urls = set()
        self._external_urls = set()

        isValid = self.__validateURL(self._url)
        if isValid is False:
            raise ValueError

    def __validateURL(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def getLinks(self):
        page = requests.get(self._url)
        domain_name = urlparse(self._url).netloc
        soup = BeautifulSoup(page.content, "html.parser")

        for link_tag in soup.find_all("a")[0:self.hops]: #Find all <a/> html tags and get their href attribute
            href = link_tag.attrs.get("href") 

            if href == "" or href == None: #If there's no href return control to the beginning 
                continue

            href = urljoin(self._url, href) #Join in case of relative paths!

            parse_href = urlparse(href) #Get the parts of the URL

            href = parse_href.scheme + "://" + parse_href.netloc + parse_href.path #Even if it was an absolute path and we accidentally joined it above this ensures all we get is an URL of this type!

            if not self.__validateURL(href):
                continue #If it's invalid return control to the beginning 

            if domain_name not in href: #Here we check if it's external link first, if it's not we can check if it's already in internal links and add it!
                if href not in self._external_urls:
                    self._external_urls.add(href)
                continue
            elif href not in self._internal_urls:
                self._internal_urls.add(href)
                continue

    def showLinks(self):
        if self._internal_urls and self._external_urls:
            return (self._internal_urls, self._external_urls)
        elif self._internal_urls:
            return self._internal_urls
        elif self._external_urls:
            return self._external_urls


class Scraper(Spider):

    def __init__(self, url, max_hops, config):
        super().__init__(url, max_hops)

        self.__config = self.__config_parser(config)
        self.__links = self.getLinks()

    def scrape(self):
        pass

    def __config_parser(self, config_file):
        file_extension = pathlib.Path('config_file').suffix

        if file_extension == "yml" or file_extension == "yaml":
            config = self.__parse_yaml(config_file=config_file)
            return config
        else:
            raise ValueError

    def __parse_yaml(self, config_file):
        
        try:
            with open(config_file, 'r') as stream:
                data = yaml.safe_load(stream)
                return data
        except yaml.YAMLError as e:
            raise e


if __name__ == "__main__":
    website_url = ""
    Crawl = Spider(url=website_url)
    Crawl.getLinks()
    print(Crawl.showLinks())
    