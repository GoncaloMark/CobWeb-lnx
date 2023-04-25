import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import yaml
from os import path
import itertools

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
        #IF 403 FORBIDDEN MAKE ERROR EXCEPTION!

        for link_tag in soup.find_all("a")[0:self.hops]: #Find all <a/> html tags and get their href attribute
            href = link_tag.attrs.get("href") 

            if href == "" or href == None: #If there's no href return control to the beginning of loop
                continue

            href = urljoin(self._url, href) #Join in case of relative paths!

            parse_href = urlparse(href) #Get the parts of the URL

            href = parse_href.scheme + "://" + parse_href.netloc + parse_href.path

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

    def __str__(self):
        return f"Spider Object with URL: {self._url} and Hops: {self.hops}"
    
    def __repr__(self):
        return f"Spider(url={self._url}, max_hops={self.hops})"
        

class Scraper(Spider):

    def __init__(self, config):
        super().__init__(config["url"], config["hops"])

        self.__config = config
        self.getLinks()
        self.__links = self.showLinks()
        self.__cache = {}

        self._parsed = list(self.__get_html())
        #self.__results = set()

    def __get_html(self):
        for link in self.__links:
            if link not in self.__cache:
                page = requests.get(link)
                soup = BeautifulSoup(page.content, "html.parser")
                self.__cache[link] = soup

            yield self.__cache[link]

    def __scrapeByElem(self):
        if len(self.__config["tags"]) == 0:
            return
        
        for soup, tag in itertools.product(self._parsed, self.__config["tags"]):
            result = soup.find_all(tag)
            for el in result:
                yield el

    def __scrapeBySelector(self):
        if len(self.__config["selectors"]) == 0:
            return
        result = []
        for soup, selector in itertools.product(self._parsed, self.__config["selectors"]):
            if selector == "id":
                for value in self.__config["IDvalue"]:
                    result.append(soup.select("#"+value))
            result.append(soup.select(selector))
            for el in result:
                yield el

    def __scrapeByClassName(self):
        if len(self.__config["classes"]) == 0:
            return
        
        for soup, tag, clsName in itertools.product(self._parsed, self.__config["tags"], self.__config["classes"]):
            result = soup.find_all(tag, class_=str(clsName))

            for el in result:
                yield el

    def __scrapeByAttr(self):
        if len(self.__config["attributes"]) == 0:
            return

        for soup, tag, attrName, value in itertools.product(self._parsed, self.__config["tags"], self.__config["attributes"], self.__config["attrV"]):
            result = soup.find_all(tag, attrs={attrName:value})

            for el in result:
                yield el

    def scrape(self):
        scrape_list = [[x for x in self.__scrapeByElem()], [x for x in self.__scrapeByAttr()], [x for x in self.__scrapeByClassName()], [x for x in self.__scrapeBySelector()]]
        print(f"""
        By Element: {scrape_list[0]},
        By Attribute: {scrape_list[1]},
        By Class: {scrape_list[2]},
        By Selector: {scrape_list[3]}
        """)

    def __str__(self):
        return f"Scraper Object with URL: {self._url} and Hops: {self.hops} and Config:{self.__config}"
    
    def __repr__(self):
        return f"Scraper(url={self._url}, max_hops={self.hops}, config={self.__config})"
    
def config_parser(config_file):
        try:
            with open(config_file, 'r') as stream:
                data = yaml.safe_load(stream)
                stream.close()
                return data
        except yaml.YAMLError as e:
            raise e

if __name__ == "__main__":
    
    #SCRAPER TEST! 
    print("Specify config file (YAML) Path!")
    config_path = input()
    if path.exists(config_path) != True:
        raise ValueError

    config = config_parser(config_file=config_path)
    scrape = Scraper(config=config)
    scrape.getLinks()
    #print(scrape.showLinks())
    scrape.scrape()
        

    
        
        

    """ 
    SPIDER TEST!
    crawl = Spider("url", 10)
    crawl.getLinks()
    print(crawl.showLinks()) """